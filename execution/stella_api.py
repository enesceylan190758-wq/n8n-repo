#!/usr/bin/env python3
"""Estesoft Stella REST client — shared by import scripts."""
from __future__ import annotations

import json
import os
import re
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
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
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def base_url() -> str:
    return os.environ.get("ESTESOFT_STELLA_API_BASE", "https://medidentistanbul.stellamedi.com").rstrip("/")


def slug_code(label: str) -> str:
    s = unicodedata.normalize("NFD", str(label or ""))
    s = s.encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s).strip("_")
    return s[:64] or "segment"


def http(method: str, url: str, *, headers: dict | None = None, body: dict | None = None) -> object:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    with urllib.request.urlopen(req, timeout=90) as resp:
        raw = resp.read().decode()
        return json.loads(raw) if raw else {}


def token() -> str:
    api_key = os.environ["ESTESOFT_API_KEY"]
    user = os.environ["ESTESOFT_API_USERNAME"]
    password = os.environ["ESTESOFT_API_PASSWORD"]
    res = http(
        "POST",
        f"{base_url()}/api/AuthApi/GetToken",
        headers={
            "apikey": api_key,
            "Content-Type": "application/json-patch+json",
            "Accept": "application/json",
            "User-Agent": UA,
        },
        body={"username": user, "password": password},
    )
    tok = res.get("token") or res.get("accessToken")
    if not tok:
        raise RuntimeError(f"GetToken failed: {json.dumps(res)[:300]}")
    return tok


def auth_headers(tok: str | None = None) -> dict[str, str]:
    return {
        "apikey": os.environ["ESTESOFT_API_KEY"],
        "Authorization": f"Bearer {tok or token()}",
        "Accept": "application/json",
        "User-Agent": UA,
    }


def list_customers(*, skip: int = 0, count: int = 100) -> dict:
    # Stella: pagination param is `offset` (not skip)
    q = urllib.parse.urlencode({"resultCount": count, "offset": skip})
    return http("GET", f"{base_url()}/api/CustomerApi/List?{q}", headers=auth_headers())


def iter_customers(page_size: int = 100, max_rows: int | None = None, skip: int = 0):
    total = 0
    while True:
        batch = list_customers(skip=skip, count=page_size)
        rows = batch.get("data") or []
        if not rows:
            break
        for row in rows:
            yield row
            total += 1
            if max_rows and total >= max_rows:
                return
        if len(rows) < page_size:
            break
        skip += page_size


def list_appointments() -> list:
    res = http("GET", f"{base_url()}/api/AppointmentApi/List", headers=auth_headers())
    return res.get("data") or []


def get_appointment(appt_id: str) -> dict:
    q = urllib.parse.urlencode({"id": appt_id})
    return http("GET", f"{base_url()}/api/AppointmentApi/Get?{q}", headers=auth_headers())
