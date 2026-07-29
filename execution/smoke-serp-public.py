#!/usr/bin/env python3
"""Public SERP smoke — entity title, ticari sayfa, host redirect.

  python3 execution/smoke-serp-public.py
  python3 execution/smoke-serp-public.py --check-redirects
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import date


def fetch(
    url: str, *, head: bool = False, follow_redirects: bool = True
) -> tuple[int, str, dict[str, str]]:
    if follow_redirects:
        opener = urllib.request.build_opener()
    else:

        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                return None

        opener = urllib.request.build_opener(NoRedirect())

    req = urllib.request.Request(
        url,
        method="HEAD" if head else "GET",
        headers={"User-Agent": "Nefalix-SERP-Smoke/1.0"},
    )
    try:
        with opener.open(req, timeout=30) as resp:
            body = "" if head else resp.read().decode("utf-8", errors="replace")
            hdrs = {k.lower(): v for k, v in resp.headers.items()}
            return resp.status, body, hdrs
    except urllib.error.HTTPError as e:
        hdrs = {k.lower(): v for k, v in e.headers.items()}
        return e.code, e.read().decode("utf-8", errors="replace")[:500], hdrs
    except Exception as e:
        return 0, str(e), {}


def title_from_html(html: str) -> str | None:
    m = re.search(r"<title[^>]*>([^<]+)</title>", html, re.I)
    return m.group(1).strip() if m else None


def check_redirect(
    source: str, expected_host: str = "nefalix.com"
) -> dict:
    code, _, hdrs = fetch(source, head=True, follow_redirects=False)
    location = hdrs.get("location", "")
    ok = code in (301, 302, 307, 308) and expected_host in location
    return {
        "name": f"redirect_{source.split('//')[1].split('/')[0]}",
        "url": source,
        "status": code,
        "location": location,
        "ok": ok,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="https://nefalix.com")
    parser.add_argument(
        "--check-redirects",
        action="store_true",
        help="www/nefalixai host'larının 301 → nefalix.com olduğunu doğrula",
    )
    args = parser.parse_args()
    base = args.base.rstrip("/")
    today = date.today().isoformat()

    results: list[dict] = []
    failed = 0

    # Homepage title — kanonik entity "Nefalix"
    code, body, _ = fetch(base)
    title = title_from_html(body) if code == 200 else None
    title_ok = bool(title and re.search(r"\bNefalix", title, re.I))
    entry = {
        "name": "homepage_title",
        "url": base,
        "status": code,
        "title": title,
        "ok": code == 200 and title_ok,
    }
    if not entry["ok"]:
        entry["error"] = "title Nefalix entity içermiyor veya sayfa 200 değil"
        failed += 1
    results.append(entry)

    # Ticari landing
    code, _, _ = fetch(f"{base}/urunler")
    urun_ok = code == 200
    entry = {"name": "urunler", "url": f"{base}/urunler", "status": code, "ok": urun_ok}
    if not urun_ok:
        entry["error"] = "/urunler 200 değil"
        failed += 1
    results.append(entry)

    # GEO sitemap — future-dated URL olmamalı
    code, body, _ = fetch(f"{base}/geo-sitemap.xml")
    future_urls: list[str] = []
    if code == 200:
        for m in re.finditer(r"<loc>https?://[^<]+/geo/(\d{4}-\d{2}-\d{2})</loc>", body):
            if m.group(1) > today:
                future_urls.append(m.group(1))
    sitemap_ok = code == 200 and not future_urls
    entry = {
        "name": "geo_sitemap_no_future",
        "url": f"{base}/geo-sitemap.xml",
        "status": code,
        "ok": sitemap_ok,
        "future_dates": future_urls[:10],
    }
    if future_urls:
        entry["error"] = f"gelecek tarihli GEO URL: {future_urls[:3]}"
        failed += 1
    elif code != 200:
        entry["error"] = "geo-sitemap 200 değil"
        failed += 1
    results.append(entry)

    # HEAD geo-sitemap (SOP: HEAD → 200)
    head_code, _, _ = fetch(f"{base}/geo-sitemap.xml", head=True)
    head_ok = head_code == 200
    entry = {
        "name": "geo_sitemap_head",
        "url": f"{base}/geo-sitemap.xml",
        "status": head_code,
        "ok": head_ok,
        "method": "HEAD",
    }
    if not head_ok:
        entry["error"] = "geo-sitemap HEAD 200 değil"
        failed += 1
    results.append(entry)

    if args.check_redirects:
        for host in (
            "https://www.nefalix.com/",
            "https://nefalixai.com/",
            "https://www.nefalixai.com/",
        ):
            entry = check_redirect(host)
            if not entry["ok"]:
                failed += 1
            results.append(entry)

    out = {"ok": failed == 0, "failed": failed, "date": today, "results": results}
    print(json.dumps(out, ensure_ascii=False, indent=2))
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
