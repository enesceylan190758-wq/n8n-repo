#!/usr/bin/env python3
"""Stella CustomerApi + AppointmentApi → Supabase crm_contacts / crm_appointments import."""
from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from stella_api import iter_customers, list_appointments, load_env, slug_code

ROOT = Path(__file__).resolve().parents[1]
CLINIC_ID = "51738ea8-c12e-40ce-a0e2-42869496d76b"

CLOSED_SEGMENTS = {
    "5 Kez Ulaşılamadı",
    "10 Kez Ulaşılamadı",
    "Satıldı",
    "Süreci Biten",
    "Tedaviye Uygun Değil",
    "Yanlış Kayıt",
    "Engelledi",
    "Geçersiz Numara (Yanlış)",
    "Başka Yerde Yaptırmış",
    "Olumsuz / İlgilenmiyor",
    "İptal",
}


def sb(method: str, path: str, body: dict | list | None = None, prefer: str = "return=representation"):
    table, _, query = path.partition("?")
    proxy = os.environ.get("N8N_SUPABASE_PROXY_URL") or "https://api.nefalix.com/webhook/nefalix/supabase-proxy"
    internal = os.environ.get("NEFALIX_INTERNAL_KEY")
    url_sb = (os.environ.get("SUPABASE_URL") or "").rstrip("/")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or ""
    # FORCE_PROXY=1 → n8n proxy (laptop → VPS). Aksi halde URL+key varsa doğrudan.
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
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        err = e.read().decode()
        raise RuntimeError(f"HTTP {e.code} {method} {path}: {err[:800]}") from e


def load_users() -> dict[str, str]:
    rows = sb("GET", "crm_users?aktif=eq.true&select=id,ad") or []
    if not isinstance(rows, list):
        raise RuntimeError(f"crm_users unexpected: {type(rows).__name__} {str(rows)[:200]}")
    return {r["ad"].strip().lower(): r["id"] for r in rows if isinstance(r, dict)}


def load_segment_codes() -> dict[str, str]:
    rows = sb("GET", "crm_segments?select=code,label") or []
    if not isinstance(rows, list):
        raise RuntimeError(f"crm_segments unexpected: {type(rows).__name__}")
    out = {}
    for r in rows:
        if not isinstance(r, dict):
            continue
        out[r["label"].strip().lower()] = r["code"]
        out[r["code"]] = r["code"]
    return out


def map_customer(c: dict, users: dict[str, str], seg_map: dict[str, str]) -> dict | None:
    seg_name = (c.get("segmentName") or "").strip()
    if seg_name in CLOSED_SEGMENTS:
        return None
    ctype = c.get("customerTypeName") or ""
    stage = "danisan" if "aktif" in ctype.lower() else "lead"
    rep = (c.get("represent") or "").strip().lower()
    assigned = users.get(rep)
    seg_code = seg_map.get(seg_name.lower())
    kampanya_parts = []
    for k in ("facebookCampaign", "facebookAdSet", "facebookAd"):
        if c.get(k):
            kampanya_parts.append(f"{k}: {c[k]}")
    return {
        "clinic_id": CLINIC_ID,
        "stella_customer_id": str(c["id"]),
        "stage": stage,
        "status": "aktif",
        "ad": (c.get("name") or "(İsimsiz)")[:120],
        "telefon": (c.get("phone") or "")[:30],
        "ulke": (c.get("countryName") or "")[:80],
        "kaynak": (c.get("referenceSource") or "")[:80],
        "email": ((c.get("email") or "")[:120] or None),
        "assigned_to": assigned,
        "segment_code": seg_code,
        "next_call_date": date.today().isoformat(),
        "kampanya": " | ".join(kampanya_parts)[:500] if kampanya_parts else None,
    }


def parse_appt_dt(d: str, t: str) -> str:
    d = (d or "")[:10]
    t = (t or "09:00")[:5]
    if not d:
        return datetime.now(timezone.utc).isoformat()
    return f"{d}T{t}:00+03:00"


def map_appt_status(name: str) -> str:
    n = (name or "").lower()
    if "tamam" in n or "geldi" in n:
        return "tamamlandi"
    if "iptal" in n:
        return "iptal"
    if "ertel" in n:
        return "ertelendi"
    if "gelmedi" in n or "no show" in n:
        return "gelmedi"
    return "beklemede"


def _flush_contacts(batch: list[dict], dry_run: bool, id_map: dict[str, str], total: int) -> list[dict]:
    seen: dict[str, dict] = {}
    for row in batch:
        seen[row["stella_customer_id"]] = row
    uniq = list(seen.values())
    if dry_run:
        print(f"[dry-run] would upsert {len(uniq)} contacts (total {total})")
        return []
    saved = sb(
        "POST",
        "crm_contacts?on_conflict=stella_customer_id",
        body=uniq,
        prefer="resolution=merge-duplicates,return=representation",
    ) or []
    if not isinstance(saved, list):
        raise RuntimeError(f"unexpected save response: {type(saved).__name__} {str(saved)[:200]}")
    print(f"  saved {len(saved)} / sent {len(uniq)}")
    for s in saved:
        if isinstance(s, dict) and s.get("stella_customer_id"):
            id_map[s["stella_customer_id"]] = s["id"]
    return []


