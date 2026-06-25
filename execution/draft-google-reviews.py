#!/usr/bin/env python3
"""draft_reply boş google_reviews kayıtları için Vertex Gemini taslak yanıt üretir."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request


def env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def sb(method: str, path: str, body: dict | list | None = None) -> object:
    base = env("SUPABASE_URL", "http://127.0.0.1:54321").rstrip("/")
    key = env(
        "SUPABASE_SERVICE_ROLE_KEY",
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0.EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU",
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
    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = resp.read().decode()
        return json.loads(raw) if raw else None


def gemini_draft(clinic_name: str, author: str, rating: int, text: str) -> dict:
    from vertex_gemini import vertex_json

    prompt = f"""Google yorumu için klinik yanıt taslağı yaz.

Klinik: {clinic_name}
Yazar: {author}
Puan: {rating}/5
Yorum: {text}

Kurallar: KVKK uyumlu, teşhis/tedavi iddiası yok, samimi ve profesyonel, max 80 kelime.
Yorum dili ne ise o dilde yanıt ver (TR/EN/AR).

JSON döndür: sentiment (positive/neutral/negative), themes (dizi, Türkçe), draftReply (yanıt metni), urgency (low/medium/high)"""

    return vertex_json(
        prompt,
        system="Sen klinik itibar yöneticisisin. Sadece geçerli JSON döndür.",
    )


def main() -> int:
    clinics = {c["id"]: c["name"] for c in (sb("GET", "clinics?select=id,name") or [])}
    q = (
        "google_reviews?"
        + urllib.parse.urlencode(
            {
                "select": "id,clinic_id,author_name,rating,review_text,draft_reply,status",
                "status": "eq.pending_approval",
                "or": "(draft_reply.is.null,draft_reply.eq.)",
                "order": "created_at.desc",
                "limit": "20",
            }
        )
    )
    reviews = sb("GET", q) or []
    if not reviews:
        print("Taslak bekleyen yorum yok")
        return 0

    done = 0
    for r in reviews:
        if (r.get("draft_reply") or "").strip():
            continue
        clinic = clinics.get(r["clinic_id"], "Klinik")
        print(f"▶ {clinic} · {r.get('author_name')} ★{r.get('rating')}")
        try:
            out = gemini_draft(
                clinic,
                r.get("author_name") or "Hasta",
                int(r.get("rating") or 5),
                r.get("review_text") or "",
            )
            sb(
                "PATCH",
                f"google_reviews?id=eq.{r['id']}",
                {
                    "draft_reply": out.get("draftReply") or out.get("draft_reply", ""),
                    "sentiment": out.get("sentiment"),
                    "themes": out.get("themes", []),
                    "urgency": out.get("urgency", "low"),
                },
            )
            done += 1
            print("  ✓ taslak yazıldı")
        except Exception as exc:
            print(f"  ✗ {exc}", file=sys.stderr)

    print(f"\n{done}/{len(reviews)} yorum için AI taslak üretildi")
    return 0 if done else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
