#!/usr/bin/env python3
"""Inject static SEO meta blocks into Nefalix landing HTML pages."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://nefalix.com"
OG_IMAGE = f"{SITE}/assets/brand/nefalix-logo-512.png"
# google483cdd5223eb8396.html dosyasından (Search Console HTML etiketi)
GOOGLE_SITE_VERIFICATION = "483cdd5223eb8396"

PAGES: dict[str, dict[str, str]] = {
    "index.html": {
        "canonical": "/",
        "description": "Nefalix: klinikler için WhatsApp, NPS, Google yorumları ve hasta geri bildirimi otomasyonu. Estesoft/HBYS entegrasyonu, KVKK uyumlu Türkiye odaklı platform.",
        "og_title": "Nefalix — Yapay Zeka ile Klinik Büyümesi",
    },
    "urunler.html": {
        "canonical": "/urunler",
        "description": "Akıllı geri bildirim, WhatsApp mesaj yönetimi, Google yorum asistanı, çalışan deneyimi, Sentinel itibar koruma ve Recall hasta geri kazanım modülleri.",
        "og_title": "Ürünler — Nefalix",
    },
    "fiyatlar.html": {
        "canonical": "/fiyatlar",
        "description": "Nefalix fiyatlandırma: sektör, şube ve modül bazlı şeffaf paketler. Sağlık, otel ve auto servis için Başlangıç, Pro ve Kurumsal planlar.",
        "og_title": "Fiyatlar — Nefalix",
    },
    "sektorler.html": {
        "canonical": "/sektorler",
        "description": "Sağlık kurumları, oteller ve auto servisler için Nefalix sektör çözümleri: hasta deneyimi, geri bildirim ve büyüme otomasyonu.",
        "og_title": "Sektörler — Nefalix",
    },
    "platformlar.html": {
        "canonical": "/platformlar",
        "description": "WhatsApp, Google, Estesoft/HBYS ve sosyal kanallarla entegre Nefalix platform mimarisi.",
        "og_title": "Platformlar — Nefalix",
    },
    "ai-ajaniniz.html": {
        "canonical": "/ai-ajaniniz",
        "description": "Klinik operasyonlarınız için yapay zeka ajanı: randevu sonrası NPS, yorum yanıtları ve hasta iletişiminde akıllı taslaklar.",
        "og_title": "AI Ajanınız — Nefalix",
    },
    "kaynaklar.html": {
        "canonical": "/kaynaklar",
        "description": "Nefalix blog, rehberler ve kaynaklar: hasta deneyimi, NPS, itibar yönetimi ve klinik büyümesi.",
        "og_title": "Kaynaklar — Nefalix",
    },
    "hakkimizda.html": {
        "canonical": "/hakkimizda",
        "description": "Nefalix ekibi ve misyonu: Türkiye'deki klinikler için KVKK uyumlu hasta deneyimi ve büyüme otomasyonu.",
        "og_title": "Hakkımızda — Nefalix",
    },
    "hbys-entegrasyon.html": {
        "canonical": "/hbys-entegrasyon",
        "description": "Estesoft Stella ve HBYS entegrasyonu: randevu tamamlandığında otomatik NPS, WhatsApp ve dashboard akışları.",
        "og_title": "HBYS Entegrasyonu — Nefalix",
    },
    "guvenlik-standartlari.html": {
        "canonical": "/guvenlik-standartlari",
        "description": "Nefalix güvenlik standartları: veri şifreleme, erişim kontrolü, KVKK ve sağlık verisi işleme ilkeleri.",
        "og_title": "Güvenlik Standartları — Nefalix",
    },
    "en.html": {
        "canonical": "/en",
        "description": "Nefalix: patient engagement and growth automation for clinics — WhatsApp, NPS, Google reviews, HBYS integration.",
        "og_title": "Nefalix — Patient Engagement for Clinics",
    },
    "ar.html": {
        "canonical": "/ar",
        "description": "نيفاليكس: أتمتة تجربة المرضى ونمو العيادات — واتساب، NPS، مراجعات Google وتكامل HBYS.",
        "og_title": "Nefalix — منصة تفاعل المرضى للعيادات",
    },
    "gizlilik-politikasi.html": {
        "canonical": "/gizlilik-politikasi",
        "description": "Nefalix gizlilik politikası ve kişisel verilerin korunması.",
        "og_title": "Gizlilik Politikası — Nefalix",
    },
    "kvkk.html": {
        "canonical": "/kvkk",
        "description": "Nefalix KVKK aydınlatma metni ve veri sorumlusu bilgileri.",
        "og_title": "KVKK Aydınlatma Metni — Nefalix",
    },
    "kullanici-sozlesmesi.html": {
        "canonical": "/kullanici-sozlesmesi",
        "description": "Nefalix kullanıcı sözleşmesi ve hizmet şartları.",
        "og_title": "Kullanıcı Sözleşmesi — Nefalix",
    },
    "veri-guvenligi.html": {
        "canonical": "/veri-guvenligi",
        "description": "Nefalix veri güvenliği, barındırma ve yedekleme politikaları.",
        "og_title": "Veri Güvenliği — Nefalix",
    },
    "iys-izin.html": {
        "canonical": "/iys-izin",
        "description": "Nefalix İYS ve ticari ileti izin yönetimi süreçleri.",
        "og_title": "İYS ve İzin Yönetimi — Nefalix",
    },
}

NOINDEX = {
    "dashboard.html",
    "login.html",
    "demo-entry.html",
    "setup-password.html",
    "landing.html",
    "anasayfa-detayi.html",
}

MARKER_START = "<!-- nefalix-seo-start -->"
MARKER_END = "<!-- nefalix-seo-end -->"


def block_index(cfg: dict[str, str], google_verify: bool = False) -> str:
    url = f"{SITE}{cfg['canonical']}"
    desc = cfg["description"]
    title = cfg["og_title"]
    google_meta = (
        f'<meta name="google-site-verification" content="{GOOGLE_SITE_VERIFICATION}">\n'
        if google_verify
        else ""
    )
    return f"""{MARKER_START}
{google_meta}<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta name="robots" content="index, follow">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Nefalix">
<meta property="og:locale" content="tr_TR">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{OG_IMAGE}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{OG_IMAGE}">
{MARKER_END}"""


def block_noindex() -> str:
    return f"""{MARKER_START}
