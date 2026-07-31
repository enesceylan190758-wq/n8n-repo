#!/usr/bin/env python3
"""Kartvizit / baskı için Nefalix QR kodları üret."""
from __future__ import annotations

import argparse
from pathlib import Path

import qrcode
from qrcode.constants import ERROR_CORRECT_H
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "brand"
LOGO = OUT / "nefalix-logo-512.png"

PRESETS = {
    "site": "https://nefalix.com?utm_source=kartvizit&utm_medium=qr",
    "enes": "https://nefalix.com/k/enes?utm_source=kartvizit&utm_medium=qr",
    "abdulkadir": "https://nefalix.com/k/abdulkadir?utm_source=kartvizit&utm_medium=qr",
    "medident": "https://nefalix.com/k/medident?utm_source=kartvizit&utm_medium=qr",
    "whatsapp": "https://wa.me/905491190819?text=Merhaba%2C%20Nefalix%20hakk%C4%B1nda%20bilgi%20almak%20istiyorum.",
    "demo": "https://cal.com/enes-ceylan/15min?utm_source=kartvizit",
}


def make_qr(data: str, size_px: int, logo_path: Path | None) -> Image.Image:
    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#062A3A", back_color="#FFFFFF").convert("RGBA")

    if logo_path and logo_path.is_file():
        logo = Image.open(logo_path).convert("RGBA")
        side = img.size[0]
        logo_side = side // 4
        logo.thumbnail((logo_side, logo_side), Image.Resampling.LANCZOS)
        pad = 12
        badge = Image.new("RGBA", (logo.width + pad * 2, logo.height + pad * 2), "#FFFFFF")
        badge.paste(logo, (pad, pad), logo)
        pos = ((side - badge.width) // 2, (side - badge.height) // 2)
        img.paste(badge, pos, badge)

    if img.size[0] != size_px:
        img = img.resize((size_px, size_px), Image.Resampling.NEAREST)
    return img


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preset", choices=list(PRESETS), default="enes")
    parser.add_argument("--url", help="Özel URL (preset yerine)")
    parser.add_argument("--size", type=int, default=1200, help="Çıktı px (baskı için 1200 önerilir)")
    parser.add_argument("--plain", action="store_true", help="Ortada logo yok")
    parser.add_argument("--name", help="Dosya adı kökü (vars: qr-kartvizit-{preset})")
    args = parser.parse_args()

    url = args.url or PRESETS[args.preset]
    stem = args.name or f"qr-kartvizit-{args.preset}"
    logo = None if args.plain else LOGO

    OUT.mkdir(parents=True, exist_ok=True)
    img = make_qr(url, args.size, logo)
    png = OUT / f"{stem}.png"
    img.save(png, "PNG")
    print(f"ok: {png}")
    print(f"url: {url}")


if __name__ == "__main__":
    main()
