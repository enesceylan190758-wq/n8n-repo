#!/usr/bin/env python3
"""Publish approved social posts to Instagram / LinkedIn.

Usage:
  python3 execution/social-publish-approved.py
  python3 execution/social-publish-approved.py --post-id <uuid>
  python3 execution/social-publish-approved.py --token <approval_token>
  python3 execution/social-publish-approved.py --dry-run
"""
from __future__ import annotations

import argparse
import json
import os
import smtplib
import ssl
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def sb(method: str, path: str, body: dict | None = None) -> list | dict:
    base = os.environ.get("SUPABASE_URL", "http://127.0.0.1:54321").rstrip("/")
    if "host.docker.internal" in base:
        base = "http://127.0.0.1:54321"
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
    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = resp.read().decode()
        return json.loads(raw) if raw.strip() else {}


def fetch_image_bytes(image_url: str) -> bytes:
    req = urllib.request.Request(image_url, headers={"User-Agent": "NefalixSocialBot/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def publish_instagram(post: dict) -> dict:
    token = os.environ.get("META_PAGE_ACCESS_TOKEN", "")
    ig_user_id = os.environ.get("INSTAGRAM_BUSINESS_ACCOUNT_ID", "")
    if not token or not ig_user_id:
        return {"ok": False, "skipped": True, "reason": "META_PAGE_ACCESS_TOKEN veya INSTAGRAM_BUSINESS_ACCOUNT_ID eksik"}
    image_url = post.get("image_url")
    if not image_url:
        return {"ok": False, "skipped": True, "reason": "image_url eksik — Storage upload gerekli"}
    caption = f"{post.get('caption', '')}\n\n{post.get('hashtags', '')}".strip()
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
    with urllib.request.urlopen(container_req, timeout=60) as resp:
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
    with urllib.request.urlopen(publish_req, timeout=60) as resp:
        result = json.loads(resp.read().decode())
    return {"ok": True, "instagram_post_id": result.get("id"), "raw": result}


def linkedin_register_upload(token: str, org_id: str) -> tuple[str, str]:
    body = {
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "owner": f"urn:li:organization:{org_id}",
            "serviceRelationships": [{
                "relationshipType": "OWNER",
                "identifier": "urn:li:userGeneratedContent",
            }],
        }
    }
    req = urllib.request.Request(
        "https://api.linkedin.com/v2/assets?action=registerUpload",
        data=json.dumps(body).encode(),
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode())
    value = data.get("value", {})
    upload_mechanism = value.get("uploadMechanism", {})
    http_req = upload_mechanism.get("com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest", {})
    upload_url = http_req.get("uploadUrl")
    asset = value.get("asset")
    if not upload_url or not asset:
        raise RuntimeError(f"LinkedIn registerUpload failed: {data}")
    return upload_url, asset


def linkedin_upload_binary(upload_url: str, token: str, image_bytes: bytes) -> None:
    req = urllib.request.Request(
        upload_url,
        data=image_bytes,
        method="PUT",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/octet-stream",
        },
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        if resp.status >= 300:
            raise RuntimeError(f"LinkedIn binary upload HTTP {resp.status}")


def publish_linkedin(post: dict) -> dict:
    token = os.environ.get("LINKEDIN_ACCESS_TOKEN", "")
    org_id = os.environ.get("LINKEDIN_ORGANIZATION_ID", "")
    if not token or not org_id:
        return {"ok": False, "skipped": True, "reason": "LINKEDIN_ACCESS_TOKEN veya LINKEDIN_ORGANIZATION_ID eksik"}

    text = f"{post.get('caption', '')}\n\n{post.get('hashtags', '')}".strip()
    image_url = post.get("image_url")

    if image_url:
        try:
            image_bytes = fetch_image_bytes(image_url)
            upload_url, asset = linkedin_register_upload(token, org_id)
            linkedin_upload_binary(upload_url, token, image_bytes)
            body = {
                "author": f"urn:li:organization:{org_id}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {"text": text},
                        "shareMediaCategory": "IMAGE",
                        "media": [{
                            "status": "READY",
                            "description": {"text": (post.get("headline") or "Nefalix")[:200]},
                            "media": asset,
                            "title": {"text": "Nefalix"},
                        }],
                    }
                },
                "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
            }
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "error": f"LinkedIn image upload: {exc}"}
    else:
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
    with urllib.request.urlopen(req, timeout=60) as resp:
        result = json.loads(resp.read().decode())
    return {"ok": True, "linkedin_post_id": result.get("id"), "raw": result}


def send_publish_email(post: dict, results: dict) -> None:
    to_raw = os.environ.get("SOCIAL_NOTIFY_TO", "enes.ceylan190758@gmail.com,akadirysr@gmail.com")
    to_addrs = [x.strip() for x in to_raw.split(",") if x.strip()]
    password = os.environ.get("BLOG_SMTP_PASSWORD", "")
    if not password:
        return

    ig = results.get("instagram") or {}
    li = results.get("linkedin") or {}
    status = results.get("status", "unknown")
    subject = f"Nefalix Sosyal — {'Yayınlandı' if status == 'published' else 'Yayın hatası'}"
    html = f"""<!DOCTYPE html><html><body style="font-family:system-ui,sans-serif;">
<p>Sosyal post durumu: <strong>{status}</strong></p>
<ul>
<li>Instagram: {ig.get('instagram_post_id') or ig.get('reason') or ig.get('error') or ig.get('skipped')}</li>
<li>LinkedIn: {li.get('linkedin_post_id') or li.get('reason') or li.get('error') or li.get('skipped')}</li>
</ul>
<p>Post ID: {post.get('id')}</p>
</body></html>"""

    host = os.environ.get("BLOG_SMTP_HOST", "smtp.hostinger.com")
    port = int(os.environ.get("BLOG_SMTP_PORT", "465"))
    user = os.environ.get("BLOG_SMTP_USER", "info@nefalix.com")
    from_addr = os.environ.get("BLOG_SMTP_FROM", user)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"Nefalix Sosyal <{from_addr}>"
    msg["To"] = ", ".join(to_addrs)
    msg.attach(MIMEText(html, "html", "utf-8"))
    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL(host, port, context=ctx) as smtp:
        smtp.login(user, password)
        smtp.sendmail(from_addr, to_addrs, msg.as_string())


def publish_one(post: dict, dry_run: bool = False) -> dict:
    if dry_run:
        return {"post_id": post["id"], "dry_run": True}

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
        publish_error = "API credential eksik — env ayarlayın"
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

    out = {
        "post_id": post["id"],
        "status": status,
        "instagram": ig_result,
        "linkedin": li_result,
    }
    try:
        send_publish_email(post, out)
    except Exception:  # noqa: BLE001
        pass
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--post-id")
    parser.add_argument("--token")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.token:
        posts = sb("GET", f"social_posts?approval_token=eq.{args.token}&limit=1")
    elif args.post_id:
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
        if post.get("status") not in ("approved", "scheduled") and not args.token and not args.post_id:
            continue
        results.append(publish_one(post, dry_run=args.dry_run))

    print(json.dumps({"ok": True, "results": results}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
