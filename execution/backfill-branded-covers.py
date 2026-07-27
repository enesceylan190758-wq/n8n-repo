#!/usr/bin/env python3
"""Mevcut blog kapaklarını Unsplash'tan markalı SVG cover URL'lerine çevir."""
from __future__ import annotations

import json
import os
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "execution"))

from branded_cover import branded_cover_url, branded_footer_url  # noqa: E402


def sb_base() -> str:
    base = os.environ.get("SUPABASE_URL", "http://127.0.0.1:54321").rstrip("/")
    if "host.docker.internal" in base:
        base = "http://127.0.0.1:54321"
    return base


def sb(method: str, path: str, body: dict | None = None):
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    url = f"{sb_base()}/rest/v1/{path}"
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


def main() -> None:
    rows = sb("GET", "blog_posts?select=id,slug,title,tag&order=published_at.desc&limit=100")
    n = 0
    for row in rows if isinstance(rows, list) else []:
        title = row.get("title") or "Nefalix"
        tag = row.get("tag") or "Rehber"
        body = {
            "cover_image_url": branded_cover_url(title=title, tag=tag, kind="blog"),
            "footer_image_url": branded_footer_url(tag=tag),
        }
        sb("PATCH", f"blog_posts?id=eq.{row['id']}", body)
        n += 1
        print(json.dumps({"updated": row.get("slug"), "cover": body["cover_image_url"][:80]}, ensure_ascii=False))
    print(json.dumps({"ok": True, "count": n}, ensure_ascii=False))


if __name__ == "__main__":
    main()
