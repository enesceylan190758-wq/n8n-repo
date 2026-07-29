"""Blog ≠ GEO kalite kapıları — publish-daily-* scriptleri paylaşır."""
from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse

SITE = "https://nefalix.com"

ALLOWED_PATHS = {
    "/",
    "/klinik-itibar-yonetimi",
    "/urunler",
    "/urunler#geri-bildirim",
    "/urunler#mesaj",
    "/urunler#yorum-asistani",
    "/urunler#calisan-deneyimi",
    "/urunler#sentinel",
    "/urunler#recall",
    "/fiyatlar",
    "/sektorler",
    "/sektorler#saglik",
    "/sektorler#otel",
    "/sektorler#oto",
    "/platformlar",
    "/blog",
    "/geo",
    "/kaynaklar",
    "/hakkimizda",
    "/ai-ajaniniz",
    "/hbys-entegrasyon",
    "/iys-izin",
    "/veri-guvenligi",
    "/guvenlik-standartlari",
}

# GEO'da yasak: blog/satış dili
GEO_BLOGGY_PATTERNS = [
    r"nefalix\w*\s+.{0,60}kolaylaş",
    r"nefalix(?:ai)?\s+ile\s+(kolaylaş|hızlan|sağlanır|mümkün|optimize)",
    r"nefalix(?:ai)?\s+geo\s+paketi",
    r"entegre\s+çözüm",
    r"çözümleriyle\s+kolaylaş",
    r"hemen\s+(demo|uygula|başla)",
    r"fark\s+yaratın",
    r"okuyar(?:ak)?\s+devam",
    r"\bplaybook\b",
    r"bu\s+rehber",
    r"adım\s+adım\s+bir\s+rehber",
    r"kredi\s+kartı\s+gerekmez",
    r"size\s+özel\s+çözüm",
    r"online\s+itibarınızı\s+güçlendirir",
]

# Blog'da yasak: GEO iskelet jargonu sızıntısı
BLOG_GEO_SKELETON_PATTERNS = [
    r"nap\s+bloğu",
    r"\bfaqpage\b",
    r"answer-first\s+giriş",
    r"şehir\+branş\s+başlıkları",
    r"görünür\s+sss,?\s*nap",
    r"entity(?:'yi|’yi)?\s+güçlendir",
    r"allowlist",
    r"direct_answer",
    r"internal_links",
]


def word_count(text: str) -> int:
    return len(re.findall(r"\w+", text or "", flags=re.UNICODE))


def looks_bloggy(text: str) -> str | None:
    """GEO için blog/satış dili yakala."""
    low = (text or "").lower()
    for pat in GEO_BLOGGY_PATTERNS:
        if re.search(pat, low, flags=re.IGNORECASE):
            return f"blog/satış kalıbı: {pat}"
    if re.match(r"^\s*nefalix(?:ai)?\b.{0,40}\b(kolay|sağlar|sunar|çözüm)", low):
        return "direct_answer ürün CTA ile başlıyor"
    return None


def looks_geo_skeleton(text: str) -> str | None:
    """Blog için GEO-iskelet jargon sızıntısı."""
    low = (text or "").lower()
    for pat in BLOG_GEO_SKELETON_PATTERNS:
        if re.search(pat, low, flags=re.IGNORECASE):
            return f"GEO iskelet jargonu: {pat}"
    return None


def geo_quality_gate(
    topic: dict[str, Any],
    direct: str,
    bullets: list[Any],
    faq: list[Any],
) -> str | None:
    """GEO kalite kapısı. None = geçti."""
    wc = word_count(direct)
    if wc < 35 or wc > 90:
        return f"direct_answer kelime sayısı {wc} (hedef 40-70)"
    blog_hit = looks_bloggy(direct)
    if blog_hit:
        return blog_hit
    if len(bullets) < 3:
        return "bullets < 3"
    for b in bullets:
        if looks_bloggy(str(b)):
            return f"bullet blog dili: {str(b)[:60]}"
    if len(faq) < 3:
        return "faq < 3"
    for item in faq:
        a = str(item.get("a") or item.get("answer") or "")
        if looks_bloggy(a):
            return "faq blog/satış dili"
    bucket = (topic.get("bucket") or "").lower()
    if bucket != "marka":
        nefalix_hits = len(re.findall(r"\bnefalix(?:ai)?\b", direct, flags=re.I))
        if nefalix_hits > 1:
            return "non-marka kovasında fazla Nefalix tekrarı"
    return None


