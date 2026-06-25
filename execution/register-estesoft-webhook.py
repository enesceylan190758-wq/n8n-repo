#!/usr/bin/env python3
"""Estesoft Stella API — token al, webhook aboneliği oluştur.

Swagger: {base}/swagger/v1/swagger.json?apiKey=YOUR_KEY

Kullanım:
  export ESTESOFT_STELLA_API_BASE=https://stellapi.estesoftbulut.com  # Swagger'daki host
  python3 execution/register-estesoft-webhook.py

Gerekli .env:
  ESTESOFT_API_USERNAME, ESTESOFT_API_KEY, ESTESOFT_TENANT_ID
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
NEfALIX_WEBHOOK = os.environ.get(
    "ESTESOFT_NEFALIX_WEBHOOK_URL",
    "https://api.nefalixai.com/webhook/nefalix/estesoft/webhook",
)
BASE = os.environ.get("ESTESOFT_STELLA_API_BASE", "https://medidentistanbul.stellamedi.com").rstrip("/")


def load_env():
    env_path = REPO / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip())


def request(
    method: str,
    path: str,
    body: dict | str | None = None,
    token: str | None = None,
    *,
    content_type: str = "application/json-patch+json",
) -> dict | str:
    api_key = os.environ["ESTESOFT_API_KEY"]
    url = f"{BASE}{path}"
    headers = {
        "apikey": api_key,
        "Content-Type": content_type,
        "Accept": "application/json",
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if body is None:
        data = None
    elif isinstance(body, str):
        data = json.dumps(body).encode()  # JSON string literal
    else:
        data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode()
            if not raw:
                return {}
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                return {"_text": raw}
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            return {"_http_error": e.code, **json.loads(raw)}
        except json.JSONDecodeError:
            return {"_http_error": e.code, "error": raw[:500]}


def get_token() -> str:
    user = os.environ["ESTESOFT_API_USERNAME"]
    password = os.environ.get("ESTESOFT_API_PASSWORD")
    if not password:
        raise SystemExit(
            "❌ ESTESOFT_API_PASSWORD eksik — API anahtarı değil; Estesoft panelindeki API kullanıcı şifresi (.env)"
        )
    out = request("POST", "/api/AuthApi/GetToken", {"username": user, "password": password})
    if out.get("_http_error"):
        raise SystemExit(f"GetToken HTTP {out['_http_error']}: {out}")
    token = out.get("token") or out.get("accessToken")
    if not token and isinstance(out.get("_text"), str):
        token = out["_text"].strip().strip('"')
    if not token:
        raise SystemExit(f"GetToken yanıtında token yok: {out}")
    return token


def main():
    load_env()
    for var in ("ESTESOFT_API_USERNAME", "ESTESOFT_API_KEY"):
        if not os.environ.get(var):
            sys.exit(f"❌ {var} eksik (.env)")

    print(f"▶ Stella API: {BASE}")
    print(f"▶ Nefalix webhook: {NEfALIX_WEBHOOK}")

    token = get_token()
    print("✓ Token alındı")

    info = request("GET", "/api/WebhooksApi/GetInformation", token=token)
    print("\n--- WebhooksApi/GetInformation ---")
    print(json.dumps(info, indent=2, ensure_ascii=False)[:3000])

    # Olay adı swagger / GetInformation'dan gelir; override ile verilebilir
    out = request("POST", "/api/WebhooksApi/Subscribe", NEfALIX_WEBHOOK, token=token)
    print("\n--- WebhooksApi/Subscribe ---")
    print(json.dumps(out, indent=2, ensure_ascii=False))
    if out.get("_http_error"):
        sys.exit(1)
    print("\n✓ Abonelik isteği gönderildi — GetInformation ile doğrula")


if __name__ == "__main__":
    main()
