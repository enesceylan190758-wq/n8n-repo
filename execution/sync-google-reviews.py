#!/usr/bin/env python3
"""Tüm klinikler için Google Places API → Supabase google_reviews senkronu.

Gereksinim: GOOGLE_PLACES_API_KEY (.env)
Places API (New) etkin: Text Search + Place Details (reviews alanı)

Kullanım:
  python3 execution/sync-google-reviews.py           # tüm klinikler
  python3 execution/sync-google-reviews.py --clinic-id UUID
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

PLACES_BASE = "https://places.googleapis.com/v1"
LEGACY_BASE = "https://maps.googleapis.com/maps/api/place"
PLACE_ID_RE = re.compile(r"(ChIJ[\w-]{20,})")

_api_mode: str | None = None  # "new" | "legacy"


def google_api_key() -> str:
    key = env("GOOGLE_PLACES_API_KEY")
    if not key:
        raise RuntimeError("GOOGLE_PLACES_API_KEY eksik — Google Cloud Console → Places API (New)")
    return key


def legacy_get(path: str, params: dict) -> dict:
    q = urllib.parse.urlencode({**params, "key": google_api_key()})
    url = f"{LEGACY_BASE}/{path}/json?{q}"
    req = urllib.request.Request(url, headers={"User-Agent": "NefalixGoogleSync/1.0"})
    with urllib.request.urlopen(req, timeout=45) as resp:
        data = json.loads(resp.read().decode())
    status = data.get("status")
    if status not in ("OK", "ZERO_RESULTS"):
        msg = data.get("error_message") or status
        raise RuntimeError(f"Legacy Places {path}: {msg}")
    return data


def detect_api_mode() -> str:
    global _api_mode
    if _api_mode:
        return _api_mode
    # SearchText bazı key kısıtlarında kapalı; GetPlace genelde açık kalır
    for probe in (
        lambda: places_request(
            "GET",
            "/places/ChIJpamxPanFyhQRKdIKscKwqi8",
            field_mask="id,rating",
        ),
        lambda: places_request(
            "POST",
            "/places:searchText",
            {"textQuery": "Istanbul", "languageCode": "tr"},
            field_mask="places.id",
        ),
    ):
        try:
            probe()
            _api_mode = "new"
            return _api_mode
        except RuntimeError:
            continue
    try:
        legacy_get("textsearch", {"query": "Istanbul"})
        _api_mode = "legacy"
        return _api_mode
    except RuntimeError as exc:
        raise RuntimeError(
            "Google Places erişilemiyor. Cloud Console'da Places API (New) etkin olsun; "
            "API key → Places API (New) seçili olsun."
        ) from exc


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


def places_request(method: str, path: str, body: dict | None = None, field_mask: str = "") -> dict:
    api_key = google_api_key()

    url = f"{PLACES_BASE}{path}"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
    }
    if field_mask:
        headers["X-Goog-FieldMask"] = field_mask

    data = json.dumps(body).encode() if body is not None else None
    last_err: Exception | None = None
    for attempt in range(3):
        req = urllib.request.Request(url, data=data, method=method, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                raw = resp.read().decode()
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            detail = e.read().decode()
            last_err = RuntimeError(f"Places API {path}: {e.code} {detail[:400]}")
            if e.code == 403 and attempt < 2:
                import time

                time.sleep(1.5)
                continue
            raise last_err from e
    raise last_err or RuntimeError(f"Places API {path}: failed")


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


def extract_place_id_from_urls(clinic: dict) -> str | None:
    for field in ("google_place_id", "google_maps_url", "google_review_url"):
        val = clinic.get(field) or ""
        m = PLACE_ID_RE.search(val)
        if m:
            return m.group(1)
    return None


def resolve_place_id(clinic: dict) -> str | None:
    existing = extract_place_id_from_urls(clinic)
    if existing:
        return existing

    query = " ".join(
        p
        for p in [clinic.get("name"), clinic.get("address")]
        if p
    ).strip()
    if not query:
        return None

    mode = detect_api_mode()
    if mode == "legacy":
        data = legacy_get("textsearch", {"query": query, "language": "tr"})
        results = data.get("results") or []
        return results[0].get("place_id") if results else None

    try:
        data = places_request(
            "POST",
            "/places:searchText",
            {"textQuery": query, "languageCode": "tr", "regionCode": "TR"},
            field_mask="places.id,places.displayName,places.rating,places.userRatingCount",
        )
    except RuntimeError:
        # SearchText kapalı key'lerde findplacefromtext dene
        try:
            fp = legacy_get(
                "findplacefromtext",
                {
                    "input": query,
                    "inputtype": "textquery",
                    "fields": "place_id",
                },
            )
            cands = fp.get("candidates") or []
            if cands:
                return cands[0].get("place_id")
        except RuntimeError:
            pass
        return None

    places = data.get("places") or []
    if not places:
        return None
    place_id = (places[0].get("id") or "").replace("places/", "")
    return place_id or None


def normalize_place_id(place_id: str) -> str:
    return place_id.replace("places/", "")


def fetch_place_details(place_id: str) -> dict:
    pid = normalize_place_id(place_id)
    mode = detect_api_mode()
    if mode == "legacy":
        data = legacy_get(
            "details",
            {
                "place_id": pid,
                "fields": "reviews,rating,user_ratings_total,name,url",
                "language": "tr",
            },
        )
        result = data.get("result") or {}
        reviews = []
        for r in result.get("reviews") or []:
            reviews.append(
                {
                    "rating": r.get("rating"),
                    "text": {"text": r.get("text") or ""},
                    "authorAttribution": {"displayName": r.get("author_name") or "Google kullanıcısı"},
                    "name": f"legacy:{r.get('author_name')}:{r.get('time', 0)}",
                }
            )
        return {
            "rating": result.get("rating"),
            "userRatingCount": result.get("user_ratings_total"),
            "reviews": reviews,
            "googleMapsUri": result.get("url"),
        }

    return places_request(
        "GET",
        f"/places/{urllib.parse.quote(pid, safe='')}",
        field_mask="id,rating,userRatingCount,reviews,displayName,googleMapsUri",
    )


def sentiment_from_rating(rating: int) -> str:
    if rating >= 4:
        return "positive"
    if rating == 3:
        return "neutral"
    return "negative"


def review_text(review: dict) -> str:
    text = review.get("text") or {}
    if isinstance(text, dict):
        return (text.get("text") or "").strip()
    return str(text).strip()


def review_author(review: dict) -> str:
    attr = review.get("authorAttribution") or {}
    return (attr.get("displayName") or "Google kullanıcısı").strip()


def review_external_id(review: dict, clinic_id: str, idx: int) -> str:
    name = review.get("name") or ""
    if name:
        return name.split("/reviews/")[-1] if "/reviews/" in name else name
    author = review_author(review)
    text = review_text(review)[:80]
    return f"{clinic_id}:{author}:{review.get('rating', 0)}:{hash(text) & 0xFFFFFFFF:x}"


def upsert_review(clinic_id: str, review: dict, idx: int) -> bool:
    ext_id = review_external_id(review, clinic_id, idx)
    rating = int(review.get("rating") or 0)
    row = {
        "clinic_id": clinic_id,
        "external_review_id": ext_id,
        "author_name": review_author(review),
        "rating": rating,
        "review_text": review_text(review),
        "sentiment": sentiment_from_rating(rating),
        "status": "pending_approval",
    }

    existing = sb_request(
        "GET",
        "google_reviews?"
        + urllib.parse.urlencode(
            {
                "clinic_id": f"eq.{clinic_id}",
                "external_review_id": f"eq.{ext_id}",
                "select": "id,status,draft_reply",
            }
        ),
    )
    if existing:
        # Mevcut kaydı güncelle (metin/puan değişmiş olabilir)
        sb_request(
            "PATCH",
            f"google_reviews?id=eq.{existing[0]['id']}",
            {
                "author_name": row["author_name"],
                "rating": row["rating"],
                "review_text": row["review_text"],
                "sentiment": row["sentiment"],
            },
        )
        return False

    sb_request("POST", "google_reviews", row)
    return True


def sync_clinic(clinic: dict) -> dict:
    clinic_id = clinic["id"]
    name = clinic.get("name") or clinic_id
    print(f"▶ {name}")

    place_id = clinic.get("google_place_id") or resolve_place_id(clinic)
    if not place_id:
        print(f"  ⚠ place_id bulunamadı — google_maps_url veya adres kontrol edin")
        return {"clinic_id": clinic_id, "name": name, "ok": False, "error": "no_place_id"}

    place_id = normalize_place_id(place_id)
    details = fetch_place_details(place_id)
    rating = details.get("rating")
    count = details.get("userRatingCount")
    reviews = details.get("reviews") or []
    if rating is None and not reviews:
        raise RuntimeError("Google place detayı boş döndü — place_id veya API kotası kontrol edin")
    maps_uri = details.get("googleMapsUri")

    patch = {
        "google_place_id": place_id,
        "google_rating": rating,
        "google_review_count": count,
        "google_reviews_synced_at": datetime.now(timezone.utc).isoformat(),
    }
    if maps_uri and not clinic.get("google_maps_url"):
        patch["google_maps_url"] = maps_uri

    sb_request("PATCH", f"clinics?id=eq.{clinic_id}", patch)

    inserted = 0
    for i, review in enumerate(reviews):
        if upsert_review(clinic_id, review, i):
            inserted += 1

    print(f"  ✓ rating={rating} toplam={count} senkron={len(reviews)} yeni={inserted}")
    return {
        "clinic_id": clinic_id,
        "name": name,
        "ok": True,
        "place_id": place_id,
        "rating": rating,
        "total": count,
        "synced": len(reviews),
        "inserted": inserted,
    }


def load_clinics(clinic_id: str | None) -> list[dict]:
    query = (
        "select=id,name,slug,address,google_place_id,google_maps_url,google_review_url,"
        "google_rating,google_review_count&order=name.asc"
    )
    if clinic_id:
        query += f"&id=eq.{clinic_id}"
    rows = sb_request("GET", f"clinics?{query}")
    return rows or []


def main() -> int:
    parser = argparse.ArgumentParser(description="Google Places → Supabase yorum senkronu")
    parser.add_argument("--clinic-id", help="Tek klinik UUID")
    args = parser.parse_args()

    clinics = load_clinics(args.clinic_id)
    if not clinics:
        print("Klinik bulunamadı", file=sys.stderr)
        return 1

    mode = detect_api_mode()
    print(f"Google API modu: {mode}")

    results = []
    for clinic in clinics:
        try:
            results.append(sync_clinic(clinic))
        except Exception as exc:
            print(f"  ✗ {exc}", file=sys.stderr)
            results.append(
                {"clinic_id": clinic.get("id"), "name": clinic.get("name"), "ok": False, "error": str(exc)}
            )

    ok = sum(1 for r in results if r.get("ok"))
    print(f"\n{'═' * 50}")
    print(f"Google senkron: {ok}/{len(results)} klinik başarılı")
    print("Not: Google Places API istek başına en fazla 5 güncel yorum verir.")
    print(f"{'═' * 50}")

    summary_path = Path(__file__).resolve().parent.parent / ".tmp" / "google-reviews-sync.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    if env("OPENAI_API_KEY") and ok > 0:
        print("\nAI taslak yanıtlar üretiliyor…")
        import subprocess

        draft_script = Path(__file__).resolve().parent / "draft-google-reviews.py"
        subprocess.run([sys.executable, str(draft_script)], check=False)

    return 0 if ok == len(results) else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
