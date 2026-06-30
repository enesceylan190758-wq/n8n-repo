#!/usr/bin/env python3
"""Social post image renderer — OpenAI (default) veya HTML/Puppeteer fallback.

Usage:
  python3 execution/render-social-image.py --post-id <uuid>
  python3 execution/render-social-image.py --post-id <uuid> --provider openai
  python3 execution/render-social-image.py --slug post_01_brand_hero --provider html
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RENDER_DIR = ROOT / ".tmp" / "social-renders"


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
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Supabase {method} {path} ({e.code}): {e.read().decode()}") from e


def strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", " ", text or "").replace("  ", " ").strip()


def badges_list(template: dict) -> list[str]:
    badges = template.get("badges") or []
    if isinstance(badges, str):
        badges = json.loads(badges)
    return [str(b) for b in badges]


def build_openai_prompt(template: dict) -> str:
    headline = strip_html(template.get("headline_html", ""))
    subtitle = (template.get("subtitle") or "").strip()
    eyebrow = (template.get("eyebrow") or "").strip()
    badges = badges_list(template)
    post_no = template.get("post_number", "")
    badge_line = " | ".join(badges[:3]) if badges else ""

    return f"""Design a premium Instagram/LinkedIn square social media post (1080x1080 style).

BRAND: NefalixAI — health-tech platform for clinics (patient experience + reputation management)
COLORS: dark navy-black background (#0D1B2A), white text, gold accents (#C9A96E)
STYLE: luxury medical SaaS, minimal, clean typography, lots of whitespace, no clutter

LAYOUT:
- Top: small gold line, NEFALIXAI wordmark (NEFALIX white, AI gold)
- Eyebrow text: "{eyebrow}"
- Large headline: "{headline}"
- Subtitle: "{subtitle}"
- Three pill badges: {badge_line}
- Bottom left: nefalixai@gmail.com (gold) and nefalixai.com (grey-white)
- Bottom right: "POST {post_no} / 10" small grey text

RULES:
- NO phone numbers
- NO stock photos of real identifiable people
- NO wrong brand names
- Text must be readable and correctly spelled in Turkish
- Professional corporate health technology aesthetic"""


def download_url(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "NefalixSocialRender/1.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        dest.write_bytes(resp.read())


def render_openai(template: dict, output: Path) -> dict:
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY eksik")

    model = os.environ.get("SOCIAL_OPENAI_IMAGE_MODEL", "gpt-image-1").strip()
    prompt = build_openai_prompt(template)

    body: dict = {
        "model": model,
        "prompt": prompt,
        "n": 1,
        "size": "1024x1024",
    }
    if model == "dall-e-3":
        body["quality"] = os.environ.get("SOCIAL_OPENAI_IMAGE_QUALITY", "hd")
        body["style"] = os.environ.get("SOCIAL_OPENAI_IMAGE_STYLE", "vivid")
    else:
        # gpt-image-1 returns b64 by default when response_format set
        body["response_format"] = "b64_json"

    req = urllib.request.Request(
        "https://api.openai.com/v1/images/generations",
        data=json.dumps(body).encode(),
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            payload = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"OpenAI image API ({e.code}): {e.read().decode()}") from e

    data = (payload.get("data") or [{}])[0]
    output.parent.mkdir(parents=True, exist_ok=True)

    if data.get("b64_json"):
        output.write_bytes(base64.b64decode(data["b64_json"]))
    elif data.get("url"):
        download_url(data["url"], output)
    else:
        raise RuntimeError(f"OpenAI yanıtında görsel yok: {payload}")

    return {
        "provider": "openai",
        "model": model,
        "revised_prompt": data.get("revised_prompt"),
        "path": str(output),
    }


def render_html(post_id: str, slug: str, output: Path) -> dict:
    cmd = [sys.executable, str(ROOT / "execution" / "render-social-post.py"), "--post-id", post_id, "--output", str(output)]
    subprocess.run(cmd, check=True, cwd=str(ROOT))
    return {"provider": "html", "path": str(output)}


def resolve_provider(explicit: str | None) -> str:
    if explicit:
        return explicit.lower()
    env = os.environ.get("SOCIAL_IMAGE_PROVIDER", "").strip().lower()
    if env in ("openai", "html"):
        return env
    if os.environ.get("OPENAI_API_KEY", "").strip():
        return "openai"
    return "html"


def update_post(post_id: str, image_path: str, meta: dict) -> None:
    public_base = os.environ.get("SOCIAL_PUBLIC_BASE_URL", "").rstrip("/")
    image_url = f"{public_base}/{Path(image_path).name}" if public_base else None

    rows = sb("GET", f"social_posts?id=eq.{post_id}&select=metadata&limit=1")
    existing: dict = {}
    if rows:
        existing = rows[0].get("metadata") or {}
        if isinstance(existing, str):
            existing = json.loads(existing)

    body = {
        "image_path": image_path,
        "metadata": {**existing, "render": meta},
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    if image_url:
        body["image_url"] = image_url

    sb("PATCH", f"social_posts?id=eq.{post_id}", body)


def load_context(post_id: str | None, slug: str | None) -> tuple[dict | None, dict]:
    if post_id:
        rows = sb(
            "GET",
            f"social_posts?id=eq.{post_id}&select=*,social_post_templates(*)&limit=1",
        )
        if not rows:
            raise SystemExit(f"Post bulunamadı: {post_id}")
        post = rows[0]
        template = post.get("social_post_templates")
        if not template:
            raise SystemExit(f"Post şablonu yok: {post_id}")
        return post, template

    if not slug:
        raise SystemExit("--post-id veya --slug gerekli")
    rows = sb("GET", f"social_post_templates?slug=eq.{slug}&limit=1")
    if not rows:
        raise SystemExit(f"Şablon bulunamadı: {slug}")
    return None, rows[0]


def main() -> None:
    parser = argparse.ArgumentParser(description="Render social post image")
    parser.add_argument("--post-id")
    parser.add_argument("--slug")
    parser.add_argument("--provider", choices=["openai", "html", "auto"])
    parser.add_argument("--output")
    args = parser.parse_args()

    post, template = load_context(args.post_id, args.slug)
    slug = template["slug"]
    post_id = post["id"] if post else args.post_id

    output = Path(args.output) if args.output else RENDER_DIR / (
        f"{slug}_{post_id[:8]}.png" if post_id else f"{slug}.png"
    )

    provider = resolve_provider(None if args.provider == "auto" else args.provider)
    result: dict
    errors: list[str] = []

    if provider == "openai":
        try:
            result = render_openai(template, output)
        except Exception as e:  # noqa: BLE001
            errors.append(f"openai: {e}")
            if not post_id:
                raise
            result = render_html(post_id, slug, output)
            result["fallback_from"] = "openai"
    else:
        if not post_id:
            raise SystemExit("HTML render için --post-id gerekli")
        result = render_html(post_id, slug, output)
        result["path"] = str(output)

    if post_id:
        update_post(post_id, str(output), {**result, "errors": errors})

    print(json.dumps({"ok": True, "slug": slug, "post_id": post_id, **result, "errors": errors}, ensure_ascii=False))


if __name__ == "__main__":
    main()
