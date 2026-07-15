#!/usr/bin/env python3
"""Nefalix sosyal post — GPT creative director prompt builder (shared)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BENCHMARKS_PATH = ROOT / "execution" / "social-benchmarks.json"

VISUAL_LAYER_STACK = """
KATMAN SIRASI (atlama = RED):
① LOGO+MARKA sol üst: mor daire, beyaz N, yeşil nokta, yanında bold lowercase "nefalix"
② HEADLINE bloğu: büyük kalın Türkçe + ince subtitle (sans-serif)
③ ANA GÖRSEL: en geniş alan — infografik / UI mockup / foto / tablo
④ FOOTER en alt sol: globe ikon + nefalix.com (+ ince info@nefalix.com sadece burada)
"""

SLUG_LAYOUT: dict[str, str] = {
    "post_01_brand_hero": "comparison_table",
    "post_02_nps_flow": "flow_infographic",
    "post_03_promoter_rule": "flow_infographic",
    "post_04_sentinel": "comparison_table",
    "post_05_review_assistant": "flow_infographic",
    "post_06_inbox": "split_ui_photo",
    "post_07_recall": "split_ui_photo",
    "post_08_enps": "comparison_table",
    "post_09_kvkk": "comparison_table",
    "post_10_demo_cta": "flow_infographic",
}

DEFAULT_LAYOUT = "flow_infographic"


def load_benchmarks() -> dict:
    if BENCHMARKS_PATH.is_file():
        return json.loads(BENCHMARKS_PATH.read_text(encoding="utf-8"))
    return {}


def layout_spec(benchmarks: dict, layout: str) -> dict:
    return (benchmarks.get("layout_specs") or {}).get(layout) or {}


def build_creative_system() -> str:
    return """Sen dünya standartında B2B SaaS sosyal medya kreatif direktörüsün.

REFERANS FEED'LER (birebir kalite hedefi):
• @nefalix_ — Türkçe klinik itibar/NPS/WhatsApp otomasyonu. Figma kalitesi infografik.
• @swell_cx — Healthcare reputation SaaS. Eğitici carousel, temiz UI, güven veren tipografi.

GÖREV: Nefalix için aynı segmentte, aynı görsel kalitede Instagram/LinkedIn postu tasarla.
Sen metin YAZMAZsin — JSON içinde caption + OpenAI DALL-E için ultra-detaylı image_prompt üretirsin.

YASAK: Generic AI slop, koyu lacivert+altın serif poster, NEFALIXAI all-caps, telefon numarası, logo/footer atlama."""
