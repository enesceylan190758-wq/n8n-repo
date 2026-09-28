#!/usr/bin/env python3
"""Canlı /geo /blog smoke: 502 plaintext değil, HTML + pillar link."""
from __future__ import annotations

import argparse
import sys
import urllib.error
import urllib.request

DEFAULT_BASE = "https://nefalix.com"
PILLAR = "/geo/klinik-itibar-yonetimi-yazilimi"


def fetch(url: str, method: str = "GET") -> tuple[int, str, str]:
    req = urllib.request.Request(
        url, method=method, headers={"User-Agent": "NefalixGeoBlogSmoke/1.0"}
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as res:
            body = res.read().decode("utf-8", errors="replace")
            ct = (res.headers.get("Content-Type") or "").split(";")[0].strip().lower()
            return res.status, ct, body
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace") if e.fp else ""
        ct = (e.headers.get("Content-Type") or "").split(";")[0].strip().lower()
        return e.code, ct, body


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--base", default=DEFAULT_BASE)
    args = ap.parse_args()
    base = args.base.rstrip("/")
    failed = 0

    checks = [
        ("GET", "/geo", 200, ["<html", "GEO", "klinik-itibar-yonetimi-yazilimi"]),
        ("HEAD", "/geo", 200, None),
        ("GET", "/blog", 200, ["<html", "Blog"]),
        ("GET", "/geo-sitemap.xml", 200, ["<urlset", "/geo"]),
        ("GET", PILLAR, 200, ["Klinik itibar", "FAQPage"]),
    ]

    for method, path, want, needles in checks:
        url = f"{base}{path}"
        code, ct, body = fetch(url, method=method)
        ok = code == want
        if ok and method == "GET" and needles:
            low = body
            for n in needles:
                if n not in low:
                    ok = False
                    print(f"FAIL {method} {url} — missing {n!r} (ct={ct})")
                    break
        if ok and method == "GET" and "yüklenemedi: fetch failed" in body and "<html" not in body.lower():
            ok = False
            print(f"FAIL {method} {url} — plaintext 502 body")
        mark = "OK  " if ok else "FAIL"
        print(f"{mark} {code} {method:4s} {ct or '-':24s} {url}")
        if not ok:
            failed += 1

    if failed:
        print(
            f"\n{failed} geo/blog check(s) failed — "
            "directives/geo.md (proxy TLS) + landing api/blog.js fallback",
            file=sys.stderr,
        )
        return 1
    print("\ngeo/blog smoke OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
