#!/usr/bin/env python3
"""SERP patch'lerini ~/nefalix-landing (Mac) üzerine uygular."""
from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATCH = ROOT / "nefalix-landing" / "patches"
KIT = ROOT / "nefalix-landing"

SEO_RE = re.compile(
    r"<!-- nefalix-seo-start -->.*?<!-- nefalix-seo-end -->",
    re.DOTALL,
)
TITLE_RE = re.compile(r"<title>[^<]*</title>", re.I)
H1_RE = re.compile(r"(<h1[^>]*>)([^<]+)(</h1>)", re.I)

TITLES = {
    "index.html": "Nefalix — Klinik itibar ve hasta memnuniyet yazılımı",
    "urunler.html": "Klinik itibar ve hasta memnuniyet yazılımı — Nefalix Ürünler",
}
H1_URUNLER = "Klinik itibar ve hasta memnuniyet yazılımı"

SITEMAP_ENTRY = """  <url>
    <loc>https://nefalix.com/klinik-itibar-yonetimi</loc>
    <lastmod>2026-07-29</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.95</priority>
  </url>"""


def default_landing_dir() -> Path:
    home = Path.home()
    candidates = [
        Path("/Users/enesceylan/nefalix-landing"),
        home / "nefalix-landing",
    ]
    for p in candidates:
        if p.is_dir():
            return p
    return candidates[0]


def patch_seo_block(html: str, patch_file: Path) -> str:
    block = patch_file.read_text(encoding="utf-8").strip()
    if "<!-- nefalix-seo-start -->" not in block:
        raise ValueError(f"patch eksik marker: {patch_file}")
    if SEO_RE.search(html):
        return SEO_RE.sub(block, html, count=1)
    # fallback: <head> içine ekle
    return html.replace("<head>", f"<head>\n{block}\n", 1)


def patch_title(html: str, title: str) -> str:
  if TITLE_RE.search(html):
      return TITLE_RE.sub(f"<title>{title}</title>", html, count=1)
  return html.replace("<head>", f"<head>\n<title>{title}</title>\n", 1)


def merge_vercel(landing: Path) -> None:
    dst = landing / "vercel.json"
    src = json.loads((KIT / "vercel.json").read_text(encoding="utf-8"))
    if dst.exists():
        cur = json.loads(dst.read_text(encoding="utf-8"))
        for key in ("redirects", "rewrites"):
            existing = cur.get(key) or []
            incoming = src.get(key) or []
            seen = {json.dumps(x, sort_keys=True) for x in existing}
            for item in incoming:
                sig = json.dumps(item, sort_keys=True)
                if sig not in seen:
                    existing.append(item)
                    seen.add(sig)
            cur[key] = existing
        dst.write_text(json.dumps(cur, indent=2) + "\n", encoding="utf-8")
    else:
        shutil.copy2(KIT / "vercel.json", dst)


def patch_sitemap(landing: Path) -> None:
    for name in ("sitemap.xml", "public/sitemap.xml"):
        sm = landing / name
        if not sm.exists():
            continue
        text = sm.read_text(encoding="utf-8")
        if "klinik-itibar-yonetimi" in text:
            return
        text = text.replace("</urlset>", SITEMAP_ENTRY + "\n</urlset>", 1)
        sm.write_text(text, encoding="utf-8")
        print(f"  sitemap: {sm}")
        return


def main() -> int:
    landing = Path(sys.argv[1]) if len(sys.argv) > 1 else default_landing_dir()
    if not landing.is_dir():
        print(f"HATA: landing yok: {landing}")
        print("  python3 execution/apply-serp-patches.py /Users/enesceylan/nefalix-landing")
        return 1

    print(f"Landing: {landing}")

    # dosya kopyaları
    shutil.copy2(
        ROOT / "nefalix-site-v2" / "klinik-itibar-yonetimi.html",
        landing / "klinik-itibar-yonetimi.html",
    )
    api_dir = landing / "api"
    api_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(KIT / "api" / "geo-sitemap.js", api_dir / "geo-sitemap.js")
    merge_vercel(landing)
    print("  vercel.json + api/geo-sitemap.js + klinik-itibar-yonetimi.html")

    for fname, patch_name in (
        ("index.html", "index-seo-head.html"),
        ("urunler.html", "urunler-seo-head.html"),
    ):
        target = landing / fname
        if not target.exists():
            print(f"  ATLA (yok): {fname}")
            continue
        html = target.read_text(encoding="utf-8")
        html = patch_seo_block(html, PATCH / patch_name)
        html = patch_title(html, TITLES[fname])
        if fname == "urunler.html":
            html = H1_RE.sub(rf"\1{H1_URUNLER}\3", html, count=1)
        target.write_text(html, encoding="utf-8")
        print(f"  patched: {fname}")

    patch_sitemap(landing)
    print("Tamam. Deploy: cd", landing, "&& npx vercel --prod")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
