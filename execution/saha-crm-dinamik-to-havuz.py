#!/usr/bin/env python3
"""Saha CRM: Dinamik Arama listesini Klinik Havuzuna geri çek (nefalix_state id=1).

Kurallar (crm.html takipListesi ile aynı):
  - hatirlatma dolu + sahip = user → dinamikte
  - segment=aranmadi + sorumlu = user → dinamikte

Havuza çek = hatirlatma temizle + sorumlu boşalt + segment=aranmadi
(notlar / randevular / busy dokunulmaz)

Kullanım:
  python3 execution/saha-crm-dinamik-to-havuz.py --all
  python3 execution/saha-crm-dinamik-to-havuz.py --user en
  python3 execution/saha-crm-dinamik-to-havuz.py --all --dry-run
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
USER_ALIASES = {
    "en": "en",
    "enes": "en",
    "ak": "ak",
    "abdulkadir": "ak",
    "kd": "kd",
    "kader": "kd",
    "mi": "mi",
    "destek": "mi",
}
ALL_UIDS = ("en", "ak", "kd", "mi")


def load_env() -> None:
    env_path = REPO / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

    # Saha CRM (nefalix_state id=1) VPS local Supabase'te yaşar.
    # n8n container URL'si host'tan çözülmez → 127.0.0.1'e çevir.
    url = (os.environ.get("SUPABASE_URL") or "").rstrip("/")
    if "host.docker.internal" in url:
        os.environ["SUPABASE_URL"] = url.replace("host.docker.internal", "127.0.0.1")
        url = os.environ["SUPABASE_URL"]

    # Mac local 54321 kapalıysa cloud PROD dene (id=1 genelde VPS'te).
    if (not url) or any(x in url for x in ("127.0.0.1", "localhost", "kong")):
        # Önce mevcut URL'yi dene; başarısız olursa caller hata verir.
        # Cloud'a zorla geçme — id=1 VPS'te.
        pass


def sb(method: str, path: str, body: dict | None = None, prefer: str = "return=representation"):
    base = os.environ["SUPABASE_URL"].rstrip("/")
    key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    url = f"{base}/rest/v1/{path.lstrip('/')}"
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": prefer,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Supabase {method} {path}: {e.code} {e.read().decode()[:500]}") from e


def sorumlu_id(c: dict) -> str:
    n = (c.get("sorumlu") or "").lower()
    if "abd" in n:
        return "ak"
    if "enes" in n:
        return "en"
    if "kader" in n:
        return "kd"
    if "destek" in n:
        return "mi"
    return ""


def sahibi(c: dict, notes: list[dict]) -> str:
    cid = c.get("id")
    for n in notes:
        if n.get("clinicId") == cid:
            return n.get("userId") or ""
    return sorumlu_id(c)


def fark_gun(hatirlatma: str) -> int:
    a = date.fromisoformat(date.today().isoformat())
    b = date.fromisoformat(hatirlatma)
    return (b - a).days


def takip_listesi(clinics: list[dict], notes: list[dict], uid: str | None) -> list[dict]:
    """crm.html takipListesi ile birebir (uid=None = Tüm ekip)."""
    out: list[dict] = []
    for c in clinics:
        own = uid is None or sahibi(c, notes) == uid
        if not own:
            continue
        if c.get("hatirlatma"):
            if fark_gun(c["hatirlatma"]) <= 7:
                out.append(c)
            continue
        if (c.get("segment") or "aranmadi") == "aranmadi" and sorumlu_id(c) and (
            uid is None or sorumlu_id(c) == uid
        ):
            out.append(c)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", default="en", help="en|enes|ak|abdulkadir|kd|kader|mi|destek")
    ap.add_argument("--all", action="store_true", help="Tüm kullanıcıların dinamik listesini havuza çek")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    load_env()
    for k in ("SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY"):
        if not os.environ.get(k):
            raise SystemExit(f"{k} eksik")

    host = os.environ["SUPABASE_URL"].split("//", 1)[-1].split("/", 1)[0]
    print(f"supabase_host={host}")

    uid = None
    if not args.all:
        uid = USER_ALIASES.get(args.user.lower())
        if not uid:
            raise SystemExit(f"Bilinmeyen user: {args.user}")

    rows = sb("GET", "nefalix_state?id=eq.1&select=data,rev")
    if not rows:
        raise SystemExit("nefalix_state id=1 yok")
    data = rows[0]["data"]
    rev = int(rows[0].get("rev") or data.get("rev") or 1)
    clinics = data.get("clinics") or []
    notes = data.get("notes") or []

    before = {u: len(takip_listesi(clinics, notes, u)) for u in ALL_UIDS}
    targets = takip_listesi(clinics, notes, uid)
    scope = "ALL" if args.all else uid
    print(f"scope={scope} dinamik_hedef={len(targets)} toplam_klinik={len(clinics)} rev={rev}")
    print("önce:", before)
    for c in targets[:12]:
        print(
            f"  - {c.get('ad')} | seg={c.get('segment')} | "
            f"sorumlu={c.get('sorumlu')!r} | hat={c.get('hatirlatma')}"
        )
    if len(targets) > 12:
        print(f"  … +{len(targets) - 12} daha")

    if args.dry_run:
        print("DRY-RUN — kayıt yok")
        return 0

    ids = {c["id"] for c in targets}
    changed = 0
    for c in clinics:
        if c.get("id") not in ids:
            continue
        c["hatirlatma"] = None
        c["sorumlu"] = ""
        c["segment"] = "aranmadi"
        changed += 1

    data["clinics"] = clinics
    data["rev"] = rev + 1
    sb(
        "PATCH",
        "nefalix_state?id=eq.1",
        {"data": data, "rev": rev + 1},
        prefer="return=minimal",
    )

    rows2 = sb("GET", "nefalix_state?id=eq.1&select=data,rev")
    d2 = rows2[0]["data"]
    after = {
        u: len(takip_listesi(d2.get("clinics") or [], d2.get("notes") or [], u)) for u in ALL_UIDS
    }
    left_all = len(takip_listesi(d2.get("clinics") or [], d2.get("notes") or [], None))
    print(f"OK: {changed} klinik havuza çekildi · kalan_dinamik_all={left_all}")
    print("sonra:", after)
    return 0


if __name__ == "__main__":
    sys.exit(main())
