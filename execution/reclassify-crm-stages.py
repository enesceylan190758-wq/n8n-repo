#!/usr/bin/env python3
"""crm_contacts stage reclassify (Stella → Hasta CRM hotfix).

Kural (P0 — Stella lead listesi ile hizalı):
  - segment yeni_data / yeni_lead / yeni_gelen → stage=lead
  - diğer her şey (segmentsiz dahil) → stage=danisan

Çalıştırma (oturumlu clinic API — VPS SSH gerekmez):
  python3 execution/reclassify-crm-stages.py
  python3 execution/reclassify-crm-stages.py --dry-run

Proxy/SQL alternatifi (VPS veya laptop + NEFALIX_INTERNAL_KEY):
  NEFALIX_CRM_FORCE_PROXY=1 python3 execution/reclassify-crm-stages.py --via-proxy

VPS SQL (hızlı):
  UPDATE crm_contacts SET stage='danisan'
  WHERE clinic_id='51738ea8-...' AND stage='lead'
    AND COALESCE(segment_code,'') NOT IN ('yeni_data','yeni_lead','yeni_gelen');
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from http.cookiejar import CookieJar

CLINIC = "51738ea8-c12e-40ce-a0e2-42869496d76b"
BASE = os.environ.get("NEFALIX_SITE", "https://nefalix.com").rstrip("/")
NEW_SEG_CODES = {"yeni_data", "yeni_lead", "yeni_gelen"}


def http_json(opener, url: str, method: str = "GET", body: dict | None = None) -> dict:
    data = None if body is None else json.dumps(body).encode()
    headers = {"Accept": "application/json"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    with opener.open(req, timeout=120) as resp:
        raw = resp.read().decode()
        return json.loads(raw) if raw.strip() else {}


def clinic_opener(kod: str = "enes"):
    jar = CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    http_json(opener, f"{BASE}/api/clinic/login", "POST", {"kod": kod})
    return opener


def fetch_stage(opener, stage: str, limit: int = 300) -> list[dict]:
    url = f"{BASE}/api/clinic/leads?stage={urllib.parse.quote(stage)}&limit={limit}"
    j = http_json(opener, url)
    return list(j.get("contacts") or [])


def should_be_danisan(c: dict) -> bool:
    """Lead listesi yalnızca yeni* — segmentsiz / diğer → danisan."""
    seg = (c.get("segment_code") or "").strip()
    if seg in NEW_SEG_CODES:
        return False
    return True


def should_be_lead(c: dict) -> bool:
    seg = (c.get("segment_code") or "").strip()
    return seg in NEW_SEG_CODES


def patch_stage(opener, contact_id: str, stage: str, dry: bool) -> None:
    if dry:
        print(f"  dry-run PATCH {contact_id} → {stage}")
        return
    http_json(
        opener,
        f"{BASE}/api/blog?action=clinic-contact",
        "POST",
        {"id": contact_id, "stage": stage},
    )


def via_proxy(dry: bool) -> int:
    """Direct Supabase via n8n proxy (needs NEFALIX_INTERNAL_KEY)."""
    sys.path.insert(0, str(__file__).rsplit("/", 1)[0])
    # reuse import-stella sb helper pattern
    proxy = os.environ.get("N8N_SUPABASE_PROXY_URL") or "https://api.nefalix.com/webhook/nefalix/supabase-proxy"
    key = os.environ.get("NEFALIX_INTERNAL_KEY") or ""
    if not key:
        raise SystemExit("NEFALIX_INTERNAL_KEY gerekli (--via-proxy)")

    def sb(method: str, table: str, query: str = "", body: dict | None = None):
        payload = {"method": method, "table": table, "query": query, "body": body, "prefer": "return=representation"}
        req = urllib.request.Request(
            proxy,
            data=json.dumps(payload).encode(),
            method="POST",
            headers={
                "Content-Type": "application/json",
                "X-Nefalix-Internal-Key": key,
            },
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw.strip() else []

    rows = sb(
        "GET",
        "crm_contacts",
        f"clinic_id=eq.{CLINIC}&select=id,stage,segment_code,assigned_to&limit=5000",
    )
    if isinstance(rows, dict):
        rows = rows.get("data") or rows.get("rows") or []
    to_danisan = [r for r in rows if r.get("stage") == "lead" and should_be_danisan(r)]
    to_lead = [r for r in rows if r.get("stage") == "danisan" and should_be_lead(r)]
    print(f"proxy rows={len(rows)} → danisan {len(to_danisan)}, → lead {len(to_lead)}")
    if dry:
        return 0
    for r in to_danisan:
        sb("PATCH", "crm_contacts", f"id=eq.{r['id']}", {"stage": "danisan"})
    for r in to_lead:
        sb("PATCH", "crm_contacts", f"id=eq.{r['id']}", {"stage": "lead"})
    print("proxy reclassify done")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--via-proxy", action="store_true")
    ap.add_argument("--kod", default="enes")
    args = ap.parse_args()

    if args.via_proxy:
        return via_proxy(args.dry_run)

    opener = clinic_opener(args.kod)
    leads = fetch_stage(opener, "lead", 5000)
    danisan = fetch_stage(opener, "danisan", 5000)
    print(f"API leads={len(leads)} danisan={len(danisan)}")

    to_danisan = [c for c in leads if should_be_danisan(c)]
    print(f"lead → danisan: {len(to_danisan)}")
    for c in to_danisan:
        print(f"  {c.get('ad')} seg={c.get('segment_code')} assigned={c.get('assigned_to')}")
        patch_stage(opener, c["id"], "danisan", args.dry_run)

    # Özet: yalnızca yeni* lead kalmalı
    keep = sum(1 for c in leads if should_be_lead(c))
    print(f"lead kalan (yeni*): {keep}/{len(leads)}")
    print("ok" if not to_danisan else ("dry-run" if args.dry_run else "patched"))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except urllib.error.HTTPError as e:
        print("HTTP", e.code, e.read()[:300], file=sys.stderr)
        raise SystemExit(1)
