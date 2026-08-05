# Nefalix SEO/GEO — Repo çapraz kontrolü

**Tarih:** 2026-07-29  
**Kaynak plan:** [`docs/nefalix-seo-geo-ajan-plani.md`](nefalix-seo-geo-ajan-plani.md)  
**Operasyon SOP:** [`directives/geo.md`](../directives/geo.md), [`directives/daily_blog.md`](../directives/daily_blog.md)  
**Ölçüm şablonu:** [`docs/geo-prompt-baseline.md`](geo-prompt-baseline.md)

Bu not, ajan planındaki Faz 0 iddialarını canlı sistemle karşılaştırır. Commit / deploy / Vertex batch bu belgenin parçası değil.

---

## Faz 0 sonucu (indeks boş mu?)

| Yüzey | curl (JS yok) | Canlı API | Sonuç |
|-------|---------------|-----------|--------|
| `/geo` indeks | SSR HTML + `/geo/DATE` linkleri (`action=geo-index`) | `action=geo-list` → ~24 paket | **Crawlable** (2026-07-29 Situation B fix) |
| `/blog` indeks | SSR HTML + `/blog/slug` linkleri (`action=blog-index`) | `action=list` → ~45 yazı | **Crawlable** |
| `/geo/YYYY-MM-DD` | SSR HTML + FAQPage / cevap gövdesi | `geo-render` | **Crawlable** — asıl alıntı yüzeyi OK |
| `/geo-sitemap.xml` / `/blog-sitemap.xml` | 200 | Dinamik | Discovery yolu var |
| GSC indexed mi? | — | Manuel | **Henüz doğrulanmadı** (plan §9) |

**Verdict:** Planın “içerik yok” hipotezi yanlıştı; indeks JS-render riski de **kapatıldı**. `/blog` ve `/geo` artık `api/blog.js` üzerinden SSR (`blog-index` / `geo-index`); `vercel.json` rewrite’ları static shell’e değil bu action’lara gidiyor. Detay sayfalar ve sitemap’ler önceki gibi.

Landing: `nefalix-landing/api/blog.js`, `vercel.json`; şablonlar `blog.html` / `geo.html` (includeFiles).

---

## Mevcut otomasyon (plan §5–8’den önce ne var)

| Parça | Durum |
|-------|--------|
| Günlük blog cron 09:05 | `publish-daily-blog.py` + `directives/daily_blog.md` |
| Günlük GEO cron 09:15 | `publish-daily-geo.py` + `geo-topics.json` |
| Pazar citation hatırlatma | `send-geo-weekly-reminder.py` |
| Public entity | `Nefalix`; FAQPage + VideoObject + `llms.txt` |
| Batch geçmişi | Handoff: 18–27 Temmuz batch canlı |
| Canlı paket aralığı (örnek) | ~2026-07-14 → 2026-08-06 (gelecek tarihli topic’ler de listede) |
| Statik markalı GEO kapak | `assets/geo-branded/geo-cover-*.jpg` **yalnızca 18–27 Temmuz**; sonrası dinamik `action=cover` |

Eksik (plana göre):

- B2B **SoftwareApplication/Product** schema GEO detayda yok (anasayfada `SoftwareApplication` var).
- **Sektör bazlı** (Sağlık / Otel / Oto) keyword haritası ve karşılaştırma sayfaları (`Nefalix vs …`) henüz ürün yüzeyi değil — sadece bu araştırma dokümanında.
- Director / researcher ajan promptları: planda var; `directives/` altında ayrı SOP yok.
- Hukuki checklist (§4: Reklam Kurulu widget, review-gating, KVKK veri sorumlusu/işleyen) içerik kapısında otomatik değil.

---

## Plan fazları → önerilen sıra

1. **Faz 0 teknik:** `/geo` ve `/blog` indeks SSR — **yapıldı**.
2. **Faz 1 araştırma:**
   - Sağlık — **yapıldı** → `research/saglik-sektoru-arastirma.md`
   - Otel — **yapıldı** (2026-07-29) → `research/otel-sektoru-arastirma.md`
   - Oto Servis — **yapıldı** (2026-08-05) → `research/oto-sektoru-arastirma.md`
3. **Faz 2–3 sağlık içerik:** 5 GEO pillar + 1 karşılaştırma canlı (`/geo/...` slug’lar, sitemap) — **yapıldı**; ek vs-sayfaları (Nefalix vs klinikitibar / VoyageRespond) opsiyonel.
4. **Faz 4:** Otel GEO + karşılaştırma seti — **sırada** (otel araştırma tamam); ardından Oto GEO seti (`research/oto-sektoru-arastirma.md` briefleriyle).
5. **Faz 5 ölçüm:** GSC indeks + AI citation testi — GSC URL isteği manuel (API yok).

Director kuralı: `.cursor/rules/nefalix-content-director.mdc` (`geo/**/*.md`, `content/**/*.md`).


---

## Landing repo

Araştırma metni **n8n-repo `docs/`** içinde yaşar. `nefalix-landing` yalnızca public yüzey; tam plan kopyası yok. Uygulama (SSR indeks, schema) landing’de yapılır.
