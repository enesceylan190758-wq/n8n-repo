#!/usr/bin/env python3
"""geo_citation_scores → markdown/JSON özet.

  python3 execution/report-geo-citation.py --week 2026-07-20
  python3 execution/report-geo-citation.py --week 2026-W30 --format md
  python3 execution/report-geo-citation.py --all --format json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENGINES = ("chatgpt", "perplexity", "gemini")
EXPECTED_PROMPTS = 25


def sb_base() -> str:
    base = os.environ.get("SUPABASE_URL", "http://127.0.0.1:54321").rstrip("/")
    if "host.docker.internal" in base:
        base = "http://127.0.0.1:54321"
    return base


def sb_get(path: str) -> list | dict:
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not key:
        raise SystemExit("SUPABASE_SERVICE_ROLE_KEY eksik")
    url = f"{sb_base()}/rest/v1/{path}"
    req = urllib.request.Request(
        url,
        headers={"apikey": key, "Authorization": f"Bearer {key}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw.strip() else []
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Supabase {e.code}: {e.read().decode()[:400]}") from e


def parse_week(value: str | None) -> str | None:
    if not value:
        return None
    value = value.strip()
    if "W" in value.upper():
        parts = value.upper().split("W")
        year = int(parts[0].rstrip("-"))
        week = int(parts[1])
        return date.fromisocalendar(year, week, 1).isoformat()
    d = date.fromisoformat(value[:10])
    return (d - __import__("datetime").timedelta(days=d.weekday())).isoformat()


def summarize(rows: list[dict]) -> dict:
    by_week: dict[str, list] = defaultdict(list)
    for r in rows:
        by_week[str(r.get("week") or "")[:10]].append(r)

    weeks = []
    for week, items in sorted(by_week.items(), reverse=True):
        scored_pairs = {(str(i.get("prompt_id")), str(i.get("engine"))) for i in items}
        expected_pairs = EXPECTED_PROMPTS * len(ENGINES)
        mention_or_cite = sum(
            1
            for i in items
            if i.get("mention") or (i.get("citation_url") or "").strip()
        )
        weeks.append(
            {
                "week": week,
                "rows": len(items),
                "expected_rows": expected_pairs,
                "missing_rows": max(0, expected_pairs - len(scored_pairs)),
                "prompt_ids_scored": len({str(i.get("prompt_id")) for i in items}),
                "citation_rate": round(mention_or_cite / len(items), 3) if items else 0.0,
                "engines": {
                    eng: sum(1 for i in items if i.get("engine") == eng) for eng in ENGINES
                },
            }
        )
    return {"weeks": weeks, "total_rows": len(rows)}


def to_markdown(summary: dict) -> str:
    lines = [
        "# GEO Citation Report",
        "",
        "| Hafta | Satır | Eksik | Prompt# | Citation rate |",
        "|-------|-------|-------|---------|---------------|",
    ]
    for w in summary["weeks"]:
        lines.append(
            f"| {w['week']} | {w['rows']} | {w['missing_rows']} | "
            f"{w['prompt_ids_scored']} | {w['citation_rate']:.0%} |"
        )
    lines.append("")
    lines.append(f"Toplam satır: {summary['total_rows']}")
    lines.append("")
    lines.append("Şablon: `docs/geo-prompt-baseline.md` — kaynak skorlar DB.")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--week", help="YYYY-MM-DD veya 2026-W30")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--format", choices=("json", "md"), default="json")
    parser.add_argument("--out", help="Opsiyonel çıktı dosyası")
    args = parser.parse_args()

    week = parse_week(args.week)
    if week:
        path = (
            "geo_citation_scores?select=*&week=eq."
            f"{week}&order=prompt_id.asc,engine.asc"
        )
    elif args.all:
        path = "geo_citation_scores?select=*&order=week.desc,prompt_id.asc"
    else:
        # default: current ISO week Monday
        today = date.today()
        week = (today - __import__("datetime").timedelta(days=today.weekday())).isoformat()
        path = (
            "geo_citation_scores?select=*&week=eq."
            f"{week}&order=prompt_id.asc,engine.asc"
        )

    rows = sb_get(path)
    if not isinstance(rows, list):
        rows = []
    summary = summarize(rows)
    summary["filter_week"] = week
    if args.format == "md":
        text = to_markdown(summary)
    else:
        text = json.dumps({"ok": True, "summary": summary, "rows": rows}, ensure_ascii=False, indent=2)

    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    print(text, end="" if text.endswith("\n") else "\n")


if __name__ == "__main__":
    main()
