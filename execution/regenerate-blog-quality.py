#!/usr/bin/env python3
"""Mevcut blog yazılarını kallavi playbook içeriğiyle yeniden üret (slug korunur).

  python3 execution/regenerate-blog-quality.py --limit 5
  python3 execution/regenerate-blog-quality.py --limit 3 --dry-run
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "execution"))

_spec = importlib.util.spec_from_file_location(
    "publish_daily_blog",
    ROOT / "execution" / "publish-daily-blog.py",
)
_mod = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader
_spec.loader.exec_module(_mod)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    rows = _mod.sb(
        "GET",
        f"blog_posts?select=id,slug,title,tag&status=eq.published&order=published_at.desc&limit={args.limit}",
    )
    if not isinstance(rows, list) or not rows:
        print(json.dumps({"ok": False, "error": "blog yok"}))
        raise SystemExit(1)

    used = _mod.recent_slugs()
    results = []
    for i, row in enumerate(rows):
        tag = (row.get("tag") or "Rehber").strip()
        topic = next((t for t in _mod.TOPICS if t.get("tag") == tag), None)
        if not topic:
            topic = _mod.pick_topic(datetime.now().toordinal() + i)
        topic = {
            **topic,
            "angle": (
                f"{row.get('title') or topic.get('angle')}. "
                "Daha derin Swell seviyesinde playbook üret; zayıf içerik olmasın."
            ),
        }
        used_local = set(used) - {row["slug"]}
        post = _mod.generate_post(topic, used_local)
        body = {
            "title": post["title"],
            "tag": post["tag"],
            "excerpt": post["excerpt"],
            "meta_description": post["meta_description"],
            "body_html": post["body_html"],
            "cover_image_url": post["cover_image_url"],
            "footer_image_url": post["footer_image_url"],
            "published_at": datetime.now(timezone.utc).isoformat(),
        }
        if post.get("youtube_video_id"):
            body["youtube_video_id"] = post["youtube_video_id"]
            body["youtube_title"] = post.get("youtube_title")

        entry = {
            "slug": row["slug"],
            "url": f"https://nefalix.com/blog/{row['slug']}",
            "new_title": body["title"],
            "body_len": len(body["body_html"]),
        }
        if args.dry_run:
            entry["dry_run"] = True
            results.append(entry)
            print(json.dumps(entry, ensure_ascii=False), flush=True)
            continue

        _mod.sb("PATCH", f"blog_posts?id=eq.{row['id']}", body)
        results.append(entry)
        print(json.dumps(entry, ensure_ascii=False), flush=True)

    print(json.dumps({"ok": True, "count": len(results), "results": results}, ensure_ascii=False))


if __name__ == "__main__":
    main()
