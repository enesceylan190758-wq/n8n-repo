#!/usr/bin/env python3
"""GEO citation skorunu DB'ye yaz (CLI veya CSV).

Kaynak gerçek skorlar: geo_citation_scores.
docs/geo-prompt-baseline.md yalnızca şablon kalır.

Örnekler:
  python3 execution/record-geo-citation.py \\
    --week 2026-07-20 --prompt-id 1 --prompt "Nefalix nedir?" \\
    --engine chatgpt --mention --citation-url https://nefalix.com/geo/2026-07-20

  python3 execution/record-geo-citation.py --csv .tmp/geo-scores.csv --dry-run
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENGINES = {"chatgpt", "perplexity", "gemini"}


def sb_base() -> str:
    base = os.environ.get("SUPABASE_URL", "http://127.0.0.1:54321").rstrip("/")
    if "host.docker.internal" in base:
        base = "http://127.0.0.1:54321"
    return base


def sb(method: str, path: str, body: dict | list | None = None) -> list | dict:
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not key:
        raise SystemExit("SUPABASE_SERVICE_ROLE_KEY eksik")
    url = f"{sb_base()}/rest/v1/{path}"
    data = json.dumps(body).encode() if body is not None else None
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates,return=representation",
    }
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Supabase {e.code}: {e.read().decode()[:500]}") from e


def monday_of_week(d: date) -> date:
    return d - __import__("datetime").timedelta(days=d.weekday())


def parse_week(value: str) -> str:
    """ISO date (any day in week) → Monday YYYY-MM-DD."""
    value = value.strip()
    if "W" in value.upper():
        # 2026-W30 → Monday of that ISO week
        year_s, week_s = value.upper().replace("W", "-").split("-")[:2]
        # handle 2026--30 from replace; prefer fromisocalendar
        parts = value.upper().split("W")
        year = int(parts[0].rstrip("-"))
        week = int(parts[1])
        return date.fromisocalendar(year, week, 1).isoformat()
    d = date.fromisoformat(value[:10])
    return monday_of_week(d).isoformat()


def truthy(v: str | bool | None) -> bool:
    if isinstance(v, bool):
        return v
    if v is None:
        return False
    return str(v).strip().lower() in {"1", "true", "t", "yes", "y", "m", "c", "evet"}


def row_payload(args_ns: argparse.Namespace) -> dict:
    engine = args_ns.engine.lower().strip()
    if engine not in ENGINES:
        raise SystemExit(f"engine {engine!r} geçersiz; {sorted(ENGINES)}")
    return {
        "week": parse_week(args_ns.week),
        "prompt_id": str(args_ns.prompt_id).strip(),
        "prompt": str(args_ns.prompt).strip(),
        "engine": engine,
        "mention": bool(args_ns.mention),
        "citation_url": (args_ns.citation_url or None) or None,
        "competitor": (args_ns.competitor or None) or None,
        "notes": (args_ns.notes or None) or None,
        "scored_at": datetime.now(timezone.utc).isoformat(),
    }


def load_csv(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            engine = (r.get("engine") or "").lower().strip()
            if engine not in ENGINES:
                raise SystemExit(f"CSV engine geçersiz: {engine!r}")
            rows.append(
                {
                    "week": parse_week(r["week"]),
                    "prompt_id": str(r["prompt_id"]).strip(),
                    "prompt": str(r["prompt"]).strip(),
                    "engine": engine,
                    "mention": truthy(r.get("mention")),
                    "citation_url": (r.get("citation_url") or "").strip() or None,
                    "competitor": (r.get("competitor") or "").strip() or None,
                    "notes": (r.get("notes") or "").strip() or None,
                    "scored_at": datetime.now(timezone.utc).isoformat(),
                }
            )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="GEO citation skor kaydı")
    parser.add_argument("--csv", help="CSV import (week,prompt_id,prompt,engine,mention,...)")
    parser.add_argument("--week", help="Hafta (YYYY-MM-DD veya 2026-W30)")
    parser.add_argument("--prompt-id")
    parser.add_argument("--prompt")
    parser.add_argument("--engine", choices=sorted(ENGINES))
    parser.add_argument("--mention", action="store_true")
    parser.add_argument("--citation-url")
    parser.add_argument("--competitor")
    parser.add_argument("--notes")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.csv:
        payloads = load_csv(Path(args.csv))
    else:
        missing = [k for k in ("week", "prompt_id", "prompt", "engine") if not getattr(args, k.replace("-", "_"))]
        if missing:
            raise SystemExit(f"CLI alanları eksik: {missing} (veya --csv kullan)")
        payloads = [row_payload(args)]

    if args.dry_run:
        print(json.dumps({"ok": True, "dry_run": True, "rows": payloads}, ensure_ascii=False, indent=2))
        return

    out = sb("POST", "geo_citation_scores", payloads if len(payloads) > 1 else payloads[0])
    print(json.dumps({"ok": True, "written": len(payloads), "result": out}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
