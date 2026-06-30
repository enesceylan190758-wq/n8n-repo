#!/usr/bin/env python3
"""Pick next social template, create queue row, render PNG, notify manager via WA gateway.

Usage:
  python3 execution/social-generate-next.py
  python3 execution/social-generate-next.py --slug post_02_nps_flow
  python3 execution/social-generate-next.py --post-number 3 --skip-render
  python3 execution/social-generate-next.py --dry-run
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


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
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Supabase error {e.code}: {e.read().decode()}") from e


def pick_template(slug: str | None, post_number: int | None) -> dict:
    if slug:
        rows = sb("GET", f"social_post_templates?slug=eq.{slug}&active=eq.true&limit=1")
    elif post_number:
        rows = sb("GET", f"social_post_templates?post_number=eq.{post_number}&active=eq.true&limit=1")
    else:
        rows = sb("GET", "social_post_templates?active=eq.true&order=post_number.asc")
        published = sb(
            "GET",
            "social_posts?status=eq.published&select=template_id,created_at&order=created_at.desc&limit=50",
        )
        recent_template_ids = {p.get("template_id") for p in published if p.get("template_id")}
        for row in rows:
            if row["id"] not in recent_template_ids:
                return row
        return rows[0] if rows else None
    if not rows:
        raise SystemExit("Aktif şablon bulunamadı")
    return rows[0]


def create_post(template: dict, platform: str) -> dict:
    caption = (template.get("caption_template") or "").strip()
    hashtags = (template.get("hashtags") or "").strip()
    rows = sb(
        "POST",
        "social_posts",
        {
            "template_id": template["id"],
            "status": "pending_approval",
            "platform": platform,
            "headline": template.get("headline_html", "").replace("<br/>", " ").replace("<em>", "").replace("</em>", ""),
            "caption": caption,
            "hashtags": hashtags,
            "metadata": {"slug": template["slug"], "post_number": template["post_number"]},
            "updated_at": datetime.now(timezone.utc).isoformat(),
        },
    )
    return rows[0]


def send_approval_wa(post: dict, template: dict) -> None:
    webhook_base = os.environ.get("N8N_WEBHOOK_URL", os.environ.get("WEBHOOK_URL", "http://127.0.0.1:5678/")).rstrip("/")
    manager = os.environ.get("CLINIC_MANAGER_WHATSAPP", "905491190819").replace("+", "").replace(" ", "")
    public_base = os.environ.get("N8N_PUBLIC_HOST", "api.nefalixai.com")
    token = post.get("approval_token", "")
    approve_url = f"https://{public_base}/webhook/nefalix/social/approve"
    caption_preview = (post.get("caption") or "")[:400]
    image_note = f"\n🖼 Görsel: {post.get('image_path')}" if post.get("image_path") else ""
    text = (
        f"📱 *Nefalix Sosyal Medya* — Onay bekliyor\n\n"
        f"Post {template.get('post_number')}/10: {template.get('slug')}\n"
        f"Platform: {post.get('platform', 'both')}\n\n"
        f"{caption_preview}\n\n"
        f"Onaylamak için webhook:\n"
        f"POST {approve_url}\n"
        f'{{"token":"{token}","action":"approve"}}\n\n'
        f"Reddet: action=reject"
        f"{image_note}"
    )
    payload = json.dumps({
        "number": manager,
        "text": text,
        "source": "social-approval",
        "priority": "normal",
    }).encode()
    req = urllib.request.Request(
        f"{webhook_base}/webhook/nefalix/whatsapp/send",
        data=payload,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20):
            pass
    except urllib.error.HTTPError as e:
        print(f"WA gateway uyarı ({e.code}): {e.read().decode()}", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--slug")
    parser.add_argument("--post-number", type=int)
    parser.add_argument("--platform", default=os.environ.get("SOCIAL_DEFAULT_PLATFORM", "both"))
    parser.add_argument("--skip-render", action="store_true")
    parser.add_argument("--skip-wa", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    template = pick_template(args.slug, args.post_number)
    if args.dry_run:
        print(json.dumps({"ok": True, "dry_run": True, "template": template}, ensure_ascii=False, indent=2))
        return

    post = create_post(template, args.platform)

    if not args.skip_render:
        try:
            subprocess.run(
                [sys.executable, str(ROOT / "execution" / "render-social-post.py"), "--post-id", post["id"]],
                check=True,
                cwd=str(ROOT),
            )
            refreshed = sb("GET", f"social_posts?id=eq.{post['id']}&limit=1")
            if refreshed:
                post = refreshed[0]
        except (subprocess.CalledProcessError, SystemExit) as e:
            print(f"Render atlandı/uyarı: {e}", file=sys.stderr)

    if not args.skip_wa:
        send_approval_wa(post, template)

    print(json.dumps({
        "ok": True,
        "post_id": post["id"],
        "approval_token": post.get("approval_token"),
        "slug": template["slug"],
        "post_number": template["post_number"],
        "status": post.get("status"),
        "image_path": post.get("image_path"),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
