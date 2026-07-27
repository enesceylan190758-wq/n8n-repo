#!/usr/bin/env python3
"""Saha CRM: Excel klinik listesini nefalix_state ile merge et.

Sheets:
  - Arama Listesi (Öncelikli)  → dalga=1
  - 2. Dalga (İskelet Branşlar) → dalga=2

Kurallar:
  - İsim eşleşirse alanları güncelle (notes/appts/busy dokunulmaz)
  - Yoksa yeni klinik ekle
  - aranmadi + dolu sorumlu → hatirlatma=bugün (Dinamik'e düşsün)

Kullanım:
  cd /Users/enesceylan/n8n-repo
  python3 execution/import-saha-crm-excel.py
  python3 execution/import-saha-crm-excel.py --dry-run
  python3 execution/import-saha-crm-excel.py "/path/to/file.xlsx"
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
DEFAULT_XLSX = Path.home() / "Downloads" / "NefalixAI_Klinik_Arama_Listesi (1).xlsx"
SHEETS = {
    "Arama Listesi (Öncelikli)": 1,
    "2. Dalga (İskelet Branşlar)": 2,
    "Diş Klinikleri - Anadolu": 1,
}

ANADOLU_HINTS = (
    "kadıköy", "kadikoy", "ataşehir", "atasehir", "üsküdar", "uskudar",
    "maltepe", "kartal", "pendik", "ümraniye", "umraniye", "tuzla",
    "sultanbeyli", "çekmeköy", "cekmekoy", "sancaktepe", "beykoz", "şile",
    "sile", "anadolu", "moda", "bostancı", "bostanci", "kozyatağı", "kozyatagi",
)
AVRUPA_HINTS = (
    "şişli", "sisli", "beşiktaş", "besiktas", "bakırköy", "bakirkoy",
    "beyoğlu", "beyoglu", "fatih", "kağıthane", "kagithane", "sarıyer",
    "sariyer", "zeytinburnu", "bahçelievler", "bahcelievler", "güngören",
    "gungoren", "avcılar", "avcilar", "esenyurt", "başakşehir", "basaksehir",
    "gaziosmanpaşa", "gaziosmanpasa", "eyüp", "eyup", "nişantaşı", "nisantasi",
    "levent", "etiler", "mecidiyeköy", "mecidiyekoy", "avrupa",
)
BRANS_OK = {
    "Diş Kliniği",
    "Saç Ekimi",
    "Estetik/Plastik",
    "Tıp Merkezi",
    "Hastane",
    "Muayenehane",
    "Güzellik/Cilt",
}


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


def norm_name(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"\s+", " ", s)
    return s


def col_letter_to_idx(col: str) -> int:
    n = 0
    for ch in col:
        if ch.isalpha():
            n = n * 26 + (ord(ch.upper()) - 64)
    return n - 1


def parse_xlsx_sheet(path: Path, sheet_name: str) -> list[dict]:
    with zipfile.ZipFile(path) as z:
        shared: list[str] = []
        if "xl/sharedStrings.xml" in z.namelist():
            root = ET.fromstring(z.read("xl/sharedStrings.xml"))
            for si in root.findall("m:si", NS):
                shared.append("".join(t.text or "" for t in si.findall(".//m:t", NS)))

        wb = ET.fromstring(z.read("xl/workbook.xml"))
        name_to_rid = {}
        for sh in wb.findall("m:sheets/m:sheet", NS):
            name_to_rid[sh.get("name")] = sh.get(
                "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
            )
        if sheet_name not in name_to_rid:
            raise SystemExit(f"Sheet yok: {sheet_name}. Var: {list(name_to_rid)}")

        rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        rid_to_target = {
            r.get("Id"): r.get("Target")
            for r in rels
            if r.tag.endswith("Relationship")
        }
        target = (rid_to_target[name_to_rid[sheet_name]] or "").lstrip("/")
        if not target.startswith("xl/"):
            target = "xl/" + target

        root = ET.fromstring(z.read(target))
        rows_out: list[list[str | None]] = []
        for row in root.findall("m:sheetData/m:row", NS):
            cells: dict[int, str | None] = {}
            max_i = -1
            for c in row.findall("m:c", NS):
                ref = c.get("r") or "A1"
                col = "".join(ch for ch in ref if ch.isalpha())
                idx = col_letter_to_idx(col)
                max_i = max(max_i, idx)
                t = c.get("t")
                if t == "inlineStr":
                    is_el = c.find("m:is", NS)
                    cells[idx] = (
                        "".join(t_el.text or "" for t_el in is_el.findall(".//m:t", NS))
                        if is_el is not None
                        else None
                    )
                    continue
                v = c.find("m:v", NS)
                if v is None:
                    cells[idx] = None
                    continue
                if t == "s":
                    cells[idx] = shared[int(v.text)]
                else:
                    cells[idx] = v.text
            if max_i < 0:
                rows_out.append([])
                continue
            rows_out.append([cells.get(i) for i in range(max_i + 1)])

    def fold(s: str) -> str:
        # TR: İ.lower() → i̇ (combining dot); normalize for matching
        return (
            (s or "")
            .replace("İ", "i")
            .replace("I", "i")
            .replace("ı", "i")
            .replace("Ş", "s")
            .replace("ş", "s")
            .replace("Ğ", "g")
            .replace("ğ", "g")
            .replace("Ü", "u")
            .replace("ü", "u")
            .replace("Ö", "o")
            .replace("ö", "o")
            .replace("Ç", "c")
            .replace("ç", "c")
            .lower()
        )

    # Find header row with İşletme Adı
    header_i = None
    headers: list[str] = []
    for i, row in enumerate(rows_out):
        joined = " | ".join(fold(str(x or "")) for x in row)
        if "isletme" in joined or "klinik adi" in joined:
            headers = [str(x or "").strip() for x in row]
            header_i = i
            break
    if header_i is None:
        raise SystemExit(f"{sheet_name}: İşletme Adı başlığı bulunamadı")

    def col(*keys: str) -> int | None:
        for i, h in enumerate(headers):
            hl = fold(h)
            if any(fold(k) in hl for k in keys):
                return i
        return None

    i_brans = col("branş", "brans")
    i_ad = col("işletme", "isletme", "klinik", "firma")
    i_semt = col("semt", "ilçe", "ilce")
    i_bolge = col("bölge", "bolge")
    i_adres = col("adres")
    i_tel = col("telefon", "tel", "gsm")
    i_web = col("web", "site")
    i_olcek = col("ölçek", "olcek", "tahmini")
    i_ul = col("uluslararası", "uluslararasi")
    i_skor = col("skor", "puan")
    i_sorumlu = col("sorumlu")

    if i_ad is None:
        raise SystemExit(f"{sheet_name}: ad sütunu yok")

    def cell(row: list, idx: int | None) -> str:
        if idx is None or idx >= len(row):
            return ""
        v = row[idx]
        return "" if v is None else str(v).strip()

    clinics: list[dict] = []
    for row in rows_out[header_i + 1 :]:
        ad = cell(row, i_ad)
        brans = cell(row, i_brans)
        if not ad:
            continue
        if brans and brans not in BRANS_OK and ad.lower() in ("işletme adı", "isletme adi"):
            continue
        if not brans and ad.lower().startswith("nefalix"):
            continue
        skor_raw = cell(row, i_skor)
        try:
            skor = int(float(skor_raw)) if skor_raw else 3
        except ValueError:
            skor = 3
        semt = cell(row, i_semt)
        bolge = cell(row, i_bolge)
        clinics.append(
            {
                "ad": ad,
                "brans": brans or ("Diş Kliniği" if "anadolu" in fold(sheet_name) else ""),
                "semt": semt,
                "bolge": bolge or semt,
                "adres": cell(row, i_adres),
                "tel": cell(row, i_tel),
                "web": cell(row, i_web),
                "olcek": cell(row, i_olcek),
                "uluslararasi": cell(row, i_ul),
                "skor": skor,
                "sorumlu": cell(row, i_sorumlu),
                "yaka": "Anadolu Yakası" if "anadolu" in fold(sheet_name) else "",
            }
        )
    return clinics


def infer_yaka(c: dict) -> str:
    existing = (c.get("yaka") or "").strip()
    if existing:
        return existing
    blob = " ".join(
        str(c.get(k) or "") for k in ("semt", "bolge", "adres", "ad")
    ).lower()
    if any(h in blob for h in ANADOLU_HINTS):
        return "Anadolu Yakası"
    if any(h in blob for h in AVRUPA_HINTS):
        return "Avrupa Yakası"
    # Mevcut Avrupa-odaklı liste varsayılanı
    return "Avrupa Yakası"


def sb(method: str, path: str, *, body: dict | None = None, prefer: str = "return=representation"):
    """REST call — direct Supabase or n8n proxy (Vercel prod)."""
    table, _, query = path.partition("?")
    proxy = os.environ.get("N8N_SUPABASE_PROXY_URL") or "https://api.nefalix.com/webhook/nefalix/supabase-proxy"
    internal = os.environ.get("NEFALIX_INTERNAL_KEY")
    url_sb = (os.environ.get("SUPABASE_URL") or "").rstrip("/")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or ""

    use_proxy = bool(internal) and (
        os.environ.get("SAHA_CRM_FORCE_PROXY") == "1"
        or not url_sb
        or "127.0.0.1" in url_sb
        or "localhost" in url_sb
        or "host.docker.internal" in url_sb
        or "kong" in url_sb
    )

    if use_proxy:
        payload = {
            "method": method,
            "table": table,
            "query": query,
            "body": body,
            "prefer": prefer,
        }
        req = urllib.request.Request(
            proxy,
            data=json.dumps(payload).encode(),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "X-Nefalix-Internal-Key": internal,
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                raw = resp.read().decode()
                data = json.loads(raw) if raw else None
        except urllib.error.HTTPError as e:
            err = e.read().decode()
            raise SystemExit(f"Proxy HTTP {e.code}: {err[:500]}") from e
        if isinstance(data, dict) and data.get("error"):
            raise SystemExit(f"Proxy error: {data['error']}")
        return data.get("data") if isinstance(data, dict) and "data" in data else data

    if not url_sb or not key:
        raise SystemExit("SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY veya NEFALIX_INTERNAL_KEY gerekli")
    url = f"{url_sb}/rest/v1/{path}"
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": prefer,
    }
    data_b = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data_b, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        err = e.read().decode()
        raise SystemExit(f"Supabase HTTP {e.code}: {err[:500]}") from e


def load_vercel_env() -> None:
    """Optional: nefalix-landing/.env.local.vercel (vercel env pull)."""
    for p in (
        Path("/Users/enesceylan/nefalix-landing/.env.local.vercel"),
        REPO.parent / "nefalix-landing" / ".env.local.vercel",
    ):
        if not p.exists():
            continue
        for line in p.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            v = v.strip().strip('"').strip("'")
            # Prefer production proxy key over local 127.0.0.1
            if k.strip() in ("NEFALIX_INTERNAL_KEY", "N8N_SUPABASE_PROXY_URL"):
                os.environ[k.strip()] = v
            else:
                os.environ.setdefault(k.strip(), v)



def uid() -> str:
    import secrets

    return secrets.token_hex(4)


def merge(existing: dict, rows: list[tuple[dict, int]], today: str) -> tuple[dict, dict]:
    data = json.loads(json.dumps(existing))  # deep copy
    clinics = data.setdefault("clinics", [])
    by_name = {norm_name(c.get("ad", "")): c for c in clinics if c.get("ad")}
    stats = {"updated": 0, "added": 0, "hatirlatma": 0}

    for row, dalga in rows:
        key = norm_name(row["ad"])
        if not key:
            continue
        if key in by_name:
            c = by_name[key]
            for field in (
                "brans",
                "semt",
                "bolge",
                "adres",
                "tel",
                "web",
                "olcek",
                "uluslararasi",
                "skor",
                "sorumlu",
                "yaka",
            ):
                if row.get(field) not in (None, ""):
                    c[field] = row[field]
            c["dalga"] = dalga
            stats["updated"] += 1
        else:
            c = {
                "id": "c" + uid(),
                **row,
                "dalga": dalga,
                "segment": "aranmadi",
                "sonArama": None,
                "hatirlatma": None,
                "aramaSayisi": 0,
            }
            clinics.append(c)
            by_name[key] = c
            stats["added"] += 1

        # Yeni Anadolu importunda dinamik kuyruğuna düşmesin (sorumlu boş kalsın)
        if (c.get("yaka") == "Anadolu Yakası") and not (row.get("sorumlu") or "").strip():
            c["sorumlu"] = c.get("sorumlu") or ""
            # hatirlatma kurma

        seg = c.get("segment") or "aranmadi"
        if seg == "aranmadi" and (c.get("sorumlu") or "").strip():
            if not c.get("hatirlatma"):
                c["hatirlatma"] = today
                stats["hatirlatma"] += 1

        c["yaka"] = infer_yaka(c)

    # Eski kayıtlara da yaka yaz
    for c in clinics:
        c["yaka"] = infer_yaka(c)

    data["clinics"] = clinics
    data["rev"] = int(data.get("rev") or 0) + 1
    for k in ("notes", "busy", "appts", "notifs"):
        data.setdefault(k, [])
    return data, stats


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("xlsx", nargs="?", default=str(DEFAULT_XLSX))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    load_env()
    load_vercel_env()
    path = Path(args.xlsx)
    if not path.exists():
        raise SystemExit(f"Dosya yok: {path}")
    if not (
        os.environ.get("NEFALIX_INTERNAL_KEY")
        or (os.environ.get("SUPABASE_URL") and os.environ.get("SUPABASE_SERVICE_ROLE_KEY"))
    ):
        raise SystemExit("SUPABASE_* veya NEFALIX_INTERNAL_KEY eksik")

    # Dosyada hangi sheet varsa onu al (eski 2-sheet + Anadolu)
    with zipfile.ZipFile(path) as z:
        wb = ET.fromstring(z.read("xl/workbook.xml"))
        present = [sh.get("name") for sh in wb.findall("m:sheets/m:sheet", NS)]

    collected: list[tuple[dict, int]] = []
    matched = [(s, d) for s, d in SHEETS.items() if s in present]
    if not matched and present:
        matched = [(present[0], 1)]
    if not matched:
        raise SystemExit(f"Sheet yok. Var: {present}")

    for sheet, dalga in matched:
        rows = parse_xlsx_sheet(path, sheet)
        print(f"{sheet}: {len(rows)} klinik (dalga={dalga})")
        for r in rows:
            collected.append((r, dalga))

    rows = sb("GET", "nefalix_state?id=eq.1&select=data,rev")
    if not rows:
        raise SystemExit("nefalix_state id=1 yok")
    existing = rows[0].get("data") or {"clinics": [], "notes": [], "busy": [], "appts": [], "notifs": [], "rev": 0}
    if not isinstance(existing.get("clinics"), list):
        existing = {"clinics": [], "notes": [], "busy": [], "appts": [], "notifs": [], "rev": 0}

    today = date.today().isoformat()
    merged, stats = merge(existing, collected, today)
    print(
        f"Önceki: {len(existing.get('clinics') or [])} → Yeni: {len(merged['clinics'])} | "
        f"updated={stats['updated']} added={stats['added']} hatirlatma={stats['hatirlatma']} rev={merged['rev']}"
    )

    if args.dry_run:
        print("dry-run: yazılmadı")
        return

    sb(
        "PATCH",
        "nefalix_state?id=eq.1",
        body={"data": merged, "rev": merged["rev"]},
        prefer="return=minimal",
    )
    print("OK: nefalix_state güncellendi")


if __name__ == "__main__":
    main()
