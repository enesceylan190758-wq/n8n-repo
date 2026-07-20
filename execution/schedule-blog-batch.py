#!/usr/bin/env python3
"""Bugün N blog yazısı üret — aralıklı yayınla, görseller + bildirim.

  python3 execution/schedule-blog-batch.py --count 3 --interval-hours 2
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent

_spec = importlib.util.spec_from_file_location(
    "publish_daily_blog", ROOT / "execution" / "publish-daily-blog.py"
)
_pdb = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader
_spec.loader.exec_module(_pdb)

pick_topic = _pdb.pick_topic
generate_post = _pdb.generate_post
recent_slugs = _pdb.recent_slugs
sb = _pdb.sb

IMAGES = json.loads((ROOT / "execution" / "blog-images.json").read_text(encoding="utf-8"))
TR = ZoneInfo("Europe/Istanbul")


def images_for_tag(tag: str) -> tuple[str, str]:
    cfg = IMAGES.get(tag) or IMAGES.get("default", {})
    default = IMAGES["default"]
    return (
        cfg.get("cover") or default["cover"],
        cfg.get("footer") or default["footer"],
    )


def publish_label(iso: str) -> str:
    dt = datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(TR)
    now = datetime.now(TR)
    if dt <= now:
        return "Yayında"
    return f"Yayın: {dt.strftime('%d.%m.%Y %H:%M')} (TR)"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=3)
    parser.add_argument("--interval-hours", type=float, default=2.0)
    parser.add_argument("--start-offset-hours", type=float, default=0.0)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--to",
        default="enes.ceylan190758@gmail.com,akadirysr@gmail.com",
    )
    parser.add_argument("--skip-notify", action="store_true")
    args = parser.parse_args()

    used = recent_slugs()
    day_index = datetime.now().toordinal()
    start = datetime.now(TR) + timedelta(hours=args.start_offset_hours)

    created: list[dict] = []
    notify_posts: list[dict] = []

    for i in range(args.count):
        publish_at = (start + timedelta(hours=i * args.interval_hours)).astimezone(timezone.utc)
        topic = pick_topic(day_index + i + len(used))
        post = generate_post(topic, used)
        used.add(post["slug"])

        cover, footer = images_for_tag(post.get("tag") or topic["tag"])
        post["cover_image_url"] = cover
        post["footer_image_url"] = footer
        post["published_at"] = publish_at.isoformat()
        post["status"] = "published"

        url = f"https://nefalix.com/blog/{post['slug']}"
        label = publish_label(post["published_at"])

        if args.dry_run:
            created.append({**post, "url": url, "publish_label": label})
            continue

        rows = sb("POST", "blog_posts", post)
        row = rows[0] if isinstance(rows, list) and rows else post
        item = {
            "slug": row.get("slug", post["slug"]),
            "title": row.get("title", post["title"]),
            "url": url,
            "published_at": row.get("published_at", post["published_at"]),
            "publish_label": label,
        }
        created.append(item)
        notify_posts.append(item)
        print(json.dumps({"ok": True, **item}, ensure_ascii=False))

    if args.dry_run:
        print(json.dumps({"ok": True, "dry_run": True, "posts": created}, ensure_ascii=False, indent=2))
        return

    if not args.skip_notify and notify_posts:
        posts_json = json.dumps(notify_posts, ensure_ascii=False)
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "execution" / "send-blog-notification.py"),
                "--posts-json",
                posts_json,
                "--to",
                args.to,
            ],
            check=False,
        )


if __name__ == "__main__":
    main()
