#!/usr/bin/env python3
"""Canlı site kritik asset smoke — CSS/JS 404'ü yakala (stil kırığı)."""
from __future__ import annotations

import argparse
import sys
import urllib.error
import urllib.request

DEFAULT_BASE = "https://nefalix.com"

# (path, must_be_css_or_js_content_type_prefix, min_bytes)
CRITICAL = [
    ("/shared.css", "text/css", 5000),
    ("/shared.js", ("application/javascript", "text/javascript", "application/x-javascript"), 1000),
]


def fetch(url: str) -> tuple[int, str, bytes]:
    req = urllib.request.Request(url, method="GET", headers={"User-Agent": "NefalixSiteAssetsSmoke/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=25) as res:
            return res.status, (res.headers.get("Content-Type") or "").split(";")[0].strip().lower(), res.read()
    except urllib.error.HTTPError as e:
        body = e.read() if e.fp else b""
        return e.code, (e.headers.get("Content-Type") or "").split(";")[0].strip().lower(), body


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--base", default=DEFAULT_BASE)
    ap.add_argument("--also", action="append", default=[], help="Ek path (örn. /nefalix-chat.css)")
    args = ap.parse_args()
    base = args.base.rstrip("/")

    checks = list(CRITICAL)
    for p in args.also:
        checks.append((p if p.startswith("/") else f"/{p}", None, 1))

    failed = 0
    for path, expect_ct, min_bytes in checks:
        url = f"{base}{path}"
        code, ct, body = fetch(url)
        ok = code == 200 and len(body) >= min_bytes
        if expect_ct:
            if isinstance(expect_ct, tuple):
                ok = ok and any(ct.startswith(x) or ct == x for x in expect_ct)
            else:
                ok = ok and (ct.startswith(expect_ct) or ct == expect_ct)
        # HTML 404 sayfası CSS sanılmasın
        if body.lstrip().lower().startswith(b"<!doctype") or b"NOT_FOUND" in body[:200]:
            ok = False
        mark = "OK" if ok else "FAIL"
        print(f"{mark}  {code}  {len(body):6d}B  {ct or '-':30s}  {url}")
        if not ok:
            failed += 1

    # Anasayfa hâlâ shared.css istiyor mu?
    code, _, html = fetch(f"{base}/")
    if code == 200:
        text = html.decode("utf-8", errors="replace")
        if "shared.css" not in text and "styles.css" not in text:
            print("FAIL  anasayfada stylesheet linki yok")
            failed += 1
        elif "shared.css" in text:
            print("INFO anasayfa shared.css referans ediyor")
    else:
        print(f"FAIL  anasayfa HTTP {code}")
        failed += 1

    if failed:
        print(f"\n{failed} kontrol başarısız — directives/site_assets.md", file=sys.stderr)
        return 1
    print("\nTüm kritik asset'ler OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
