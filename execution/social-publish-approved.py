#!/usr/bin/env python3
"""Publish approved social posts to Instagram / LinkedIn (MVP stub + API when configured).

Usage:
  python3 execution/social-publish-approved.py
  python3 execution/social-publish-approved.py --post-id <uuid>
  python3 execution/social-publish-approved.py --dry-run
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone


def sb(method: str, path: str, body: dict | None = None) -> list | dict:
    base = os.environ.get("SUPABASE_URL", "http://127.0.0.1:54321").rstrip("/")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not key:
        raise SystemExit("SUPABASE_SERVICE_ROLE_KEY eksik")
    url = f"{base}/rest/v1/{path}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read().decode()
        return json.loads(raw) if raw.strip() else {}


def publish_instagram(post: dict) -> dict:
    token = os.environ.get("META_PAGE_ACCESS_TOKEN", "")
    ig_user_id = os.environ.get("INSTAGRAM_BUSINESS_ACCOUNT_ID", "")
    if not token or not ig_user_id:
        return {"ok": False, "skipped": True, "reason": "META_PAGE_ACCESS_TOKEN veya INSTAGRAM_BUSINESS_ACCOUNT_ID eksik"}
    image_url = post.get("image_url")
    if not image_url:
        return {"ok": False, "skipped": True, "reason": "image_url eksik — SOCIAL_PUBLIC_BASE_URL ayarla"}
    caption = f"{post.get('caption', '')}\n\n{post.get('hashtags', '')}".strip()
    # Container create
    container_body = urllib.parse.urlencode({
        "image_url": image_url,
        "caption": caption,
        "access_token": token,
    }).encode()
    container_req = urllib.request.Request(
        f"https://graph.facebook.com/v19.0/{ig_user_id}/media",
        data=container_body,
        method="POST",
    )
    with urllib.request.urlopen(container_req, timeout=30) as resp:
        container = json.loads(resp.read().decode())
    creation_id = container.get("id")
    if not creation_id:
        return {"ok": False, "error": container}
    publish_body = urllib.parse.urlencode({"creation_id": creation_id, "access_token": token}).encode()
    publish_req = urllib.request.Request(
        f"https://graph.facebook.com/v19.0/{ig_user_id}/media_publish",
        data=publish_body,
        method="POST",
    )
    with urllib.request.urlopen(publish_req, timeout=30) as resp:
        result = json.loads(resp.read().decode())
    return {"ok": True, "instagram_post_id": result.get("id"), "raw": result}


def publish_linkedin(post: dict) -> dict:
    token = os.environ.get("LINKEDIN_ACCESS_TOKEN", "")
    org_id = os.environ.get("LINKEDIN_ORGANIZATION_ID", "")
    if not token or not org_id:
        return {"ok": False, "skipped": True, "reason": "LINKEDIN_ACCESS_TOKEN veya LINKEDIN_ORGANIZATION_ID eksik"}
    # MVP: text-only share when image upload not configured
    text = f"{post.get('caption', '')}\n\n{post.get('hashtags', '')}".strip()
    body = {
        "author": f"urn:li:organization:{org_id}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": text},
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }
    req = urllib.request.Request(
        "https://api.linkedin.com/v2/ugcPosts",
        data=json.dumps(body).encode(),
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read().decode())
    return {"ok": True, "linkedin_post_id": result.get("id"), "raw": result}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--post-id")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.post_id:
        posts = sb("GET", f"social_posts?id=eq.{args.post_id}&limit=1")
    else:
        now = datetime.now(timezone.utc).isoformat()
        posts = sb(
            "GET",
            f"social_posts?status=in.(approved,scheduled)&or=(scheduled_at.is.null,scheduled_at.lte.{now})&order=scheduled_at.asc.nullsfirst&limit=5",
        )

    if not posts:
        print(json.dumps({"ok": True, "published": 0, "message": "Yayınlanacak post yok"}))
        return

    results = []
    for post in posts:
        if args.dry_run:
            results.append({"post_id": post["id"], "dry_run": True})
            continue
        platform = post.get("platform", "both")
        ig_result = li_result = None
        errors = []
        try:
            if platform in ("instagram", "both"):
                ig_result = publish_instagram(post)
                if not ig_result.get("ok") and not ig_result.get("skipped"):
                    errors.append(f"instagram: {ig_result}")
        except Exception as e:  # noqa: BLE001
            errors.append(f"instagram: {e}")
            ig_result = {"ok": False, "error": str(e)}
        try:
            if platform in ("linkedin", "both"):
                li_result = publish_linkedin(post)
                if not li_result.get("ok") and not li_result.get("skipped"):
                    errors.append(f"linkedin: {li_result}")
        except Exception as e:  # noqa: BLE001
            errors.append(f"linkedin: {e}")
            li_result = {"ok": False, "error": str(e)}

        both_skipped = (
            (ig_result or {}).get("skipped") and (li_result or {}).get("skipped")
        ) or (
            platform == "instagram" and (ig_result or {}).get("skipped")
        ) or (
            platform == "linkedin" and (li_result or {}).get("skipped")
        )

        if both_skipped:
            status = "approved"
            publish_error = "API credential eksik — manuel yayın veya env ayarla"
        elif errors:
            status = "failed"
            publish_error = "; ".join(errors)
        else:
            status = "published"
            publish_error = None

        patch = {
            "status": status,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "publish_error": publish_error,
        }
        if status == "published":
            patch["published_at"] = datetime.now(timezone.utc).isoformat()
        if ig_result and ig_result.get("instagram_post_id"):
            patch["instagram_post_id"] = ig_result["instagram_post_id"]
        if li_result and li_result.get("linkedin_post_id"):
            patch["linkedin_post_id"] = li_result["linkedin_post_id"]

        sb("PATCH", f"social_posts?id=eq.{post['id']}", patch)
        results.append({
            "post_id": post["id"],
            "status": status,
            "instagram": ig_result,
            "linkedin": li_result,
        })

    print(json.dumps({"ok": True, "results": results}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
