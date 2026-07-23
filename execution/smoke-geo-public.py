#!/usr/bin/env python3
"""Public GEO/blog smoke — canlı yüzeylerin 200 olduğunu doğrular.

  python3 execution/smoke-geo-public.py
  python3 execution/smoke-geo-public.py --base https://nefalix.com
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from datetime import date


def fetch(url: str, *, head: bool = False) -> tuple[int, str]:
    req = urllib.request.Request(
        url,
        method="HEAD" if head else "GET",
        headers={"User-Agent": "Nefalix-GEO-Smoke/1.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = "" if head else resp.read().decode("utf-8", errors="replace")
            return resp.status, body
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")[:200]
    except Exception as e:
        return 0, str(e)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="https://nefalix.com")
    parser.add_argument("--date", help="GEO günü YYYY-MM-DD (default: bugün)")
    args = parser.parse_args()
    base = args.base.rstrip("/")
    day = args.date or date.today().isoformat()

    checks: list[tuple[str, str]] = [
        ("geo_index", f"{base}/geo"),
        ("geo_today", f"{base}/geo/{day}"),
        ("geo_list_api", f"{base}/api/geo/list?limit=5"),
        ("llms", f"{base}/llms.txt"),
        ("geo_sitemap", f"{base}/geo-sitemap.xml"),
        ("blog_index", f"{base}/blog"),
    ]

    results = []
    failed = 0

    # list API → son blog slug
    list_code, list_body = fetch(f"{base}/api/geo/list?limit=5")
    blog_slug = None
    if list_code == 200:
        try:
            data = json.loads(list_body)
            # also try blog list
        except json.JSONDecodeError:
            data = None
    blog_code, blog_body = fetch(f"{base}/api/blog?action=list&limit=3")
    if blog_code == 200:
        try:
            bdata = json.loads(blog_body)
            items = bdata if isinstance(bdata, list) else bdata.get("posts") or bdata.get("items") or []
            if items and isinstance(items, list):
                blog_slug = items[0].get("slug")
        except json.JSONDecodeError:
            pass
    if blog_slug:
        checks.append(("blog_slug", f"{base}/blog/{blog_slug}"))

    for name, url in checks:
        code, body = fetch(url)
        ok = 200 <= code < 400
        # soft: geo_today may 404 if not published yet — still report
        entry = {"name": name, "url": url, "status": code, "ok": ok}
        if name == "llms" and ok and "nefalix" not in body.lower():
            entry["ok"] = False
            entry["error"] = "llms.txt Nefalix içermiyor"
            ok = False
        if name == "geo_list_api" and ok:
            try:
                parsed = json.loads(body)
                entry["list_len"] = len(parsed) if isinstance(parsed, list) else (
                    len(parsed.get("items") or parsed.get("runs") or [])
                    if isinstance(parsed, dict)
                    else 0
                )
            except json.JSONDecodeError:
                entry["ok"] = False
                entry["error"] = "geo list JSON değil"
                ok = False
        if not ok:
            failed += 1
        results.append(entry)

    out = {
        "ok": failed == 0,
        "failed": failed,
        "date": day,
        "results": results,
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
