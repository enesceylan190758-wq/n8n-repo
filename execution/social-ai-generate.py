#!/usr/bin/env python3
"""Manus Aşama 1 — GPT-5 metin + Swell CX görsel prompt (logo YOK, overlay sonra)."""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "execution"))

from social_creative_prompt import DEFAULT_LAYOUT, SLUG_LAYOUT, layout_spec, load_benchmarks  # noqa: E402
from social_manus_prompt import COMPOSITION_BY_LAYOUT, build_from_ai_data  # noqa: E402

SYSTEM = """Sen Nefalix (@nefalix_) Instagram kreatif direktörüsün. Referans: @swell_cx Swell CX estetiği.

Manus 2 aşamalı üretim:
- Sen Aşama 1'sin: arka plan görseli için prompt + caption üretirsin.
- Logo Python ile sonra eklenecek — görsel prompt'ta ASLA logo/marka ikonu olmamalı.
- Footer (nefalix.com) Python ile sonra eklenecek — görselde ASLA URL/footer yazma.
- Sol üst 320x120px tamamen boş beyaz alan bırakılacak.
- İnsan figürleri, telefon ekranı mockup'ları, UI panelleri kullanılabilir — gerçekçi, profesyonel.

Swell CX stili: minimal, beyaz zemin, mor-mavi dalga altta, floating UI kartları, sans-serif Türkçe.
Yasak: telefon numarası, sahte logo, NEFALIXAI all-caps, serif poster."""


def sb(method: str, path: str, body: dict | None = None) -> list | dict:
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not key:
        raise SystemExit("SUPABASE_SERVICE_ROLE_KEY eksik")
    base = os.environ.get("SUPABASE_URL", "http://127.0.0.1:54321").rstrip("/")
    if "host.docker.internal" in base:
        base = "http://127.0.0.1:54321"
    url = f"{base}/rest/v1/{path}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        url, data=data, method=method,
        headers={
            "apikey": key, "Authorization": f"Bearer {key}",
            "Content-Type": "application/json", "Prefer": "return=representation",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = resp.read().decode()
        return json.loads(raw) if raw.strip() else {}


def strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", " ", text or "").replace("  ", " ").strip()


def load_post(post_id: str) -> tuple[dict, dict]:
    rows = sb("GET", f"social_posts?id=eq.{post_id}&select=*,social_post_templates(*)&limit=1")
    if not rows:
        raise SystemExit(f"Post yok: {post_id}")
    post = rows[0]
    tpl = post.get("social_post_templates")
    if not tpl:
        raise SystemExit("Şablon yok")
    return post, tpl


def text_models() -> list[str]:
    primary = os.environ.get("SOCIAL_OPENAI_TEXT_MODEL", "gpt-5").strip()
    fallbacks = os.environ.get("SOCIAL_OPENAI_TEXT_FALLBACKS", "gpt-4.1,gpt-4o").split(",")
    out = []
    for m in [primary, *fallbacks]:
        m = m.strip()
        if m and m not in out:
            out.append(m)
    return out


def gpt_json(user_prompt: str) -> dict:
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY eksik")
    errors = []
    for model in text_models():
        body: dict = {
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": user_prompt},
            ],
            "response_format": {"type": "json_object"},
        }
        if not model.startswith("gpt-5"):
            body["temperature"] = float(os.environ.get("SOCIAL_OPENAI_TEMPERATURE", "0.8"))
        if model.startswith("gpt-5"):
            body["max_completion_tokens"] = int(os.environ.get("SOCIAL_GPT5_MAX_TOKENS", "16000"))
        else:
            body["max_tokens"] = 4096

        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=json.dumps(body).encode(), method="POST",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=240) as resp:
                payload = json.loads(resp.read().decode())
            out = json.loads(payload["choices"][0]["message"]["content"])
            out["_model"] = model
            return out
        except Exception as e:  # noqa: BLE001
            detail = e.read().decode()[:250] if isinstance(e, urllib.error.HTTPError) else str(e)
            errors.append(f"{model}: {detail}")
    raise RuntimeError(f"GPT başarısız: {errors}")


def build_prompt(template: dict, benchmarks: dict) -> str:
    slug = template.get("slug", "")
    layout = SLUG_LAYOUT.get(slug, DEFAULT_LAYOUT)
    spec = layout_spec(benchmarks, layout)
    comp_hint = COMPOSITION_BY_LAYOUT.get(layout, "")

    return f"""Nefalix Instagram postu üret (Manus / Swell CX metodu).

Konu: {template.get('eyebrow', '')}
Layout: {layout}
Başlık fikri: {strip_html(template.get('headline_html', ''))}
Alt metin fikri: {template.get('subtitle', '')}
Kompozisyon ipucu: {comp_hint}
Referans: {spec.get('structure', '')}

JSON döndür (image_prompt YAZMA — sistem otomatik Manus şablonundan üretecek):
{{
  "layout": "{layout}",
  "subject": "İngilizce kısa konu (ör: WhatsApp Appointment Reminders)",
  "composition": "İngilizce görsel kompozisyon tarifi",
  "ui_cards": ["Türkçe kart/adım metinleri 4-5 adet"],
  "headline": "güçlü Türkçe başlık (ör: Yorum Toplamak Çok Kolay)",
  "subtitle": "tek cümle Türkçe",
  "caption": "Instagram caption 5-8 satır, info@nefalix.com CTA",
  "hashtags": "#nefalix ile başlayan hashtagler"
}}

ÖNEMLİ: Logo/marka ikonu ve footer URL tarif etme — sol üst ve alt sol overlay ile eklenecek."""


def save(post_id: str, template: dict, ai: dict) -> None:
    rows = sb("GET", f"social_posts?id=eq.{post_id}&select=metadata&limit=1")
    meta = (rows[0].get("metadata") if rows else {}) or {}
    sb("PATCH", f"social_posts?id=eq.{post_id}", {
        "headline": ai.get("headline", ""),
        "caption": ai.get("caption", "").strip(),
        "hashtags": ai.get("hashtags", "").strip(),
        "metadata": {
            **meta,
            "slug": template.get("slug"),
            "ai": {
                "method": "manus",
                "model": ai.get("_model"),
                "layout": ai.get("layout"),
                "subject": ai.get("subject"),
                "composition": ai.get("composition"),
                "ui_cards": ai.get("ui_cards"),
                "headline": ai.get("headline"),
                "subtitle": ai.get("subtitle"),
                "image_prompt": ai.get("image_prompt"),
                "generated_at": datetime.now(timezone.utc).isoformat(),
            },
        },
        "updated_at": datetime.now(timezone.utc).isoformat(),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--post-id", required=True)
    args = parser.parse_args()

    benchmarks = load_benchmarks()
    _, template = load_post(args.post_id)
    layout = SLUG_LAYOUT.get(template.get("slug", ""), DEFAULT_LAYOUT)

    ai = gpt_json(build_prompt(template, benchmarks))
    for k in ("headline", "subtitle", "caption", "hashtags"):
        if not str(ai.get(k, "")).strip():
            raise SystemExit(f"GPT yanıtında {k} eksik")

    ai["layout"] = ai.get("layout") or layout
    ai["image_prompt"] = build_from_ai_data(ai, template)
    save(args.post_id, template, ai)

    print(json.dumps({
        "ok": True,
        "post_id": args.post_id,
        "method": "manus",
        "model": ai.get("_model"),
        "layout": ai["layout"],
        "headline": ai.get("headline"),
        "prompt_len": len(ai["image_prompt"]),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
