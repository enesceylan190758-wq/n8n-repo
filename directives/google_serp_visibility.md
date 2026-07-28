# Google SERP Görünürlük — Nefalix

## Hedef

Kategori/ticari sorgularda (`klinik itibar yönetimi yazılımı`, WhatsApp NPS, Google yorum) Nefalix’in **index + snippet** sinyallerini güçlendirmek. Ranking #1 vaat edilmez; marka sorgusu ve doğru intent eşleşmesi öncelik.

**Lead brief:** `.tmp/nefalix-serp-brief.md` (2026-07-28 ajan koşusu).

## Kritik ayrım

| Yanlış varsayım | Gerçek |
|-----------------|--------|
| Site kırık / robots blok | Site 200; robots Allow; sitemap/llms var |
| GEO günlük paket = Google SEO | GEO = AI alıntı yüzeyi; klasik SERP için ticari landing/meta lazım |
| “uygulama” = bizim ürün | TR’de çoğu zaman App Store / HBYS/KYS (Medibulut vb.) |

## Entity / marka kuralı

- **Kanonik entity:** `Nefalix` (schema, og, llms.txt, `<title>`, mail)
- **UI:** logo/ürün hattında `NefalixAI` kalabilir
- Aynı içeriği 4 host’ta sunma: `nefalix.com` primary; `www` + `nefalixai.com` → **301** apex

## Hedef sorgular

1. `klinik itibar yönetimi yazılımı` (birincil ticari)
2. `hasta memnuniyet yazılımı klinik`
3. `Google yorum yönetimi klinik`
4. `WhatsApp NPS klinik`
5. `klinik itibar uygulaması` (dikkat: App Store intent — copy’de “web yazılım / platform” ayır)
6. `Nefalix` / `NefalixAI` (marka)
7. `site:nefalix.com` (coverage)

## P0 teknik (landing / Vercel — `nefalix-landing`)

1. Host 301: www + nefalixai → `https://nefalix.com`
2. `<title>` / og hizası → **Nefalix** + kategori kelimeleri
3. `/urunler` title/H1/meta: “klinik itibar / hasta memnuniyet yazılımı”
4. geo/blog sitemap `HEAD` → 200
5. Sitemap’e **future-dated** `/geo/YYYY-MM-DD` koyma

## Bu repoda (n8n-repo)

| Dosya | Rol |
|-------|-----|
| `execution/geo-topics.json` | Q1–Q5 ticari prompt’lar + NefalixAI marka netleştirme |
| `nefalix-site-v2/index.html` / `urunler.html` | Title/meta/H1 senkron iskelet (canlı SEO asıl Vercel landing’de) |
| `docs/geo-prompt-baseline.md` | Citation ölçüm şablonu |
| `directives/geo.md` | GEO ≠ klasik SEO |

## Ölçüm

- GSC: property `nefalix.com`, sitemap submit, Coverage
- Marka: `Nefalix` 1. sayfa
- Haftalık: `docs/geo-prompt-baseline.md` + `record-geo-citation.py`

## Edge case

| Durum | Çözüm |
|-------|--------|
| “uygulama” SERP’te KYS | Landing’de “App Store klinik yönetim değil; itibar/NPS katmanı” |
| Repo patch canlıya gitmedi | `nefalix-landing` deploy; v2 yalnız mirror |
| Future GEO tarihleri | Publisher `run_date` ≤ today; sitemap filtre |
| Çift host index | 301 + GSC preferred domain |

## İlgili

- Brief: `.tmp/nefalix-serp-brief.md`
- GEO: `directives/geo.md`
- Smoke: `execution/smoke-geo-public.py`
