#!/usr/bin/env python3
"""Offline GEO + blog kalite birimleri — Vertex/Supabase gerekmez."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "execution"))

from lib.content_quality import (  # noqa: E402
    blog_quality_gate,
    geo_quality_gate,
    looks_bloggy,
    looks_geo_skeleton,
    normalize_geo_links,
)
from lib.topic_picker import pick_blog_topic, pick_geo_topic  # noqa: E402


def _fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    raise SystemExit(1)


def main() -> None:
    hit = looks_bloggy(
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
    if looks_bloggy(good):
        _fail(f"iyi cevap yanlış reddedildi: {looks_bloggy(good)}")

    topic = {"bucket": "problem", "prompt": "test", "internal_path": "/urunler"}
    gate = geo_quality_gate(
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

    links = normalize_geo_links(
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

    # Blog gate: GEO skeleton reject
    skeleton_hit = looks_geo_skeleton(
        "Yerel klinik on-page Geo SEO; şehir+branş başlıkları, answer-first giriş, NAP bloğu."
    )
    if not skeleton_hit:
        _fail("blog GEO iskeleti yakalanmalıydı")

    thin = blog_quality_gate(
        intro="Kısa intro.",
        sections=[{"heading": "A", "body": "Çok kısa."}],
        faq=[{"q": "Soru?", "a": "Evet."}],
        title="Test",
        excerpt="Özet",
    )
    if not thin:
        _fail("ince blog reddedilmeliydi")

    long_sec = (
        "Bu bölümde klinik yöneticisinin uygulayabileceği adımları netleştiriyoruz. "
        "Önce mevcut Google İşletme Profili ve site iletişim bilgilerini yan yana koyun. "
        "Ardından en çok randevu getiren üç hizmet sayfasının ilk paragrafını doğrudan "
        "cevap verecek şekilde yeniden yazın. Son olarak mobil Ara ve Randevu butonlarını "
        "kontrol edin; yavaşlık varsa görselleri sıkıştırın. Haftalık kısa bir kontrol "
        "rutini eklemek, küçük hataların birikmesini engeller ve ekip içi sahipliği netleştirir. "
        "Değişiklikleri yayınladıktan sonra iki hafta boyunca arama tıklama ve arama "
        "gösterim trendini izleyin; düşüş varsa title veya ilk paragrafı yeniden gözden geçirin. "
        "Sahiplik klinik koordinatörde olsun; pazarlama yalnızca metin desteği versin."
    )
    good_blog = blog_quality_gate(
        intro=(
            "Yerel görünürlük için web sitenizin kritik sayfalarını şehir ve hizmet dilinde "
            "düzenlemek gerekir. Amaç jargon değil; hastanın sizi bulması ve güven duymasıdır. "
            "Bu playbook adım adım uygulanabilir bir kontrol listesi sunar; "
            "ekip içinde sahiplik ve haftalık skor rutini olmadan ilerleme rastgele kalır."
        ),
        sections=[
            {"heading": "Başlıkları netleştirin", "body": long_sec},
            {"heading": "İlk paragrafı düzeltin", "body": long_sec},
            {"heading": "SSS ekleyin", "body": long_sec},
            {"heading": "Aylık denetim rutini", "body": long_sec},
        ],
        faq=[
            {
                "q": "Keyword stuffing gerekir mi?",
                "a": "Hayır. Şehir ve hizmet adını doğal yerlerde kullanın; abartı zarar verir.",
            },
            {
                "q": "Hangi sayfalar önce?",
                "a": "Ana sayfa, en çok randevu getiren üç hizmet ve iletişim sayfası.",
            },
            {
                "q": "Ne sıklıkla gözden geçirilmeli?",
                "a": "Ayda bir title ve SSS kontrolü yeterlidir; büyük değişikliklerde hemen bakın.",
            },
        ],
        title="Yerel klinik on-page rehberi",
        excerpt="Şehir ve hizmet odaklı sayfa düzeni için uygulanabilir kontrol listesi.",
    )
    if good_blog:
        _fail(f"iyi blog yanlış reddedildi: {good_blog}")

    # Topic picker diversity
    topics = [
        {"bucket": "problem", "prompt": "A sorusu", "internal_path": "/"},
        {"bucket": "marka", "prompt": "B sorusu", "internal_path": "/"},
        {"bucket": "problem", "prompt": "C sorusu", "internal_path": "/"},
    ]
    picked = pick_geo_topic(
        topics,
        0,
        recent_prompts={"A sorusu"},
        recent_buckets=["problem", "problem", "problem"],
    )
    if picked["prompt"] != "B sorusu":
        _fail(f"bucket dengesi beklenen B, gelen {picked}")

    blog_topics = [
        {"tag": "NPS", "angle": "a"},
        {"tag": "GEO", "angle": "b"},
    ]
    bt = pick_blog_topic(blog_topics, 0, recent_tags={"nps"})
    if bt["tag"] != "GEO":
        _fail(f"blog tag çeşitliliği beklenen GEO, gelen {bt}")

    print("ok: geo + blog quality gates")


if __name__ == "__main__":
    main()
