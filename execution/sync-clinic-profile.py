#!/usr/bin/env python3
"""medidentistanbul.com profil ve web yorumlarını Supabase clinics tablosuna yazar."""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from html import unescape

CLINIC_ID = "51738ea8-c12e-40ce-a0e2-42869496d76b"
WEBSITE = "https://medidentistanbul.com"
REVIEWS_URL = f"{WEBSITE}/musteri-yorumlari/"
SIKAYETVAR_URL = "https://www.sikayetvar.com/ozel-medident-agiz-ve-dis-sagligi-poliklinigi"
GOOGLE_MAPS_URL = (
    "https://www.google.com/maps/search/?api=1&query="
    + urllib.parse.quote("Medident İstanbul Acıbadem Cd 195F Üsküdar")
)

REVIEW_KEYWORDS = ("teşekkür", "memnun", "tavsiye", "hocam", "klinik", "medident", "levent", "abdülkadir")
SKIP_KEYWORDS = ("hastalarımıza her türlü", "ağız ve diş sağlığı hizmetini sunabilmek")


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "NefalixClinicSync/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", "ignore")


def parse_json_ld(html: str) -> dict:
    for block in re.findall(
        r'<script[^>]+type="application/ld\+json"[^>]*>(.*?)</script>',
        html,
        re.S | re.I,
    ):
        try:
            data = json.loads(block.strip())
        except json.JSONDecodeError:
            continue
        graph = data.get("@graph", [data])
        for node in graph:
            if node.get("@type") == "Organization":
                return node
    return {}


def scrape_website_reviews(html: str) -> list[str]:
    quotes = re.findall(r">([^<]{60,350})<", html)
    out: list[str] = []
    for q in quotes:
        text = unescape(q.strip())
        low = text.lower()
        if any(s in low for s in SKIP_KEYWORDS):
            continue
        if not any(k in low for k in REVIEW_KEYWORDS):
            continue
        if text.startswith("http") or "function" in text:
            continue
        if text not in out:
            out.append(text)
    return out


def supabase_request(method: str, path: str, body: dict | list | None = None) -> object:
    base = os.environ.get("SUPABASE_URL", "http://127.0.0.1:54321").rstrip("/")
    key = os.environ.get(
        "SUPABASE_SERVICE_ROLE_KEY",
        os.environ.get(
            "SUPABASE_ANON_KEY",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0.EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU",
        ),
    )
    url = f"{base}/rest/v1/{path}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        detail = e.read().decode()
        raise RuntimeError(f"{method} {path}: {e.code} {detail}") from e


def main() -> int:
    print("Fetching", WEBSITE)
    home = fetch(WEBSITE)
    org = parse_json_ld(home)
    logo = (org.get("logo") or {}).get("url") if isinstance(org.get("logo"), dict) else org.get("logo")
    name = org.get("name") or "Medident İstanbul"

    print("Fetching reviews page")
    reviews_html = fetch(REVIEWS_URL)
    website_reviews = scrape_website_reviews(reviews_html) or scrape_website_reviews(home)
    print(f"Found {len(website_reviews)} website review(s)")

    patch = {
        "name": name.replace(" - Diş Sağlığı Merkezi", "").strip(),
        "logo_url": logo or f"{WEBSITE}/wp-content/uploads/2021/07/cropped-MediDent_pdf.png",
        "website_url": WEBSITE,
        "email": "info@medidentistanbul.com",
        "address": "Acıbadem, Acıbadem Cd. 195F, 34718 Üsküdar/İstanbul",
        "whatsapp_phone": "+905491190819",
        "booking_url": f"{WEBSITE}/iletisim/",
        "google_maps_url": GOOGLE_MAPS_URL,
        "google_review_url": GOOGLE_MAPS_URL,
        "trustpilot_url": None,
        "sikayetvar_url": SIKAYETVAR_URL,
        "website_reviews_url": REVIEWS_URL,
        "complaint_form_url": SIKAYETVAR_URL,
    }

    supabase_request("PATCH", f"clinics?id=eq.{CLINIC_ID}", patch)
    print("Updated clinic profile")

    for content in website_reviews:
        existing = supabase_request(
            "GET",
            "reputation_mentions?"
            + urllib.parse.urlencode(
                {
                    "clinic_id": f"eq.{CLINIC_ID}",
                    "source": "eq.website",
                    "content": f"eq.{content}",
                    "select": "id",
                }
            ),
        )
        if existing:
            continue
        supabase_request(
            "POST",
            "reputation_mentions",
            {
                "clinic_id": CLINIC_ID,
                "source": "website",
                "url": REVIEWS_URL,
                "content": content,
                "sentiment": "positive",
                "risk_score": 5,
                "is_critical": False,
            },
        )
        print("Inserted website review:", content[:60], "...")

    print("Done.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