def blog_quality_gate(
    *,
    intro: str,
    sections: list[dict[str, Any]],
    faq: list[Any],
    title: str = "",
    excerpt: str = "",
) -> str | None:
    """Blog kalite kapısı. None = geçti.

    Blog uzun playbook olmalı; kısa GEO iskeleti reddedilir.
    """
    for blob in (intro, title, excerpt):
        hit = looks_geo_skeleton(blob)
        if hit:
            return hit

    if word_count(intro) < 40:
        return f"intro çok kısa ({word_count(intro)} kelime; min 40)"

    if len(sections) < 3:
        return f"sections < 3 ({len(sections)})"

    total_body = word_count(intro)
    for sec in sections:
        heading = str(sec.get("heading") or sec.get("h2") or "")
        body = str(sec.get("body") or sec.get("text") or "")
        hit = looks_geo_skeleton(heading) or looks_geo_skeleton(body)
        if hit:
            return hit
        bw = word_count(body)
        if bw < 60:
            return f"bölüm çok kısa: {heading[:40]} ({bw} kelime; min 60)"
        total_body += bw

    if total_body < 350:
        return f"toplam gövde çok kısa ({total_body} kelime; min 350)"

    if len(faq) < 3:
        return f"faq < 3 ({len(faq)})"

    for item in faq:
        q = str(item.get("q") or item.get("question") or "")
        a = str(item.get("a") or item.get("answer") or "")
        hit = looks_geo_skeleton(q) or looks_geo_skeleton(a)
        if hit:
            return hit
        if word_count(a) < 8:
            return f"faq cevap çok kısa: {q[:40]}"

    return None


def public_geo_url(run_date: str) -> str:
    return f"{SITE}/geo/{run_date}"


def normalize_geo_links(
    raw_links: list[Any],
    topic_path: str,
    run_date: str,
    *,
    extra_urls: list[str] | None = None,
) -> list[str]:
    """Sadece allowlist path + bu günün geo URL'si (+ opsiyonel blog slug URL)."""
    allowed_full = {SITE.rstrip("/") + p for p in ALLOWED_PATHS}
    allowed_full.add(public_geo_url(run_date))
    for u in extra_urls or []:
        if u.startswith("https://nefalix.com/blog/"):
            allowed_full.add(u.rstrip("/"))

    cleaned: list[str] = []
    for item in raw_links or []:
        u = str(item).strip()
        if not u:
            continue
        if u.startswith("/"):
            u = SITE.rstrip("/") + u
        parsed = urlparse(u)
        if parsed.netloc and parsed.netloc not in {
            "nefalix.com",
            "www.nefalix.com",
            "nefalixai.com",
        }:
            continue
        path = parsed.path or "/"
        frag = f"#{parsed.fragment}" if parsed.fragment else ""
        candidate = SITE.rstrip("/") + path + frag
        if candidate in allowed_full or (SITE.rstrip("/") + path) in allowed_full:
            if candidate not in cleaned:
                cleaned.append(candidate)

    musts = [
        public_geo_url(run_date),
        SITE.rstrip("/") + (topic_path if topic_path in ALLOWED_PATHS else "/"),
        f"{SITE}/geo",
        f"{SITE}/blog",
    ]
    for u in extra_urls or []:
        if u.startswith("https://nefalix.com/"):
            musts.append(u.rstrip("/"))
    for must in musts:
        if must not in cleaned:
            cleaned.append(must)
    return cleaned[:8]


def geo_cover_url(prompt: str, bucket: str = "GEO") -> str:
    """Landing cover API — GEO paket OG/kapak."""
    from urllib.parse import urlencode

    q = urlencode(
        {
            "action": "cover",
            "kind": "geo",
            "tag": (bucket or "GEO")[:40],
            "t": (prompt or "GEO")[:120],
            "v": "11",
        }
    )
    return f"{SITE}/api/blog?{q}"
