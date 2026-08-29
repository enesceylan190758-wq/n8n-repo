#!/usr/bin/env python3
"""Meta (Facebook/Instagram) Graph API + Google Ads API → Supabase reklam performans senkronu.

Kaynak tablo: ad_accounts (klinik ↔ platform ↔ hesap eşlemesi)
Hedef tablo: ad_insights_daily (günlük kampanya metrikleri)

Gereksinim (.env):
  META_ACCESS_TOKEN         Meta Marketing API long-lived token (ads_read izni)
  GOOGLE_ADS_DEVELOPER_TOKEN
  GOOGLE_ADS_ACCESS_TOKEN   OAuth access token (refresh token'dan üretilir, süresi kısa)
  GOOGLE_ADS_LOGIN_CUSTOMER_ID  (MCC kullanılıyorsa)

Kullanım:
  python3 execution/sync-ads-performance.py                         # tüm hesaplar, son 7 gün
  python3 execution/sync-ads-performance.py --platform meta         # yalnız Meta
  python3 execution/sync-ads-performance.py --clinic-id UUID --days 30
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, timedelta
from pathlib import Path

META_API_VERSION = "v21.0"
META_BASE = f"https://graph.facebook.com/{META_API_VERSION}"
GOOGLE_ADS_API_VERSION = "v18"
GOOGLE_ADS_BASE = f"https://googleads.googleapis.com/{GOOGLE_ADS_API_VERSION}"


def env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def supabase_key() -> str:
    return env(
        "SUPABASE_SERVICE_ROLE_KEY",
        env(
            "SUPABASE_ANON_KEY",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0.EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU",
        ),
    )


def supabase_base() -> str:
    return env("SUPABASE_URL", "http://127.0.0.1:54321").rstrip("/")


def sb_request(method: str, path: str, body: dict | list | None = None, prefer: str = "return=minimal") -> object:
    url = f"{supabase_base()}/rest/v1/{path}"
    headers = {
        "apikey": supabase_key(),
        "Authorization": f"Bearer {supabase_key()}",
        "Content-Type": "application/json",
        "Prefer": prefer,
    }
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        detail = e.read().decode()
        raise RuntimeError(f"Supabase {method} {path}: {e.code} {detail[:400]}") from e


def http_get(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "NefalixAdsSync/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        detail = e.read().decode()
        raise RuntimeError(f"{url.split('?')[0]}: {e.code} {detail[:500]}") from e


def http_post_json(url: str, headers: dict, body: dict) -> dict:
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, method="POST", headers={**headers, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        detail = e.read().decode()
        raise RuntimeError(f"{url.split('?')[0]}: {e.code} {detail[:500]}") from e


def load_ad_accounts(clinic_id: str | None, platform: str | None) -> list[dict]:
    query = "select=id,clinic_id,platform,account_id,account_name,status&status=eq.active&order=platform.asc"
    if clinic_id:
        query += f"&clinic_id=eq.{clinic_id}"
    if platform and platform != "all":
        query += f"&platform=eq.{platform}"
    rows = sb_request("GET", f"ad_accounts?{query}")
    return rows or []


def mark_account_synced(account_id: str, status: str = "active") -> None:
    sb_request(
        "PATCH",
        f"ad_accounts?id=eq.{account_id}",
        {"last_synced_at": date.today().isoformat() + "T00:00:00Z", "status": status},
    )


def upsert_insight(row: dict) -> None:
    existing = sb_request(
        "GET",
        "ad_insights_daily?"
        + urllib.parse.urlencode(
            {
                "clinic_id": f"eq.{row['clinic_id']}",
                "platform": f"eq.{row['platform']}",
                "campaign_id": f"eq.{row['campaign_id']}",
                "date": f"eq.{row['date']}",
                "select": "id",
            }
        ),
    )
    if existing:
        sb_request("PATCH", f"ad_insights_daily?id=eq.{existing[0]['id']}", row)
    else:
        sb_request("POST", "ad_insights_daily", row)


def meta_action_value(actions: list[dict] | None, action_type: str) -> int:
    for a in actions or []:
        if a.get("action_type") == action_type:
            try:
                return int(float(a.get("value", 0)))
            except (TypeError, ValueError):
                return 0
    return 0


def sync_meta_account(account: dict, since: date, until: date) -> dict:
    token = env("META_ACCESS_TOKEN")
    if not token:
        raise RuntimeError("META_ACCESS_TOKEN eksik — Meta for Developers'ta ads_read token üret")

    fields = "campaign_id,campaign_name,spend,impressions,clicks,ctr,cpc,actions,date_start"
    params = urllib.parse.urlencode(
        {
            "level": "campaign",
            "time_increment": "1",
            "time_range": json.dumps({"since": since.isoformat(), "until": until.isoformat()}),
            "fields": fields,
            "access_token": token,
            "limit": "200",
        }
    )
    url = f"{META_BASE}/{account['account_id']}/insights?{params}"

    rows_written = 0
    while url:
        try:
            data = http_get(url)
        except RuntimeError as exc:
            if "190" in str(exc) or "OAuthException" in str(exc):
                raise RuntimeError(f"Meta token geçersiz/süresi dolmuş: {exc}") from exc
            raise

        for item in data.get("data", []):
            leads = meta_action_value(item.get("actions"), "lead")
            leads += meta_action_value(item.get("actions"), "onsite_conversion.lead_grouped")
            upsert_insight(
                {
                    "clinic_id": account["clinic_id"],
                    "platform": "meta",
                    "account_id": account["account_id"],
                    "campaign_id": item.get("campaign_id", "unknown"),
                    "campaign_name": item.get("campaign_name"),
                    "date": item.get("date_start"),
                    "currency": "TRY",
                    "spend": float(item.get("spend", 0) or 0),
                    "impressions": int(item.get("impressions", 0) or 0),
                    "clicks": int(item.get("clicks", 0) or 0),
                    "leads": leads,
                    "conversions": leads,
                    "cpc": float(item.get("cpc", 0) or 0) or None,
                    "ctr": float(item.get("ctr", 0) or 0) or None,
                }
            )
            rows_written += 1

        url = (data.get("paging") or {}).get("next")

    mark_account_synced(account["id"])
    return {"account": account["account_id"], "platform": "meta", "rows": rows_written, "ok": True}


def sync_google_account(account: dict, since: date, until: date) -> dict:
    dev_token = env("GOOGLE_ADS_DEVELOPER_TOKEN")
    access_token = env("GOOGLE_ADS_ACCESS_TOKEN")
    if not dev_token or not access_token:
        raise RuntimeError(
            "GOOGLE_ADS_DEVELOPER_TOKEN / GOOGLE_ADS_ACCESS_TOKEN eksik — "
            "OAuth refresh token'dan yeni access token üretilmeli (bkz. directives/ads_performance_sync.md)"
        )

    customer_id = account["account_id"].replace("-", "")
    headers = {
        "Authorization": f"Bearer {access_token}",
        "developer-token": dev_token,
    }
    login_customer_id = env("GOOGLE_ADS_LOGIN_CUSTOMER_ID")
    if login_customer_id:
        headers["login-customer-id"] = login_customer_id.replace("-", "")

    query = f"""
        SELECT
          campaign.id, campaign.name,
          segments.date,
          metrics.cost_micros, metrics.impressions, metrics.clicks,
          metrics.conversions, metrics.ctr, metrics.average_cpc
        FROM campaign
        WHERE segments.date BETWEEN '{since.isoformat()}' AND '{until.isoformat()}'
    """
    url = f"{GOOGLE_ADS_BASE}/customers/{customer_id}/googleAds:searchStream"

    try:
        data = http_post_json(url, headers, {"query": query})
    except RuntimeError as exc:
        if "UNAUTHENTICATED" in str(exc) or "401" in str(exc):
            raise RuntimeError(f"Google Ads token geçersiz/süresi dolmuş: {exc}") from exc
        raise

    rows_written = 0
    batches = data if isinstance(data, list) else [data]
    for batch in batches:
        for result in batch.get("results", []):
            campaign = result.get("campaign", {})
            metrics = result.get("metrics", {})
            segments = result.get("segments", {})
            cost_micros = int(metrics.get("costMicros", 0) or 0)
            upsert_insight(
                {
                    "clinic_id": account["clinic_id"],
                    "platform": "google",
                    "account_id": account["account_id"],
                    "campaign_id": str(campaign.get("id", "unknown")),
                    "campaign_name": campaign.get("name"),
                    "date": segments.get("date"),
                    "currency": "TRY",
                    "spend": cost_micros / 1_000_000,
                    "impressions": int(metrics.get("impressions", 0) or 0),
                    "clicks": int(metrics.get("clicks", 0) or 0),
                    "leads": int(float(metrics.get("conversions", 0) or 0)),
                    "conversions": int(float(metrics.get("conversions", 0) or 0)),
                    "cpc": (int(metrics.get("averageCpc", 0) or 0) / 1_000_000) or None,
                    "ctr": float(metrics.get("ctr", 0) or 0) or None,
                }
            )
            rows_written += 1

    mark_account_synced(account["id"])
    return {"account": account["account_id"], "platform": "google", "rows": rows_written, "ok": True}


def main() -> int:
    parser = argparse.ArgumentParser(description="Meta/Google Ads → Supabase reklam performans senkronu")
    parser.add_argument("--platform", choices=["meta", "google", "all"], default="all")
    parser.add_argument("--clinic-id", help="Tek klinik UUID")
    parser.add_argument("--days", type=int, default=7, help="Kaç günlük geçmiş çekilsin (varsayılan 7)")
    args = parser.parse_args()

    until = date.today() - timedelta(days=1)
    since = until - timedelta(days=args.days - 1)

    accounts = load_ad_accounts(args.clinic_id, args.platform)
    if not accounts:
        print("Aktif ad_accounts kaydı yok — önce ad_accounts tablosuna klinik/hesap eşlemesi ekleyin", file=sys.stderr)
        return 1

    results = []
    for account in accounts:
        label = f"{account['platform']}:{account['account_id']}"
        print(f"▶ {label} ({since} → {until})")
        try:
            if account["platform"] == "meta":
                res = sync_meta_account(account, since, until)
            else:
                res = sync_google_account(account, since, until)
            print(f"  ✓ {res['rows']} satır senkron edildi")
            results.append(res)
        except Exception as exc:
            print(f"  ✗ {exc}", file=sys.stderr)
            if "token" in str(exc).lower():
                try:
                    mark_account_synced(account["id"], status="token_expired")
                except Exception:
                    pass
            results.append({"account": account["account_id"], "platform": account["platform"], "ok": False, "error": str(exc)})

    ok = sum(1 for r in results if r.get("ok"))
    print(f"\n{'═' * 50}")
    print(f"Reklam senkron: {ok}/{len(results)} hesap başarılı")
    print(f"{'═' * 50}")

    summary_path = Path(__file__).resolve().parent.parent / ".tmp" / "ads-performance-sync.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    return 0 if ok == len(results) else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
