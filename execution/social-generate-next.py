#!/usr/bin/env python3
"""Pick next social template → GPT görsel → caption → Drive/local paket.

Instagram yüklemesi manuel (planlayıcı). WhatsApp / Meta API yok.

Usage:
  python3 execution/social-generate-next.py
  python3 execution/social-generate-next.py --slug post_01_brand_hero
  python3 execution/social-generate-next.py --dry-run
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Supabase helpers inlined — same as before
import urllib.error
import urllib.request


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
        done = sb(
            "GET",
            "social_posts?status=in.(ready,published)&select=template_id&order=created_at.desc&limit=50",
        )
        done_ids = {p.get("template_id") for p in done if p.get("template_id")}
        for row in rows:
            if row["id"] not in done_ids:
                return row
        return rows[0] if rows else None
    if not rows:
        raise SystemExit("Aktif şablon bulunamadı")
    return rows[0]


def create_post(template: dict) -> dict:
    rows = sb(
        "POST",
        "social_posts",
        {
            "template_id": template["id"],
            "status": "draft",
            "platform": "instagram",
            "headline": template.get("headline_html", "").replace("<br/>", " ").replace("<em>", "").replace("</em>", ""),
            "caption": (template.get("caption_template") or "").strip(),
            "hashtags": (template.get("hashtags") or "").strip(),
            "metadata": {"slug": template["slug"], "post_number": template["post_number"]},
            "updated_at": datetime.now(timezone.utc).isoformat(),
        },
    )
    return rows[0]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--slug")
    parser.add_argument("--post-number", type=int)
    parser.add_argument("--skip-render", action="store_true")
    parser.add_argument("--skip-upload", action="store_true")
    parser.add_argument("--provider", choices=["openai", "html", "auto"], default="auto")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    template = pick_template(args.slug, args.post_number)
    if args.dry_run:
        print(json.dumps({"ok": True, "dry_run": True, "template": template}, ensure_ascii=False, indent=2))
        return

    post = create_post(template)

    if not args.skip_render:
        render_cmd = [
            sys.executable,
            str(ROOT / "execution" / "render-social-image.py"),
            "--post-id",
            post["id"],
        ]
        if args.provider != "auto":
            render_cmd.extend(["--provider", args.provider])
        subprocess.run(render_cmd, check=True, cwd=str(ROOT))

    result = {"post_id": post["id"], "slug": template["slug"], "post_number": template["post_number"]}

    if not args.skip_upload:
        upload = subprocess.run(
            [sys.executable, str(ROOT / "execution" / "social-upload-drive.py"), "--post-id", post["id"]],
            check=True,
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
        result["upload"] = json.loads(upload.stdout)

    refreshed = sb("GET", f"social_posts?id=eq.{post['id']}&limit=1")
    if refreshed:
        post = refreshed[0]

    print(json.dumps({
        "ok": True,
        **result,
        "status": post.get("status"),
        "local_path": (post.get("metadata") or {}).get("local_path"),
        "drive": (post.get("metadata") or {}).get("drive"),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