<meta name="robots" content="noindex, nofollow">
{MARKER_END}"""


def strip_existing(text: str) -> str:
    return re.sub(
        re.escape(MARKER_START) + r".*?" + re.escape(MARKER_END) + r"\n?",
        "",
        text,
        flags=re.DOTALL,
    )


def inject_after_viewport(text: str, block: str) -> str:
    pattern = r'(<meta name="viewport"[^>]*>\n?)'
    if re.search(pattern, text):
        return re.sub(pattern, r"\1" + block + "\n", text, count=1)
    pattern2 = r"(<title>[^<]+</title>\n?)"
    return re.sub(pattern2, block + "\n" + r"\1", text, count=1)


def org_json_ld() -> str:
    return """<!-- nefalix-jsonld-org -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Nefalix",
  "url": "https://nefalix.com",
  "logo": "https://nefalix.com/assets/brand/nefalix-logo-512.png",
  "email": "info@nefalix.com",
  "description": "Klinikler için yapay zeka destekli hasta deneyimi ve büyüme otomasyonu platformu.",
  "areaServed": "TR",
  "sameAs": [
    "https://www.linkedin.com/company/nefalixai/",
    "https://www.instagram.com/nefalixai/"
  ]
}
</script>"""


def main() -> None:
    for name, cfg in PAGES.items():
        path = ROOT / name
        if not path.exists():
            print(f"skip missing {name}")
            continue
        text = strip_existing(path.read_text(encoding="utf-8"))
        text = inject_after_viewport(text, block_index(cfg, google_verify=(name == "index.html")))
        if name == "index.html" and "<!-- nefalix-jsonld-org -->" not in text:
            text = text.replace(MARKER_END + "\n", MARKER_END + "\n" + org_json_ld() + "\n", 1)
        path.write_text(text, encoding="utf-8")
        print(f"indexed {name}")

    for name in NOINDEX:
        path = ROOT / name
        if not path.exists():
            continue
        text = strip_existing(path.read_text(encoding="utf-8"))
        text = inject_after_viewport(text, block_noindex())
        path.write_text(text, encoding="utf-8")
        print(f"noindex {name}")


if __name__ == "__main__":
    main()
