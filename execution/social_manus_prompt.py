#!/usr/bin/env python3
"""Manus / Swell CX görsel prompt şablonu — logo YZ'de değil, Python overlay'de."""
from __future__ import annotations

from social_creative_prompt import DEFAULT_LAYOUT, SLUG_LAYOUT, layout_spec, load_benchmarks

MANUS_TEMPLATE = (
    'Professional Instagram social media post background for Nefalix. '
    'Style: Swell CX aesthetic, clean, modern, white background with soft purple-blue '
    'gradient wave at the bottom. '
    'Subject: {subject}. '
    'Composition: {composition}. '
    'Floating white UI cards with rounded corners and subtle drop shadow. '
    'UI cards in TURKISH: {ui_cards}. '
    'Title in bold Turkish sans-serif: "{headline}". '
    'Subtitle in Turkish: "{subtitle}". '
    'Use realistic human figures, phone/tablet screen mockups, and floating UI panels '
    'where they fit the subject — professional stock-photo quality, not cartoon. '
    'IMPORTANT: NO LOGO in top left — keep top-left 320x120px clean white empty space. '
    'IMPORTANT: NO website URL, NO footer text, NO nefalix.com anywhere — footer is added '
    'by brand overlay after generation. No fake logos anywhere. '
    'High quality, seamless SaaS healthcare marketing design, square 1024x1024.'
)

COMPOSITION_BY_LAYOUT = {
    "flow_infographic": (
        "Vertical numbered step infographic on the right with colored circle icons and "
        "connecting arrows; large headline block on the left; subtle dotted decorative line"
    ),
    "split_ui_photo": (
        "Circular cutout photo of smiling dental clinic professional on the right; "
        "realistic WhatsApp chat bubble mockup on the left with green send button"
    ),
    "comparison_table": (
        "Centered three-column comparison table: features | MANUEL (gray X marks) | "
        "NEFALIX (purple highlight column with checkmarks); dark purple-blue gradient "
        "background with soft glow; headline below table"
    ),
}


def default_ui_cards(template: dict, layout: str) -> list[str]:
    badges = template.get("badges") or []
    if isinstance(badges, str):
        import json
        badges = json.loads(badges)
    if badges:
        return [str(b) for b in badges[:4]]
    if layout == "flow_infographic":
        return ["1. Otomatik Tetikleme", "2. Hasta Yanıtlar", "3. Akıllı Yönlendirme", "4. Google Yorumu"]
    return []


def build_manus_image_prompt(
    *,
    subject: str,
    headline: str,
    subtitle: str,
    composition: str,
    ui_cards: list[str],
) -> str:
    cards = ", ".join(f'"{c}"' for c in ui_cards[:5]) if ui_cards else '"Adım 1", "Adım 2", "Adım 3"'
    return MANUS_TEMPLATE.format(
        subject=subject,
        composition=composition,
        ui_cards=cards,
        headline=headline.replace('"', "'"),
        subtitle=subtitle.replace('"', "'"),
    )


def build_from_ai_data(data: dict, template: dict) -> str:
    layout = data.get("layout") or SLUG_LAYOUT.get(template.get("slug", ""), DEFAULT_LAYOUT)
    benchmarks = load_benchmarks()
    spec = layout_spec(benchmarks, layout)

    subject = (data.get("subject") or template.get("eyebrow") or "Healthcare clinic automation").strip()
    composition = (
        data.get("composition")
        or COMPOSITION_BY_LAYOUT.get(layout)
        or spec.get("structure", COMPOSITION_BY_LAYOUT["flow_infographic"])
    )
    ui_cards = data.get("ui_cards") or data.get("flow_steps") or default_ui_cards(template, layout)
    if isinstance(ui_cards, str):
        ui_cards = [ui_cards]

    return build_manus_image_prompt(
        subject=subject,
        headline=str(data.get("headline", "")).strip(),
        subtitle=str(data.get("subtitle", "")).strip(),
        composition=str(composition).strip(),
        ui_cards=[str(c) for c in ui_cards],
    )
