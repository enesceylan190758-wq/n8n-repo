#!/usr/bin/env python3
"""Manus pipeline — GPT görsel (logo yok) + Pillow logo overlay."""
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
OVERLAY_SCRIPT = ROOT / "execution" / "social-brand-overlay.py"
MANUS_SCRIPT = ROOT / "execution" / "social-manus-generate.py"


def image_provider() -> str:
    pref = os.environ.get("SOCIAL_IMAGE_PROVIDER", "openai").strip().lower()
    has_manus = bool(os.environ.get("MANUS_API_KEY", "").strip())
    if pref == "manus":
        return "manus" if has_manus else "openai"
    if pref == "auto":
        return "manus" if has_manus else "openai"
    return "openai"


def sb(method: str, path: str, body: dict | None = None) -> list | dict:
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not key:
        raise SystemExit("SUPABASE_SERVICE_ROLE_KEY eksik")
    base = os.environ.get("SUPABASE_URL", "http://127.0.0.1:54321").rstrip("/")
    if "host.docker.internal" in base:
        base = "http://127.0.0.1:54321"
    url = f"{base}/rest/v1/{path}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        url, data=data, method=method,
        headers={
            "apikey": key, "Authorization": f"Bearer {key}",
            "Content-Type": "application/json", "Prefer": "return=representation",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = resp.read().decode()
        return json.loads(raw) if raw.strip() else {}


def image_prompt(post: dict) -> str:
    meta = post.get("metadata") or {}
    if isinstance(meta, str):
        meta = json.loads(meta)
    p = (meta.get("ai") or {}).get("image_prompt") or ""
    if p.strip():
        return p.strip()
    tpl = post.get("social_post_templates") or {}
    h = post.get("headline") or re.sub(r"<[^>]+>", " ", tpl.get("headline_html", ""))
    return (
        f'Professional Instagram social media post background for Nefalix. '
        f'Style: Swell CX aesthetic, clean white background. '
        f'Title in bold Turkish: "{h}". '
        f'IMPORTANT: NO LOGO in top left. NO footer URL or nefalix.com text anywhere.'
    )


def render_gpt_image(prompt: str, output: Path) -> dict:
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY eksik")

    models = []
    for m in [
        os.environ.get("SOCIAL_OPENAI_IMAGE_MODEL", "gpt-image-2"),
        *os.environ.get("SOCIAL_OPENAI_IMAGE_FALLBACKS", "gpt-image-1.5,gpt-image-1").split(","),
    ]:
        m = m.strip()
        if m and m not in models:
            models.append(m)

    quality = os.environ.get("SOCIAL_OPENAI_IMAGE_QUALITY", "high").strip()
    size = os.environ.get("SOCIAL_OPENAI_IMAGE_SIZE", "1024x1024").strip()
    last_err = None

    for model in models:
        body: dict = {"model": model, "prompt": prompt, "n": 1, "size": size}
        if model.startswith("gpt-image"):
            body["quality"] = quality
        req = urllib.request.Request(
            "https://api.openai.com/v1/images/generations",
            data=json.dumps(body).encode(), method="POST",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=600) as resp:
                payload = json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            last_err = f"{model}: {e.read().decode()[:300]}"
            continue

        data = (payload.get("data") or [{}])[0]
        output.parent.mkdir(parents=True, exist_ok=True)
        if data.get("b64_json"):
            output.write_bytes(base64.b64decode(data["b64_json"]))
        elif data.get("url"):
            r = urllib.request.Request(data["url"], headers={"User-Agent": "Nefalix/1"})
            output.write_bytes(urllib.request.urlopen(r, timeout=120).read())
        else:
            last_err = f"{model}: görsel yok"
            continue

        return {"provider": "openai", "model": model, "path": str(output)}

    raise RuntimeError(f"gpt-image üretilemedi: {last_err}")


def render_manus_image(prompt: str, output: Path) -> dict:
    cmd = [
        sys.executable,
        str(MANUS_SCRIPT),
        "--prompt", prompt,
        "--output", str(output),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
    if proc.returncode != 0:
        raise RuntimeError(f"Manus render failed: {proc.stderr or proc.stdout}")
    return json.loads(proc.stdout.strip())


def render_image(prompt: str, output: Path) -> dict:
    provider = image_provider()
    if provider == "manus":
        try:
            return render_manus_image(prompt, output)
        except Exception as e:  # noqa: BLE001
            if os.environ.get("SOCIAL_IMAGE_FALLBACK_OPENAI", "1").strip().lower() in ("0", "false"):
                raise
            print(json.dumps({"warn": "manus_failed", "error": str(e)[:200]}), file=sys.stderr)
    return render_gpt_image(prompt, output)


def apply_brand_overlay(raw_path: Path, final_path: Path) -> dict:
    if os.environ.get("SOCIAL_SKIP_BRAND_OVERLAY", "").strip().lower() in ("1", "true"):
        final_path.write_bytes(raw_path.read_bytes())
        return {"overlay": "skipped"}

    cmd = [
        sys.executable,
        str(OVERLAY_SCRIPT),
        "--input", str(raw_path),
        "--output", str(final_path),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
    if proc.returncode != 0:
        raise RuntimeError(f"Brand overlay failed: {proc.stderr or proc.stdout}")
    return json.loads(proc.stdout.strip())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--post-id", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()

    rows = sb("GET", f"social_posts?id=eq.{args.post_id}&select=*,social_post_templates(*)&limit=1")
    if not rows:
        raise SystemExit("Post yok")
    post = rows[0]
    slug = (post.get("social_post_templates") or {}).get("slug", "post")
    stem = f"{slug}_{args.post_id[:8]}"
    final = Path(args.output) if args.output else RENDER_DIR / f"{stem}.png"
    raw = RENDER_DIR / f"{stem}_raw.png"

    prompt = image_prompt(post)
    gen = render_image(prompt, raw)
    overlay = apply_brand_overlay(raw, final)

    meta = post.get("metadata") or {}
    render_meta = {**gen, "overlay": overlay, "method": "manus", "raw_path": str(raw)}
    sb("PATCH", f"social_posts?id=eq.{args.post_id}", {
        "image_path": str(final),
        "metadata": {**meta, "render": render_meta},
        "updated_at": datetime.now(timezone.utc).isoformat(),
    })
    print(json.dumps({"ok": True, "slug": slug, **render_meta}, ensure_ascii=False))


if __name__ == "__main__":
    main()
