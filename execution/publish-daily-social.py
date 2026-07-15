#!/usr/bin/env python3
"""Günlük sosyal medya postu üret → onaya gönder (IG + LinkedIn).

VPS cron (her gün 09:30 TR) veya manuel:
  python3 execution/publish-daily-social.py
  python3 execution/publish-daily-social.py --dry-run
  python3 execution/publish-daily-social.py --skip-notify
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import traceback
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_NOTIFY_TO = "enes.ceylan190758@gmail.com,akadirysr@gmail.com"


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
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Supabase {e.code}: {e.read().decode()[:400]}") from e


def today_start_iso() -> str:
    now = datetime.now(timezone.utc).astimezone()
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return start.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def existing_today() -> dict | None:
    start = today_start_iso()
    rows = sb(
        "GET",
        "social_posts?"
        f"created_at=gte.{start}"
        "&status=in.(pending_approval,approved,published,ready)"
        "&select=id,status,approval_token,metadata,social_post_templates(slug,post_number)"
        "&order=created_at.desc&limit=1",
    )
    return rows[0] if rows else None


def mark_ready(post_id: str) -> None:
    delivery = os.environ.get("SOCIAL_DELIVERY", "manual").strip().lower()
    status = "pending_approval" if delivery == "auto" else "ready"
    sb("PATCH", f"social_posts?id=eq.{post_id}", {
        "status": status,
        "platform": "both",
        "updated_at": datetime.now(timezone.utc).isoformat(),
    })


def mark_pending_approval(post_id: str) -> None:
    mark_ready(post_id)


def notify(post_id: str, to_addrs: str) -> None:
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "execution" / "send-social-notification.py"),
            "--post-id",
            post_id,
            "--to",
            to_addrs,
        ],
        check=True,
        cwd=str(ROOT),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-notify", action="store_true")
    parser.add_argument("--to", default=os.environ.get("SOCIAL_NOTIFY_TO", DEFAULT_NOTIFY_TO))
    parser.add_argument("--force", action="store_true", help="Bugün zaten post varsa yine üret")
    args = parser.parse_args()

    try:
        if not args.force:
            existing = existing_today()
            if existing:
                print(json.dumps({
                    "ok": True,
                    "skipped": True,
                    "reason": "Bugün zaten sosyal post var",
                    "post_id": existing["id"],
                    "status": existing.get("status"),
                }, ensure_ascii=False, indent=2))
                if existing.get("status") == "pending_approval" and not args.skip_notify:
                    notify(existing["id"], args.to)
                return

        if args.dry_run:
            gen = subprocess.run(
                [sys.executable, str(ROOT / "execution" / "social-generate-next.py"), "--dry-run"],
                check=True,
                cwd=str(ROOT),
                capture_output=True,
                text=True,
            )
            print(gen.stdout)
            return

        gen = subprocess.run(
            [sys.executable, str(ROOT / "execution" / "social-generate-next.py")],
            check=True,
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
        result = json.loads(gen.stdout)
        post_id = result["post_id"]
        mark_pending_approval(post_id)

        if not args.skip_notify:
            notify(post_id, args.to)

        refreshed = sb("GET", f"social_posts?id=eq.{post_id}&select=id,status,approval_token,image_url&limit=1")
        post = refreshed[0] if refreshed else {"id": post_id}

        print(json.dumps({
            "ok": True,
            "post_id": post_id,
            "status": post.get("status", "ready"),
            "delivery": os.environ.get("SOCIAL_DELIVERY", "manual"),
            "approval_token": post.get("approval_token"),
            "image_url": post.get("image_url"),
            "slug": result.get("slug"),
        }, ensure_ascii=False, indent=2))
    except Exception as exc:
        err = {"ok": False, "error": str(exc), "trace": traceback.format_exc()}
        print(json.dumps(err, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
