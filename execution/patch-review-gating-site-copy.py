#!/usr/bin/env python3
"""Google review-gating uyumsuz site metinlerini düzelt.

Review gating = memnun olmayanı yorumdan uzak tutmak (Google politikasına aykırı).
Bu script canlı nefalix.com HTML'ini indirir, metinleri değiştirir, çıktı yazar.

  python3 execution/patch-review-gating-site-copy.py
  python3 execution/patch-review-gating-site-copy.py --write landing-web
"""
from __future__ import annotations

import argparse
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://nefalix.com"

REPLACEMENTS: list[tuple[str, str]] = [
    (
        "memnunsa Google/Trustpilot yorum davetine yönlendirir, değilse anında klinik ekibine bildirim gönderir.",
        "tek soruyla deneyim ölçülür. Google ve Trustpilot yorum linki tüm hastalara aynı mesajda ve eşit şekilde sunulur; puan skoruna göre gizlenmez veya geciktirilmez (Google işletme politikası). Düşük memnuniyet sinyali ekip görevi açar — amaç şikayeti içeride çözmek, yorumu engellemek değil.",
    ),
    (
        "Memnuniyetsizlik tespitinde yorum öncesi insan müdahalesi",
        "Düşük memnuniyet sinyalinde ekip görevi (içeride çözüm; yorumu filtrelemez)",
    ),
    (
        "NPS/promoter, yorum yanıt hızı, olumsuz sinyal, geri kazanım",
        "NPS, yorum yanıt hızı, memnuniyet sinyali, geri kazanım",
    ),
    (
        "Memnun hasta → yorum daveti",
        "Deneyim anketi → eşit yorum daveti",
    ),
    (
        "Memnun hastayı görünür itibara çevirin.",
        "Deneyimi ölçün, yorumu herkese eşit sunun.",
    ),
    (
        "Olumlu sinyal yakalandığında Google yorum daveti doğru zamanda başlar.",
        "Yorum daveti skora bağlı değil; tüm hastalara aynı anda ve eşit erişimle sunulur.",
    ),
    (
        "<b>Memnun hasta</b><span>Google yorum daveti gönder</span>",
        "<b>Anket tamamlandı</b><span>Yorum linki (tüm hastalara eşit)</span>",
    ),
    (
        "<b>NPS 6 ve altı</b><span>Yöneticiye görev aç</span>",
        "<b>Düşük memnuniyet sinyali</b><span>Ekip görevi (içeride çözüm)</span>",
    ),
    (
        "memnun hastayı yorum bırakmaya yönlendirir.",
        "tedavi sonrası anket sunar; yorum daveti tüm hastalara eşit (review gating yok).",
    ),
    (
        "Tedavi sonrası otomatik anket, memnun hastayı yorum bırakmaya yönlendirir.",
        "Tedavi sonrası otomatik anket; yorum daveti tüm hastalara eşit sunulur.",
    ),
]


def fetch(path: str) -> str:
    url = f"{SITE}{path}"
    req = urllib.request.Request(url, headers={"User-Agent": "Nefalix-Copy-Patch/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8", errors="replace")


def apply(html: str) -> tuple[str, int]:
    count = 0
    for old, new in REPLACEMENTS:
        if old in html:
            html = html.replace(old, new)
            count += 1
    return html, count


def patch_file(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    patched, n = apply(text)
    if n:
        path.write_text(patched, encoding="utf-8")
    return n


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", help="Çıktı klasörü (index.html, urunler.html)")
    args = parser.parse_args()

    pages = [("/", "index.html"), ("/urunler", "urunler.html")]
    total = 0
    for url_path, filename in pages:
        html = fetch(url_path)
        patched, n = apply(html)
        total += n
        if args.write:
            out = Path(args.write)
            out.mkdir(parents=True, exist_ok=True)
            (out / filename).write_text(patched, encoding="utf-8")
            print(f"written {out / filename} ({n} replacements)")
        else:
            print(f"{filename}: {n} replacement groups from live fetch")

    # Local repo files
    for rel in ("nefalix-site-v2/urunler.html", "nefalix-site-v2/index.html"):
        p = ROOT / rel
        if p.exists():
            n = patch_file(p)
            print(f"patched {rel}: {n}")
            total += n

    print(f"done (total replacement groups: {total})")


if __name__ == "__main__":
    main()
