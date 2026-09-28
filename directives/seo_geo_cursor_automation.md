# Cursor Automations — Nefalix SEO/GEO (tek operasyon)

**Bu dosya:** Cloud Agent talimatlarının kaynak gerçeği.  
**Cursor Agent instructions:** yalnızca bu dosyayı oku ve uygula (aşağıdaki kısa prompt).

## İki katman (karıştırma)

| Katman | Nerede | Ne yapar | PC / Cursor gerekir mi? |
|--------|--------|----------|-------------------------|
| **A — Günlük yayın + mail** | VPS cron | 09:05 blog, 09:15 GEO, Pazar citation mail | Hayır |
| **B — Strateji / pillar / araştırma** | Bu Cursor Automation | Plan fazları, SERP araştırma, director, `geo/*.md` | Hayır (cloud) |

Katman A SOP: `directives/daily_blog.md`, `directives/geo.md`  
Katman B plan: `docs/nefalix-seo-geo-ajan-plani.md`, `docs/nefalix-seo-geo-gap-notes.md`  
Director: `.cursor/rules/nefalix-content-director.mdc`

**Kural:** Cursor otomasyonu VPS SMTP’nin yerine geçmez. Günlük mail VPS’ten gelir. Bu ajan sabah yayınını **doğgular** ve planı **ilerletir**.

## Her koşuda sıra

1. **Durum oku:** gap notes + plan; `research/` ve `geo/` listesi.
2. **Sabah yayını smoke (Katman A kontrolü):**
   - Bugünün `/geo/YYYY-MM-DD` → 200, cevap + SSS HTML’de var mı
   - `/geo` ve `/blog` indeks **HTML 200** mü (plaintext `yüklenemedi: fetch failed` = 502 — pillar publish yok)
   - Statik pillar `/geo/klinik-itibar-yonetimi-yazilimi` 200 mü
   - Son `/blog` indeksi SSR (curl’de “yükleniyor” yok, yazı veya statik GEO linkleri var)
   - Kırık menü / `Geçersiz tarih` / `Geçersiz action` / 502 varsa önce bunu not et; yeni araştırma PR’ı açma
3. **Strateji teslimatı (Katman B — tek ana iş):**
   - `research/oto-sektoru-arastirma.md` **main’de yoksa** yaz (sağlık/otel formatı, gerçek SERP). **Varsa atla.** Aynı başlıklı açık PR varsa yeni kopya açma.
   - Sonra: otel GEO seti (`geo/*.md` + director + `nefalix-landing/geo-pillars/`)
   - Sonra: oto GEO seti
4. **Director kapısı** — red kuralları director dosyasındaki gibi; Onay/Red + gerekçe.
5. **Çıktı:** commit’lenebilir dosyalar + Open PR; kısa handoff (yapılan / kalan / smoke / risk).

## Yasaklar

- Kaynaksız rakip fiyat/özellik; review-gating dili; KVKK sorumluluk bulanıklığı; kaynaksız istatistik
- `/nav.js` (yok) — `/shared.js` veya inline nav
- `/demo` (404) — Cal.com demo linki
- GSC “dizine ekle” buradan yok — URL listesi yeterli
- Aynı koşuda hem büyük pillar seti hem VPS cron’u “yeniden yazma” — cron’a dokunma unless broken

## Kısa Cursor Agent instructions (kutuya yapıştır)

```
Sen Nefalix SEO/GEO cloud ajanısın. Tek kaynak: directives/seo_geo_cursor_automation.md — oku ve aynen uygula.
Repo: n8n-repo @ main. Plan + gap notes + director + research/ + geo/ orada.
Günlük blog/GEO mail VPS cron’dadır; sen yerine geçme — smoke et, sonra sıradaki strateji fazını bitir.
research/oto-sektoru-arastirma.md main’de varsa oto araştırmasını tekrar yazma; sıradaki iş otel GEO seti.
/geo veya /blog 502 ise yeni pillar PR’ı açma — TLS/proxy notu bırak.
Tahmin yok. Siteyi bozma. Open PR + kısa handoff.
```
