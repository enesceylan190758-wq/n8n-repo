#!/usr/bin/env python3
"""Stella segment + referans kaynaklarını Supabase crm_segments / crm_reference_sources'a yükler."""
from __future__ import annotations

import argparse
import csv
import json
import os
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEG_CSV = ROOT / "docs" / "stella_segments.csv"
REF_CSV = ROOT / "docs" / "stella_reference_sources.csv"


def load_env() -> None:
    for p in (ROOT / ".env", Path("/Users/enesceylan/nefalix-landing/.env.local.vercel")):
        if not p.exists():
            continue
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def sb(method: str, path: str, body: dict | list | None = None, prefer: str = "return=representation"):
    table, _, query = path.partition("?")
    proxy = os.environ.get("N8N_SUPABASE_PROXY_URL") or "https://api.nefalix.com/webhook/nefalix/supabase-proxy"
    internal = os.environ.get("NEFALIX_INTERNAL_KEY")
    url_sb = (os.environ.get("SUPABASE_URL") or "").rstrip("/")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or ""
    use_proxy = bool(internal) and (
        os.environ.get("NEFALIX_CRM_FORCE_PROXY") == "1"
        or not url_sb
        or not key
    )
    if use_proxy:
        payload = {"method": method, "table": table, "query": query, "body": body, "prefer": prefer}
        req = urllib.request.Request(
            proxy,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json", "X-Nefalix-Internal-Key": internal},
            method="POST",
        )
    else:
        url = f"{url_sb}/rest/v1/{table}"
        if query:
            url += f"?{query}"
        headers = {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json", "Prefer": prefer}
        req = urllib.request.Request(url, data=json.dumps(body).encode() if body is not None else None, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=90) as resp:
        raw = resp.read().decode()
        return json.loads(raw) if raw else None


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def upsert_segments(dry_run: bool) -> int:
    rows = []
    for r in read_csv(SEG_CSV):
        rows.append({
            "code": r["code"],
            "label": r["label"],
            "gun_offset": int(r.get("gun_offset") or 1),
            "show_in_dynamic": r.get("show_in_dynamic", "true").lower() in ("1", "true", "yes"),
            "hide_in_report": r.get("hide_in_report", "false").lower() in ("1", "true", "yes"),
            "durum": r.get("durum") or "notr",
            "max_dynamic_attempts": int(r["max_dynamic_attempts"]) if r.get("max_dynamic_attempts") else None,
            "sira": int(r.get("sira") or 100),
            "aktif": True,
        })
    if dry_run:
        print(f"[dry-run] {len(rows)} segment upsert")
        return len(rows)
    sb("POST", "crm_segments?on_conflict=code", body=rows, prefer="resolution=merge-duplicates,return=representation")
    print(f"Upserted {len(rows)} segments")
    return len(rows)


def upsert_refs(dry_run: bool) -> int:
    rows = []
    for r in read_csv(REF_CSV):
        rows.append({
            "code": r["code"],
            "label": r["label"],
            "sira": int(r.get("sira") or 100),
            "aktif": True,
        })
    if dry_run:
        print(f"[dry-run] {len(rows)} reference source upsert")
        return len(rows)
    sb("POST", "crm_reference_sources?on_conflict=code", body=rows, prefer="resolution=merge-duplicates,return=representation")
    print(f"Upserted {len(rows)} reference sources")
    return len(rows)


def use_vps_proxy() -> None:
    """Klinik CRM tabloları VPS Supabase'te — proxy zorunlu."""
    os.environ["NEFALIX_CRM_FORCE_PROXY"] = "1"
    # Local/docker URL'i proxy'ye düşsün diye temizle
    for k in ("SUPABASE_URL",):
        if any(x in (os.environ.get(k) or "") for x in ("127.0.0.1", "localhost", "host.docker")):
            os.environ.pop(k, None)


def main() -> None:
    load_env()
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--prod", action="store_true", help="VPS Klinik CRM (n8n supabase proxy)")
    args = ap.parse_args()
    if args.prod:
        use_vps_proxy()
    if not SEG_CSV.exists() or not REF_CSV.exists():
        raise SystemExit(f"CSV missing: {SEG_CSV} / {REF_CSV}")
    upsert_segments(args.dry_run)
    upsert_refs(args.dry_run)


if __name__ == "__main__":
    main()
