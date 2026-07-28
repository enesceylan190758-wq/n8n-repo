# Cursor Handoff — Nefalix

**Tarih:** 2026-07-28

## Bu oturum (Google SERP / 3 ajan)

Branch: `cursor/nefalix-serp-gorunurluk-5b76`  
Lead: https://cursor.com/agents/bc-cd41d924-157e-418b-a188-d8bb12955b76  
Brief: `.tmp/nefalix-serp-brief.md` · SOP: `directives/google_serp_visibility.md`

**Verdict:** Site crawlable; kategori sorgusunda yokluk = intent mismatch + entity/host parçalanma + zayıf marka index. GEO ≠ Google SEO.

| Ajan | Bulgu |
|------|--------|
| A Teknik | Host duplikasyonu (nefalix.com / www / nefalixai); title NefalixAI vs schema Nefalix; geo-sitemap HEAD 405; future-dated GEO |
| B SERP | “uygulama” → KYS/App Store; asıl fırsat Q2–Q5 (yazılım/NPS/yorum); rakipler ePrestij, eKlinisyen, Esinix |
| C Patch | Bu repoda geo-topics + v2 title/meta; canlı patch `nefalix-landing` (Vercel) |

## Sonraki (canlı)

1. **nefalix-landing:** host 301 + homepage/`/urunler` title/meta (Nefalix + kategori kelimeleri)
2. GSC: `nefalix.com` sitemap + Coverage; `site:nefalix.com` manuel
3. Opsiyonel: `/klinik-itibar-yonetimi` landing (Ajan B #1)
4. Future GEO tarihlerini düzelt / sitemap filtre
5. Önceki GEO checklist (handoff 2026-07-23) hâlâ açık: prod migration, tek cron yolu, smoke
