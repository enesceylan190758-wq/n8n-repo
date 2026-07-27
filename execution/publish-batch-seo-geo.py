#!/usr/bin/env python3
"""10 blog + 10 GEO (SEO/AI) batch üret → Supabase published → tek digest mail.

  python3 execution/publish-batch-seo-geo.py
  python3 execution/publish-batch-seo-geo.py --dry-run
  python3 execution/publish-batch-seo-geo.py --skip-notify
  python3 execution/publish-batch-seo-geo.py --blogs-only
  python3 execution/publish-batch-seo-geo.py --geos-only
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "execution"))

SITE = "https://nefalix.com"
DEFAULT_TO = "enes.ceylan190758@gmail.com,akadirysr@gmail.com"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


blog_mod = _load("publish_daily_blog", ROOT / "execution" / "publish-daily-blog.py")
geo_mod = _load("publish_daily_geo", ROOT / "execution" / "publish-daily-geo.py")

BLOG_TOPICS = json.loads(
    (ROOT / "execution" / "blog-topics-batch-seo-geo.json").read_text(encoding="utf-8")
)
GEO_TOPICS = json.loads(
    (ROOT / "execution" / "geo-topics-batch-seo-geo.json").read_text(encoding="utf-8")
)


def publish_blogs(*, dry_run: bool) -> list[dict]:
    used = blog_mod.recent_slugs(limit=80)
    out: list[dict] = []
    for i, topic in enumerate(BLOG_TOPICS):
        print(json.dumps({"phase": "blog", "i": i + 1, "tag": topic.get("tag")}, ensure_ascii=False), flush=True)
        post = blog_mod.generate_post(topic, used)
        used.add(post["slug"])
        if dry_run:
            out.append(
                {
                    "title": post["title"],
                    "tag": post["tag"],
                    "slug": post["slug"],
                    "url": f"{SITE}/blog/{post['slug']}",
                    "body_len": len(post.get("body_html") or ""),
                    "dry_run": True,
                }
            )
            continue
        rows = blog_mod.sb("POST", "blog_posts", post)
        row = rows[0] if isinstance(rows, list) and rows else post
        slug = row.get("slug", post["slug"])
        entry = {
            "title": row.get("title", post["title"]),
            "tag": row.get("tag", post["tag"]),
            "slug": slug,
            "url": f"{SITE}/blog/{slug}",
        }
        out.append(entry)
        print(json.dumps({"published_blog": entry}, ensure_ascii=False), flush=True)
    return out


def publish_geos(*, dry_run: bool, force: bool) -> list[dict]:
    out: list[dict] = []
    for i, topic in enumerate(GEO_TOPICS):
        run_date = topic.get("run_date")
        if not run_date:
            raise RuntimeError(f"GEO topic {i} run_date eksik")
        print(
            json.dumps(
                {"phase": "geo", "i": i + 1, "run_date": run_date, "prompt": topic["prompt"][:60]},
                ensure_ascii=False,
            ),
            flush=True,
        )
        if not dry_run and geo_mod.already_ran(run_date):
            if force:
                geo_mod.sb("DELETE", f"geo_daily_runs?run_date=eq.{run_date}")
            else:
                entry = {
                    "prompt": topic["prompt"],
                    "bucket": topic.get("bucket"),
                    "run_date": run_date,
                    "url": geo_mod.public_url(run_date),
                    "skipped": True,
                }
                out.append(entry)
                print(json.dumps({"skipped_geo": entry}, ensure_ascii=False), flush=True)
                continue

        row = geo_mod.generate_geo(topic)
        if dry_run:
            out.append(
                {
                    "prompt": row["prompt"],
                    "bucket": row.get("bucket"),
                    "run_date": row["run_date"],
                    "url": geo_mod.public_url(row["run_date"]),
                    "answer_len": len(row.get("direct_answer") or ""),
                    "dry_run": True,
                }
            )
            continue
        saved = geo_mod.sb("POST", "geo_daily_runs", row)
        entry = {
            "prompt": row["prompt"],
            "bucket": row.get("bucket"),
            "run_date": row["run_date"],
            "url": geo_mod.public_url(row["run_date"]),
            "id": saved[0].get("id") if isinstance(saved, list) and saved else None,
        }
        out.append(entry)
        print(json.dumps({"published_geo": entry}, ensure_ascii=False), flush=True)
    return out


def send_digest(blogs: list[dict], geos: list[dict], to: str) -> dict:
    payload = json.dumps({"blogs": blogs, "geos": geos}, ensure_ascii=False)
    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / "execution" / "send-batch-digest.py"),
            "--payload-json",
            payload,
            "--to",
            to,
        ],
        capture_output=True,
        text=True,
        timeout=90,
    )
    raw = (proc.stdout or "").strip() or (proc.stderr or "").strip()
    if proc.returncode != 0:
        return {"ok": False, "detail": raw[:600]}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"ok": True, "raw": raw[:400]}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-notify", action="store_true")
    parser.add_argument("--blogs-only", action="store_true")
    parser.add_argument("--geos-only", action="store_true")
    parser.add_argument("--force-geo", action="store_true", help="Mevcut run_date varsa silip yeniden yaz")
    parser.add_argument(
        "--to",
        default=os.environ.get("BLOG_NOTIFY_TO", DEFAULT_TO),
    )
    args = parser.parse_args()

    blogs: list[dict] = []
    geos: list[dict] = []
    try:
        if not args.geos_only:
            blogs = publish_blogs(dry_run=args.dry_run)
        if not args.blogs_only:
            geos = publish_geos(dry_run=args.dry_run, force=args.force_geo)

        result = {
            "ok": True,
            "dry_run": args.dry_run,
            "blogs": blogs,
            "geos": geos,
            "blog_count": len(blogs),
            "geo_count": len(geos),
            "at": datetime.now(timezone.utc).isoformat(),
        }

        if not args.dry_run and not args.skip_notify and (blogs or geos):
            result["notify"] = send_digest(blogs, geos, args.to)

        print(json.dumps(result, ensure_ascii=False), flush=True)
    except Exception as exc:
        err = {
            "ok": False,
            "error": str(exc),
            "traceback": traceback.format_exc()[-1500:],
            "blogs_so_far": blogs,
            "geos_so_far": geos,
        }
        print(json.dumps(err, ensure_ascii=False), flush=True)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
