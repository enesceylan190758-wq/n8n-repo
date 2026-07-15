#!/usr/bin/env python3
"""Manus Aşama 2 — gerçek logo + nefalix wordmark + footer düzeltme (Pillow).

Usage:
  python3 execution/social-brand-overlay.py --input .tmp/social-renders/raw.png --output .tmp/social-renders/final.png
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

WORDMARK_COLOR = "#1A1A2E"
FOOTER_COLOR = "#64748B"
LOGO_SIZE = int(os.environ.get("SOCIAL_LOGO_SIZE", "96"))
LOGO_PAD = 28
WORDMARK_GAP = 14


def find_logo() -> Path:
    custom = os.environ.get("SOCIAL_LOGO_PATH", "").strip()
    if custom and Path(custom).is_file():
        return Path(custom)
    for p in [
        ROOT / "assets" / "brand" / "nefalix-logo.png",
        ROOT / "assets" / "brand" / "nefalix-logo-512.png",
    ]:
        if p.is_file():
            return p
    raise FileNotFoundError("Logo bulunamadı: assets/brand/nefalix-logo.png")


def find_font(size: int):
    from PIL import ImageFont

    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/Library/Fonts/Arial Bold.ttf",
    ]
    for path in candidates:
        if Path(path).is_file():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def apply_brand(input_path: Path, output_path: Path) -> dict:
    from PIL import Image, ImageDraw

    img = Image.open(input_path).convert("RGBA")
    w, h = img.size
    draw = ImageDraw.Draw(img)

    # 1) Sol üst logo alanını temizle (YZ kalıntısı)
    clean_w = min(340, w // 3)
    clean_h = min(130, h // 8)
    draw.rectangle([0, 0, clean_w, clean_h], fill=(255, 255, 255, 255))

    # 2) Logo — LANCZOS resize
    logo_path = find_logo()
    logo = Image.open(logo_path).convert("RGBA")
    logo.thumbnail((LOGO_SIZE, LOGO_SIZE), Image.Resampling.LANCZOS)
    lx, ly = LOGO_PAD, LOGO_PAD
    img.paste(logo, (lx, ly), logo)

    # 3) Wordmark "nefalix" — logo ile dikey ortalı
    font_size = max(28, LOGO_SIZE // 3)
    font = find_font(font_size)
    wordmark = "nefalix"
    wx = lx + logo.width + WORDMARK_GAP
    bbox = draw.textbbox((0, 0), wordmark, font=font)
    text_h = bbox[3] - bbox[1]
    wy = ly + (logo.height - text_h) // 2
    draw.text((wx, wy), wordmark, fill=WORDMARK_COLOR, font=font)

    # 4) Alt şerit — YZ'nin çizdiği nefalix.com kalıntılarını sil (sol + sağ)
    footer_h = min(56, h // 14)
    footer_top = h - footer_h
    draw.rectangle([0, footer_top, min(360, w // 2), h], fill=(255, 255, 255, 255))
    draw.rectangle([w - 220, footer_top, w, h], fill=(255, 255, 255, 255))

    # 5) Footer sol alt — nefalix.com (tek, net)
    footer_y = h - footer_h + 8
    footer_font = find_font(18)
    footer_text = "nefalix.com"
    draw.text((LOGO_PAD, footer_y), footer_text, fill=FOOTER_COLOR, font=footer_font)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(output_path, "PNG", optimize=True)

    return {
        "overlay": "pillow",
        "logo": str(logo_path),
        "logo_size": LOGO_SIZE,
        "output": str(output_path),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    result = apply_brand(Path(args.input), Path(args.output))
    print(json.dumps({"ok": True, **result}, ensure_ascii=False))


if __name__ == "__main__":
    main()