def import_customers(dry_run: bool, limit: int | None, skip: int = 0) -> tuple[int, dict[str, str]]:
    users = {} if dry_run else load_users()
    seg_map = {} if dry_run else load_segment_codes()
    id_map: dict[str, str] = {}
    batch: list[dict] = []
    n = 0
    # Zaten import edilmişleri atlamak için mevcut Stella id seti
    existing = set()
    if not dry_run:
        rows = sb("GET", "crm_contacts?select=stella_customer_id&stella_customer_id=not.is.null&limit=10000") or []
        existing = {r["stella_customer_id"] for r in rows if isinstance(r, dict) and r.get("stella_customer_id")}
        print(f"Existing Stella contacts: {len(existing)}")
    for c in iter_customers(page_size=100, max_rows=limit, skip=skip):
        row = map_customer(c, users, seg_map)
        if not row:
            continue
        if row["stella_customer_id"] in existing:
            continue
        batch.append(row)
        n += 1
        if len(batch) >= 50:
            print(f"Flushing {len(batch)} new contacts (imported so far {n})...")
            batch = _flush_contacts(batch, dry_run, id_map, n)
            existing.update(id_map.keys())
    if batch:
        print(f"Flushing final {len(batch)} contacts...")
        _flush_contacts(batch, dry_run, id_map, n)
    if not dry_run:
        rows = sb("GET", "crm_contacts?select=id,stella_customer_id&stella_customer_id=not.is.null&limit=10000") or []
        for r in rows:
            if isinstance(r, dict) and r.get("stella_customer_id"):
                id_map[r["stella_customer_id"]] = r["id"]
    print(f"New customers imported this run: {n}")
    return n, id_map


def import_appointments(dry_run: bool, id_map: dict[str, str], days_back: int, days_fwd: int) -> int:
    start = date.today() - timedelta(days=days_back)
    end = date.today() + timedelta(days=days_fwd)
    batch: list[dict] = []
    n = 0
    for a in list_appointments():
        cid = str(a.get("customerID") or "")
        contact_id = id_map.get(cid)
        if not contact_id:
            continue
        d0 = (a.get("startDate") or "")[:10]
        if not d0:
            continue
        try:
            ad = date.fromisoformat(d0)
        except ValueError:
            continue
        if ad < start or ad > end:
            continue
        row = {
            "stella_appointment_id": str(a["id"]),
            "contact_id": contact_id,
            "start_at": parse_appt_dt(a.get("startDate"), a.get("startTime")),
            "end_at": parse_appt_dt(a.get("endDate") or a.get("startDate"), a.get("endTime")),
            "hizmet": (a.get("serviceName") or "")[:120],
            "personel": (a.get("staffName") or "")[:120],
            "oda": (a.get("branchRoomName") or "")[:80],
            "tip": (a.get("typeName") or "")[:80],
            "durum": map_appt_status(a.get("statusName") or ""),
            "not_text": (a.get("notes") or "")[:500],
        }
        batch.append(row)
        n += 1
        if len(batch) >= 50:
            seen = {r["stella_appointment_id"]: r for r in batch}
            uniq = list(seen.values())
            if not dry_run:
                sb("POST", "crm_appointments?on_conflict=stella_appointment_id", body=uniq, prefer="resolution=merge-duplicates,return=representation")
            else:
                print(f"[dry-run] would upsert {len(uniq)} appointments")
            batch = []
    if batch:
        seen = {r["stella_appointment_id"]: r for r in batch}
        uniq = list(seen.values())
        if not dry_run:
            sb("POST", "crm_appointments?on_conflict=stella_appointment_id", body=uniq, prefer="resolution=merge-duplicates,return=representation")
        else:
            print(f"[dry-run] would upsert {len(uniq)} appointments")
    print(f"Appointments in window: {n}")
    return n


def use_vps_proxy() -> None:
    os.environ["NEFALIX_CRM_FORCE_PROXY"] = "1"
    for k in ("SUPABASE_URL",):
        if any(x in (os.environ.get(k) or "") for x in ("127.0.0.1", "localhost", "host.docker")):
            os.environ.pop(k, None)


def main() -> None:
    load_env()
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--prod", action="store_true", help="VPS Klinik CRM (n8n supabase proxy)")
    ap.add_argument("--limit", type=int, default=None, help="Max Stella rows to scan")
    ap.add_argument("--skip", type=int, default=0, help="Skip first N Stella customers")
    ap.add_argument("--days-back", type=int, default=60)
    ap.add_argument("--days-fwd", type=int, default=90)
    ap.add_argument("--customers-only", action="store_true")
    ap.add_argument("--appointments-only", action="store_true")
    args = ap.parse_args()
    if args.prod:
        use_vps_proxy()
    if not args.appointments_only:
        _, id_map = import_customers(args.dry_run, args.limit, skip=args.skip)
    elif args.dry_run:
        id_map = {}
    else:
        rows = sb("GET", "crm_contacts?select=id,stella_customer_id&stella_customer_id=not.is.null&limit=10000") or []
        id_map = {r["stella_customer_id"]: r["id"] for r in rows}
    if not args.customers_only:
        import_appointments(args.dry_run, id_map, args.days_back, args.days_fwd)


if __name__ == "__main__":
    main()
