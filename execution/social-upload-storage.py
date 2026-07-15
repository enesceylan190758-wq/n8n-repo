#!/usr/bin/env python3
"""Upload social post PNG to Supabase Storage (public bucket) → image_url.

Usage:
  python3 execution/social-upload-storage.py --post-id <uuid>
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


def sb_base() -> str:
    base = os.environ.get("SUPABASE_URL", "http://127.0.0.1:54321").rstrip("/")
    if "host.docker.internal" in base:
        base = "http://127.0.0.1:54321"
    return base


def sb_key() -> str:
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not key:
        raise SystemExit("SUPABASE_SERVICE_ROLE_KEY eksik")
    return key


def sb(method: str, path: str, body: dict | None = None) -> list | dict:
    url = f"{sb_base()}/rest/v1/{path}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "apikey": sb_key(),
            "Authorization": f"Bearer {sb_key()}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = resp.read().decode()
        return json.loads(raw) if raw.strip() else {}


def public_url(object_path: str) -> str:
    base = sb_base()
    return f"{base}/storage/v1/object/public/social-images/{object_path}"


def upload_bytes(object_path: str, content: bytes, content_type: str = "image/png") -> str:
    url = f"{sb_base()}/storage/v1/object/social-images/{object_path}"
    req = urllib.request.Request(
        url,
        data=content,
        method="POST",
        headers={
            "apikey": sb_key(),
            "Authorization": f"Bearer {sb_key()}",
            "Content-Type": content_type,
            "x-upsert": "true",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            resp.read()
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:400]
        raise SystemExit(f"Storage upload {e.code}: {body}") from e
    return public_url(object_path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--post-id", required=True)
    args = parser.parse_args()

    rows = sb("GET", f"social_posts?id=eq.{args.post_id}&select=*,social_post_templates(slug,post_number)&limit=1")
    if not rows:
        raise SystemExit("Post bulunamadı")
    post = rows[0]
    template = post.get("social_post_templates") or {}
    image_path = Path(post.get("image_path") or "")
    if not image_path.is_file():
        raise SystemExit(f"Görsel yok: {image_path}")

    slug = template.get("slug", "post")
    num = template.get("post_number", 0)
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    object_path = f"{date}/post_{num:02d}_{slug}_{args.post_id[:8]}.png"

    image_url = upload_bytes(object_path, image_path.read_bytes())

    meta = post.get("metadata") or {}
    if isinstance(meta, str):
        meta = json.loads(meta)

    sb("PATCH", f"social_posts?id=eq.{args.post_id}", {
        "image_url": image_url,
        "metadata": {**meta, "storage_path": object_path},
        "updated_at": datetime.now(timezone.utc).isoformat(),
    })

    print(json.dumps({
        "ok": True,
        "post_id": args.post_id,
        "image_url": image_url,
        "storage_path": object_path,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
