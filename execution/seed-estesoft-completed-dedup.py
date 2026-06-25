#!/usr/bin/env python3
"""Estesoft'taki mevcut Tamamlandı randevularını dedup işaretle (mesaj/taslak üretme).

Yeni pilot açılışında geçmiş hastalara NPS gitmesin diye automation_events'e yazar.
wf-12 / wf-13 bu kayıtları görünce atlar.

Kullanım (VPS):
  cd /opt/nefalix && python3 execution/seed-estesoft-completed-dedup.py
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CLINIC_ID = "51738ea8-c12e-40ce-a0e2-42869496d76b"
BASE = os.environ.get("ESTESOFT_STELLA_API_BASE", "https://medidentistanbul.stellamedi.com").rstrip("/")
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def load_env() -> None:
    env_path = REPO / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip())


def norm(s: str) -> str:
    import unicodedata

    return unicodedata.normalize("NFD", str(s or "")).encode("ascii", "ignore").decode().lower()


def http(method: str, url: str, *, headers: dict | None = None, body: dict | None = None) -> object:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        err = e.read().decode()
        print(f"HTTP {e.code} {url}: {err[:400]}", file=sys.stderr)
        raise


def estesoft_token() -> str:
    api_key = os.environ["ESTESOFT_API_KEY"]
    user = os.environ["ESTESOFT_API_USERNAME"]
    password = os.environ["ESTESOFT_API_PASSWORD"]
    res = http(
        "POST",
        f"{BASE}/api/AuthApi/GetToken",
        headers={
            "apikey": api_key,
            "Content-Type": "application/json-patch+json",
            "Accept": "application/json",
            "User-Agent": UA,
        },
        body={"username": user, "password": password},
    )
    token = res.get("token") or res.get("accessToken")
    if not token:
        raise SystemExit(f"GetToken başarısız: {json.dumps(res)[:300]}")
    return token


def list_appointments(token: str) -> list:
    api_key = os.environ["ESTESOFT_API_KEY"]
    res = http(
        "GET",
        f"{BASE}/api/AppointmentApi/List",
        headers={
            "apikey": api_key,
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "User-Agent": UA,
        },
    )
    return res.get("data") or []


def already_triggered(sb_base: str, sb_key: str, ext_id: str) -> bool:
    q = urllib.parse.urlencode(
        {
            "clinic_id": f"eq.{CLINIC_ID}",
            "event_type": "eq.estesoft_nps_triggered",
            "payload->>appointmentId": f"eq.{ext_id}",
            "select": "id",
            "limit": "1",
        }
    )
    rows = http(
        "GET",
        f"{sb_base}/rest/v1/automation_events?{q}",
        headers={"apikey": sb_key, "Authorization": f"Bearer {sb_key}"},
    )
    return isinstance(rows, list) and len(rows) > 0


def seed_event(sb_base: str, sb_key: str, ext_id: str, appt: dict) -> None:
    http(
        "POST",
        f"{sb_base}/rest/v1/automation_events",
        headers={
            "apikey": sb_key,
            "Authorization": f"Bearer {sb_key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        },
        body={
            "clinic_id": CLINIC_ID,
            "workflow_name": "seed-estesoft-completed-dedup",
            "event_type": "estesoft_nps_triggered",
            "payload": {
                "appointmentId": ext_id,
                "patientName": appt.get("customerName") or "",
                "source": "historical_seed",
            },
            "status": "success",
        },
    )


def sb_base_url() -> str:
    raw = os.environ.get("SUPABASE_URL", "http://127.0.0.1:54321").rstrip("/")
    if "host.docker.internal" in raw:
        return raw.replace("host.docker.internal", "127.0.0.1")
    return raw


def main() -> None:
    load_env()
    sb_base = sb_base_url()
    sb_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not sb_key:
        raise SystemExit("SUPABASE_SERVICE_ROLE_KEY eksik")

    token = estesoft_token()
    appointments = list_appointments(token)
    completed = [
        a
        for a in appointments
        if norm(a.get("statusName")) == "tamamlandi" or a.get("statusState") == "+"
    ]

    seeded = skipped = 0
    for appt in completed:
        ext_id = f"estesoft-{appt.get('id')}"
        if not appt.get("id"):
            continue
        if already_triggered(sb_base, sb_key, ext_id):
            skipped += 1
            continue
        seed_event(sb_base, sb_key, ext_id, appt)
        seeded += 1
        print(f"  ✓ dedup: {ext_id} ({appt.get('customerName', '?')})")

    print(
        f"\n✓ Tamamlandı randevu: {len(completed)} · yeni dedup: {seeded} · zaten vardı: {skipped}"
    )
    print("  Bundan sonra sadece YENİ tamamlanan randevular taslak üretir.")


if __name__ == "__main__":
    main()
