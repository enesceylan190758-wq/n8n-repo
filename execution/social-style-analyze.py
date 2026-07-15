#!/usr/bin/env python3
"""@nefalix_ referans görsellerini YZ ile analiz et → social-style-guide.json.

Usage:
  python3 execution/social-style-analyze.py
  python3 execution/social-style-analyze.py --provider openai
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REF_DIR = ROOT / "assets" / "social-references"
OUT = ROOT / "execution" / "social-style-guide.json"
sys.path.insert(0, str(ROOT / "execution"))

from vertex_gemini import vertex_vision_json  # noqa: E402

# Her layout tipinden bir temsilci (duplicate dosyalar hariç)
CURATED = [
    "nefalix_final_reviews_v8-f15c8f08-4050-463f-8af6-55b4150dc9b8.png",
    "nefalix_final_wa_v7-9f33979c-c6c7-476c-b21f-d37a6a64967d.png",
    "nefalix_final_vs_v8-f9983383-f318-4668-b998-80661f0dc19a.png",
    "nefalix_final_nps_v6-c449cfb7-251e-431b-9864-7b7522d3627c.png",
    "nefalix_final_automation_v6-0740bc54-b470-4a17-9645-6e993d243133.png",
]

ANALYSIS_PROMPT = """Bu görseller Nefalix (@nefalix_) Instagram feed'indeki GERÇEK referans postlar.
Hepsini karşılaştırarak marka stil rehberi çıkar.

JSON döndür:
{
  "brand": {
    "logo_description": "...",
    "wordmark": "nefalix lowercase mi NEFALIXAI mi?",
    "primary_colors": ["hex veya isim"],
    "background_styles": ["açık beyaz", "koyu gradient", ...],
    "typography": "font stili — serif var mı?",
    "footer_pattern": "..."
  },
  "quality_signals": ["feed kalitesini veren 8-12 madde"],
  "avoid": ["asla yapma listesi — düşük kalite işaretleri"],
  "layout_archetypes": {
    "flow_infographic": {
      "description": "adım adım akış infografik",
      "visual_elements": ["..."],
      "best_for_topics": ["..."],
      "openai_prompt_template": "İngilizce, 200+ kelime, bu layout'u birebir tarif eden şablon — {headline} {subtitle} {steps} placeholder'ları ile"
    },
    "split_ui_photo": {
      "description": "...",
      "visual_elements": ["..."],
      "best_for_topics": ["..."],
      "openai_prompt_template": "..."
    },
    "comparison_table": {
      "description": "Manuel vs Nefalix karşılaştırma tablosu",
      "visual_elements": ["..."],
      "best_for_topics": ["..."],
      "openai_prompt_template": "..."
    }
  },
  "caption_style": {
    "tone": "...",
    "structure": "...",
    "emoji_usage": "..."
  }
}

Kritik: Bu referanslarda koyu lacivert+altın serif tipografi YOK — açık SaaS infografik veya mor gradient tablo var.
openai_prompt_template alanları OpenAI image modeline direkt verilebilecek kadar DETAYLI olsun."""


SYSTEM = (
    "Sen senior brand designer'sın. Instagram feed referanslarını analiz edip "
    "üretim ekibine stil rehberi yazarsın. Sadece geçerli JSON."
)


def openai_vision_json(image_paths: list[Path], prompt: str) -> dict:
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY eksik")
    model = os.environ.get("SOCIAL_OPENAI_VISION_MODEL", "gpt-4o").strip()

    content: list[dict] = [{"type": "text", "text": prompt}]
    for path in image_paths:
        mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
        b64 = base64.standard_b64encode(path.read_bytes()).decode()
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:{mime};base64,{b64}", "detail": "high"},
        })

    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": content},
        ],
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
        "max_tokens": 8192,
    }
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(body).encode(),
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            payload = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"OpenAI vision ({e.code}): {e.read().decode()[:400]}") from e
    return json.loads(payload["choices"][0]["message"]["content"])


def pick_images() -> list[Path]:
    paths: list[Path] = []
    for name in CURATED:
        p = REF_DIR / name
        if p.is_file():
            paths.append(p)
    if paths:
        return paths
    return sorted(REF_DIR.glob("*.png"))[:5]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", choices=["gemini", "openai"], default="gemini")
    parser.add_argument("--output", type=Path, default=OUT)
    args = parser.parse_args()

    images = pick_images()
    if not images:
        raise SystemExit(f"Referans görsel yok: {REF_DIR}")

    if args.provider == "openai":
        guide = openai_vision_json(images, ANALYSIS_PROMPT)
        guide["_analyzed_by"] = "openai"
    else:
        try:
            guide = vertex_vision_json(ANALYSIS_PROMPT, images, system=SYSTEM)
            guide["_analyzed_by"] = "gemini"
        except Exception as e:  # noqa: BLE001
            guide = openai_vision_json(images, ANALYSIS_PROMPT)
            guide["_analyzed_by"] = "openai"
            guide["_fallback_from"] = f"gemini: {e}"

    guide["version"] = 1
    guide["analyzed_at"] = datetime.now(timezone.utc).isoformat()
    guide["reference_images"] = [p.name for p in images]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(guide, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"ok": True, "output": str(args.output), "images": len(images)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
