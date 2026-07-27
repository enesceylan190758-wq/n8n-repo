#!/usr/bin/env python3
"""Excel → Nefalix CRM (nefalix_state id=2) seedKurum + dinamik."""
from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
import zipfile
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCEL = Path(
    os.environ.get(
        "NEFALIX_CRM_EXCEL",
        str(Path.home() / "Downloads" / "NefalixAI_Klinik_Arama_Listesi (1).xlsx"),
    )
)
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
BRANS = {
    "Diş Kliniği",
    "Saç Ekimi",
    "Estetik/Plastik",
    "Tıp Merkezi",
    "Hastane",
    "Muayenehane",
    "Güzellik/Cilt",
}


def load_env() -> None:
    for p in (
        ROOT / ".env",
        Path("/Users/enesceylan/nefalix-landing/.env.local.vercel"),
        Path("/tmp/vercel-env-nfx.txt"),
    ):
        if not p.exists():
            continue
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            k, v = k.strip(), v.strip().strip('"').strip("'")
            if k in ("NEFALIX_INTERNAL_KEY", "N8N_SUPABASE_PROXY_URL"):
                os.environ[k] = v
            else:
                os.environ.setdefault(k, v)


def sb(method: str, path: str, body: dict | None = None, prefer: str = "return=representation"):
    table, _, query = path.partition("?")
    proxy = os.environ.get("N8N_SUPABASE_PROXY_URL") or "https://api.nefalix.com/webhook/nefalix/supabase-proxy"
    internal = os.environ.get("NEFALIX_INTERNAL_KEY")
    url_sb = (os.environ.get("SUPABASE_URL") or "").rstrip("/")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or ""
    use_proxy = bool(internal) and (
        os.environ.get("NEFALIX_CRM_FORCE_PROXY") == "1"
        or not url_sb
        or any(x in url_sb for x in ("127.0.0.1", "localhost", "host.docker.internal", "kong"))
    )
    if use_proxy:
        payload = {"method": method, "table": table, "query": query, "body": body, "prefer": prefer}
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
            raise SystemExit(f"Proxy HTTP {e.code}: {e.read().decode()[:500]}") from e
        if isinstance(data, dict) and data.get("error"):
            raise SystemExit(f"Proxy error: {data['error']}")
        return data.get("data") if isinstance(data, dict) and "data" in data else data

    if not url_sb or not key:
        raise SystemExit("SUPABASE_* veya NEFALIX_INTERNAL_KEY gerekli")
    url = f"{url_sb}/rest/v1/{path}"
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": prefer,
    }
    req = urllib.request.Request(
        url, data=None if body is None else json.dumps(body).encode(), headers=headers, method=method
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Supabase HTTP {e.code}: {e.read().decode()[:500]}") from e


def parse_sheet(z: zipfile.ZipFile, shared: list[str], sheet_path: str, dalga: int) -> list[dict]:
    root = ET.fromstring(z.read(sheet_path))
    out: list[dict] = []
    for row in root.findall("m:sheetData/m:row", NS):
        cells: dict[str, str] = {}
        for c in row.findall("m:c", NS):
            ref = c.get("r") or "A1"
            col = "".join(ch for ch in ref if ch.isalpha())
            t = c.get("t")
            v = c.find("m:v", NS)
            if v is None or v.text is None:
                continue
            cells[col] = shared[int(v.text)] if t == "s" else v.text
        brans = (cells.get("A") or "").strip()
        if brans not in BRANS:
            continue
        ad = (cells.get("B") or "").strip()
        if not ad:
            continue
        sorumlu = (cells.get("N") or "").strip()
        if sorumlu.lower().startswith("enes"):
            sorumlu = "Enes Ceylan"
        elif "abd" in sorumlu.lower():
            sorumlu = "Abdülkadir Yaşar"
        try:
            skor = int(float(cells.get("K") or 3))
        except Exception:
            skor = 3
        kid = "xl-" + re.sub(r"[^a-z0-9]+", "-", ad.lower())[:48].strip("-")
        out.append(
            {
                "_id": kid,
                "ID": kid,
                "Ad": ad,
                "Telefon": (cells.get("F") or "").strip(),
                "Kurum tipi": brans,
                "Şehir": (cells.get("C") or "").strip(),
                "Adres": (cells.get("E") or "").strip(),
                "Bölge": (cells.get("D") or "").strip(),
                "Web": (cells.get("G") or "").strip(),
                "Satış temsilcisi": sorumlu,
                "Segment": "Yeni Lead",
                "Skor": skor,
                "Dalga": dalga,
            }
        )
    return out


def parse_excel(path: Path) -> list[dict]:
    with zipfile.ZipFile(path) as z:
        shared: list[str] = []
        if "xl/sharedStrings.xml" in z.namelist():
            root = ET.fromstring(z.read("xl/sharedStrings.xml"))
            for si in root.findall("m:si", NS):
                shared.append("".join((t.text or "") for t in si.findall(".//m:t", NS)))
        wb = ET.fromstring(z.read("xl/workbook.xml"))
        names = [s.get("name") for s in wb.findall("m:sheets/m:sheet", NS)]
        sheets = sorted(
            [n for n in z.namelist() if n.startswith("xl/worksheets/sheet")],
            key=lambda x: int(re.search(r"sheet(\d+)", x).group(1)),
        )
        want = {"Arama Listesi (Öncelikli)": 1, "2. Dalga (İskelet Branşlar)": 2}
        all_k: list[dict] = []
        for idx, name in enumerate(names):
            if name not in want:
                continue
            all_k.extend(parse_sheet(z, shared, sheets[idx], want[name]))
        return all_k


def main() -> None:
    load_env()
    os.environ.setdefault("NEFALIX_CRM_FORCE_PROXY", "1")
    if not EXCEL.exists():
        raise SystemExit(f"Excel yok: {EXCEL}")
    kurumlar = parse_excel(EXCEL)
    print(f"Parsed {len(kurumlar)} kurum")
    today = date.today().strftime("%d.%m.%Y")
    dinamik = {}
    for k in kurumlar:
        if not k.get("Satış temsilcisi"):
            continue
        dinamik[k["_id"]] = {
            "Segment": "Aranacak",
            "nextCallDate": today,
            "done": False,
            "Satış temsilcisi": k["Satış temsilcisi"],
            "Değişiklik tarihi": today,
        }

    rows = sb("GET", "nefalix_state?id=eq.2&select=id,data,rev")
    if not rows:
        data = {"rev": 1, "bag": {"nfx_dinamik": dinamik}, "seedKurum": kurumlar}
        sb("POST", "nefalix_state", {"id": 2, "data": data, "rev": 1}, prefer="return=minimal")
        print("Inserted nefalix_state id=2")
    else:
        row = rows[0] if isinstance(rows, list) else rows
        data = row.get("data") or {}
        bag = dict(data.get("bag") or {})
        bag["nfx_dinamik"] = {**(bag.get("nfx_dinamik") or {}), **dinamik}
        existing = {str(x.get("Ad", "")).lower(): x for x in (data.get("seedKurum") or [])}
        for k in kurumlar:
            key = k["Ad"].lower()
            if key in existing:
                existing[key].update({kk: vv for kk, vv in k.items() if vv not in (None, "")})
            else:
                existing[key] = k
        merged = list(existing.values())
        rev = int(row.get("rev") or 0) + 1
        payload = {"rev": rev, "bag": bag, "seedKurum": merged}
        sb("PATCH", "nefalix_state?id=eq.2", {"data": payload, "rev": rev}, prefer="return=minimal")
        print(f"Updated id=2 rev={rev} seedKurum={len(merged)} dinamik={len(dinamik)}")


if __name__ == "__main__":
    main()
