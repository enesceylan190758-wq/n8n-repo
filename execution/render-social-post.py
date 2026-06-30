#!/usr/bin/env python3
"""Render Nefalix social post HTML template to PNG (1080x1080).

Usage:
  python3 execution/render-social-post.py --post-id <uuid>
  python3 execution/render-social-post.py --slug post_01_brand_hero
  python3 execution/render-social-post.py --slug post_01_brand_hero --output .tmp/social-renders/test.png
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "social-templates" / "base.html"
RENDER_DIR = ROOT / ".tmp" / "social-renders"
SCREENSHOT_JS = Path(__file__).resolve().parent / "render-social-screenshot.js"


def sb_request(method: str, path: str, body: dict | None = None) -> list | dict:
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
        detail = e.read().decode()
        raise SystemExit(f"Supabase {method} {path} failed ({e.code}): {detail}") from e


def badges_html(badges: list[str]) -> str:
    parts = []
    for b in badges:
        parts.append(
            f'<div class="badge"><span class="dot"></span>{b}</div>'
        )
    return "\n".join(parts)


def render_html(template_row: dict) -> str:
    html = TEMPLATE.read_text(encoding="utf-8")
    badges = template_row.get("badges") or []
    if isinstance(badges, str):
        badges = json.loads(badges)
    replacements = {
        "{{POST_NUMBER}}": str(template_row.get("post_number", "")),
        "{{EYEBROW}}": template_row.get("eyebrow", ""),
        "{{HEADLINE_HTML}}": template_row.get("headline_html", ""),
        "{{SUBTITLE}}": template_row.get("subtitle", ""),
        "{{BADGES_HTML}}": badges_html(badges),
    }
    for k, v in replacements.items():
        html = html.replace(k, v)
    return html


def screenshot_html(html_path: Path, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    chrome = os.environ.get("CHROME_PATH", "/usr/local/bin/google-chrome")
    cmd = [
        "node",
        str(SCREENSHOT_JS),
        "--input",
        str(html_path),
        "--output",
        str(output_path),
        "--chrome",
        chrome,
    ]
    subprocess.run(cmd, check=True, cwd=str(ROOT))


def load_template_by_slug(slug: str) -> dict:
    rows = sb_request(
        "GET",
        f"social_post_templates?slug=eq.{slug}&select=*&limit=1",
    )
    if not rows:
        raise SystemExit(f"Şablon bulunamadı: {slug}")
    return rows[0]


def load_post(post_id: str) -> tuple[dict, dict]:
    posts = sb_request(
        "GET",
        f"social_posts?id=eq.{post_id}&select=*,social_post_templates(*)&limit=1",
    )
    if not posts:
        raise SystemExit(f"Post bulunamadı: {post_id}")
    post = posts[0]
    template = post.get("social_post_templates")
    if not template:
        raise SystemExit(f"Post şablonu yok: {post_id}")
    return post, template


def update_post_image(post_id: str, image_path: str, image_url: str | None = None) -> None:
    body = {
        "image_path": image_path,
        "updated_at": __import__("datetime").datetime.utcnow().isoformat() + "Z",
    }
    if image_url:
        body["image_url"] = image_url
    sb_request("PATCH", f"social_posts?id=eq.{post_id}", body)


def main() -> None:
    parser = argparse.ArgumentParser(description="Render social post PNG")
    parser.add_argument("--post-id", help="social_posts UUID")
    parser.add_argument("--slug", help="social_post_templates slug")
    parser.add_argument("--output", help="Output PNG path")
    args = parser.parse_args()

    if not args.post_id and not args.slug:
        parser.error("--post-id veya --slug gerekli")

    if args.post_id:
        post, template = load_post(args.post_id)
        slug = template["slug"]
        post_number = template["post_number"]
        output = Path(args.output) if args.output else RENDER_DIR / f"{slug}_{args.post_id[:8]}.png"
    else:
        template = load_template_by_slug(args.slug)
        slug = template["slug"]
        post_number = template["post_number"]
        output = Path(args.output) if args.output else RENDER_DIR / f"{slug}.png"
        post = None

    html = render_html(template)
    html_path = RENDER_DIR / f"{slug}_render.html"
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(html, encoding="utf-8")

    screenshot_html(html_path, output)
    print(json.dumps({"ok": True, "slug": slug, "post_number": post_number, "png": str(output)}))

    if post:
        public_base = os.environ.get("SOCIAL_PUBLIC_BASE_URL", "").rstrip("/")
        image_url = f"{public_base}/{output.name}" if public_base else None
        update_post_image(post["id"], str(output), image_url)


if __name__ == "__main__":
    main()
