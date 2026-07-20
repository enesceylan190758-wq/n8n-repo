#!/usr/bin/env python3
"""Offline GEO kalite birimleri — Vertex/Supabase gerekmez."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    raise SystemExit(1)


def load_mod():
    path = ROOT / "execution" / "publish-daily-geo.py"
    spec = importlib.util.spec_from_file_location("pub_geo", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    # Avoid executing vertex import side effects? vertex_gemini is imported at module level.
    # Stub vertex_gemini before load if missing deps — file only needs helpers for this test.
    sys.path.insert(0, str(ROOT / "execution"))
    spec.loader.exec_module(mod)
    return mod


def main() -> None:
    mod = load_mod()

    hit = mod.looks_bloggy(
        "Klinikler için haftalık citation ölçümü, Nefalix ile kolaylaşır ve optimize edilir."
    )
    if not hit:
        _fail("sales opening yakalanmalıydı")

    good = (
        "Haftalık citation ölçümü, sabit bir prompt listesini her hafta ChatGPT, Perplexity "
        "ve Gemini üzerinde aynı sırayla sorup marka mention ile URL citation kaydetmektir. "
        "Skor, mention veya citation içeren cevap sayısının prompt çarpı motor sayısına "
        "oranıdır; sonuçlar rakip notlarıyla birlikte haftalık tabloya işlenir."
    )
    if mod.looks_bloggy(good):
        _fail(f"iyi cevap yanlış reddedildi: {mod.looks_bloggy(good)}")

    topic = {"bucket": "problem", "prompt": "test", "internal_path": "/urunler"}
    gate = mod.quality_gate(
        topic,
        good,
        ["Prompt listesini sabitle", "Üç motorda sor", "Mention/citation işaretle"],
        [
            {"q": "Hangi motorlar?", "a": "ChatGPT, Perplexity, Gemini."},
            {"q": "Ne sıklıkla?", "a": "Haftada bir, aynı prompt setiyle."},
            {"q": "Ne kaydedilir?", "a": "Mention, citation URL ve rakip notu."},
        ],
    )
    if gate:
        _fail(f"iyi paket reddedildi: {gate}")

    links = mod.normalize_links(
        [
            "https://nefalix.com/klinikler",
            "https://evil.example/x",
            "https://nefalix.com/urunler",
        ],
        "/urunler",
        "2026-07-20",
    )
    if any("klinikler" in u or "evil" in u for u in links):
        _fail(f"allowlist dışı link kaldı: {links}")
    if "https://nefalix.com/geo/2026-07-20" not in links:
        _fail("günün geo URL'si zorunlu")
    if "https://nefalix.com/urunler" not in links:
        _fail("topic path zorunlu")

    print("ok: geo quality gates")


if __name__ == "__main__":
    main()
