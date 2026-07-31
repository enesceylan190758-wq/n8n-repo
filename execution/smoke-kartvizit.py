#!/usr/bin/env python3
"""Kartvizit QR hedefleri canlı mı? /k/enes + /k/abdulkadir + asset."""
from __future__ import annotations

import argparse
import sys
import urllib.error
import urllib.request

CHECKS = [
    ("https://nefalix.com/k/enes", 200, ["Enes Ceylan", "Nefalix", "enes@nefalix.com"]),
    ("https://nefalix.com/k/abdulkadir", 200, ["Abdülkadir", "Nefalix"]),
    ("https://nefalix.com/k/medident", 200, ["MediDent", "medidentistanbul.com", "+90 549"]),
    ("https://nefalix.com/k/card.css", 200, [":root", "--navy"]),
    ("https://nefalix.com/k/enes.vcf", 200, ["BEGIN:VCARD", "Enes Ceylan"]),
    ("https://nefalix.com/k/medident.vcf", 200, ["BEGIN:VCARD", "MediDent"]),
    ("https://nefalix.com/nefalix-logo-512.png", 200, None),
]


def fetch(url: str, timeout: float = 20.0) -> tuple[int, str]:
    req = urllib.request.Request(url, headers={"User-Agent": "nefalix-smoke-kartvizit/1"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            body = res.read().decode("utf-8", errors="replace")
            return res.status, body
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace") if e.fp else ""
        return e.code, body


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="https://nefalix.com")
    args = parser.parse_args()
    base = args.base.rstrip("/")

    failed = 0
    for url, want, needles in CHECKS:
        url = url.replace("https://nefalix.com", base)
        code, body = fetch(url)
        ok = code == want
        if ok and needles:
            for n in needles:
                if n not in body:
                    ok = False
                    print(f"FAIL {url} — missing {n!r}")
                    break
        if ok:
            print(f"OK   {code} {url}")
        else:
            if code != want:
                print(f"FAIL {code} {url} (want {want})")
            failed += 1

    if failed:
        print(f"\n{failed} check(s) failed — Mac: bash execution/deploy-kartvizit-cards.sh")
        return 1
    print("\nall kartvizit checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
