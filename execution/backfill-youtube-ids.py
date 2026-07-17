#!/usr/bin/env python3
"""Mevcut blog + GEO kayıtlarına youtube_video_id ekle (tek seferlik)."""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "execution"))

from pick_youtube_video import pick_youtube_video  # noqa: E402


def sb_base() -> str:
    base = os.environ.get("SUPABASE_URL", "http://127.0.0.1:54321").rstrip("/")
    if "host.docker.internal" in base:
        base = "http://127.0.0.1:54321"
    return base


def sb(method: str, path: str, body: dict | None = None) -> list | dict:
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not key:
        raise SystemExit("SUPABASE_SERVICE_ROLE_KEY eksik")
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
    updated = {"blog": 0, "geo": 0}
    day = datetime.now().toordinal()

    blogs = sb(
        "GET",
        "blog_posts?select=id,slug,title,tag,youtube_video_id&order=published_at.desc&limit=50",
    )
    for i, row in enumerate(blogs if isinstance(blogs, list) else []):
        if row.get("youtube_video_id"):
            continue
        yt = pick_youtube_video(tag=row.get("tag") or "", prompt=row.get("title") or "", day_index=day + i)
        if not yt:
            continue
        sb("PATCH", f"blog_posts?id=eq.{row['id']}", yt)
        updated["blog"] += 1

    geos = sb(
        "GET",
        "geo_daily_runs?select=id,run_date,bucket,prompt,youtube_video_id&order=run_date.desc&limit=50",
    )
    for i, row in enumerate(geos if isinstance(geos, list) else []):
        if row.get("youtube_video_id"):
            continue
        yt = pick_youtube_video(
            tag=row.get("bucket") or "",
            prompt=row.get("prompt") or "",
            day_index=day + i,
        )
        if not yt:
            continue
        sb("PATCH", f"geo_daily_runs?id=eq.{row['id']}", yt)
        updated["geo"] += 1

    print(json.dumps({"ok": True, "updated": updated}, ensure_ascii=False))


if __name__ == "__main__":
    main()
