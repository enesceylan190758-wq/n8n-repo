# Günlük GEO Otomasyonu

## Hedef

Her gün (İstanbul, Cursor gerekmez):

1. **09:05** — Blog playbook (`publish-daily-blog.py`) → public `/blog/:slug`
2. **09:15** — **GEO paketi** (`publish-daily-geo.py`) → Supabase + **public site** `/geo/YYYY-MM-DD` + mail
3. **Pazar 10:00** — citation ölçüm hatırlatma maili (`send-geo-weekly-reminder.py`)

**Entity adı:** `Nefalix` (schema / llms / mail). UI’da NefalixAI kalabilir.

Alıntı yüzeyleri: ChatGPT, Perplexity, Gemini, Google AI Overviews.

## Blog ≠ GEO (kritik)

| | Blog | GEO |
|---|------|-----|
| URL | `/blog/:slug` | `/geo/YYYY-MM-DD` |
| Biçim | Uzun playbook (H2 + checklist) | Kısa answer-first + 3–5 madde + 3 SSS |
| Amaç | İnsan okur, operasyon uygular | AI motoru alıntılar |
| Dil | Rehber / örnek akış olabilir | Nötr tanım; satış CTA yok |
| Başarı | Yazı 200 + mail | **Public crawlable sayfa** + alıntılanabilir cevap |
| Kalite | `blog_quality_gate` | `geo_quality_gate` |

Ortak lib: `execution/lib/content_quality.py` · konu seçimi: `execution/lib/topic_picker.py`

> **Kritik:** AI motorları yalnızca public crawlable sayfaları alıntılar.
> Supabase + yönetici maili GEO değildir. “GEO” etiketli blog yazısı da GEO değildir.
> Başarı kriteri = `https://nefalix.com/geo/YYYY-MM-DD` 200 + answer-first/SSS + `geo-sitemap.xml` + `llms.txt`.

## Kalite kapısı (`publish-daily-geo.py`)

Üretim sonrası otomatik reddeder / yeniden dener (`retry_log`):

- `direct_answer` ~40–70 kelime (kapı 35–90)
- Blog/satış kalıpları yok (`Nefalix ile kolaylaşır`, playbook, demo CTA…)
- marka kovası dışında en fazla 1× “Nefalix”
- FAQ ≥ 3; bullets ≥ 3
- `internal_links` yalnızca allowlist path (+ ilgili blog slug URL)
- Konu seçimi: son 21 gün prompt tekrarı yok; aynı haftada aynı bucket ≤ 3

## Kapak

`geo_daily_runs.cover_image_url` (migration `20260723120100_geo_daily_runs_cover.sql`).
Günlük publisher `geo_cover_url()` → `/api/blog?action=cover&kind=geo...`.

## Akış

```
VPS cron 09:15 Europe/Istanbul
    ↓
python3 -u execution/publish-daily-geo.py
    ↓
geo-topics.json → topic_picker (çeşitlilik)
    ↓
Vertex Gemini → answer / FAQ / LinkedIn one-liner
    ↓
kalite kapısı (blog dili → retry)
    ↓
Supabase geo_daily_runs INSERT (status=published, cover_image_url)
    ↓
Landing (Vercel) /geo + /geo/:date  ← public crawl surface
    ↓
SMTP → yöneticiler (mailde public_url?v= cache-bust)
```

Public yüzeyler (nefalix-landing):

| URL | Rol |
|-----|-----|
| `/geo` | İndeks listesi |
| `/geo/YYYY-MM-DD` | Günlük paket (answer-first + FAQPage) |
| `/geo-sitemap.xml` | Dinamik sitemap |
| `llms.txt` | AI crawler özeti |

## Tek otomasyon yolu (çift tetik yok)

**Ya crontab ya n8n — ikisi birden değil.**

| Yol | Kurulum | Risk |
|-----|---------|------|
| **A — Cron (önerilen VPS)** | `setup-geo-cron.sh` + `setup-blog-cron.sh` | Basit; VPS `.env` |
| **B — n8n** | `nefalix-19-geo-daily` + `nefalix-18-blog-daily` | Schedule çakışması |

Çift aktif olursa aynı gün iki paket / iki blog riski. Cron kuruyorsan n8n schedule’ı disable et (veya tersi).

## Kurulum (tek sefer)

### 1. Migration

```bash
# Local
docker exec -i supabase_db_n8n-repo psql -U postgres -d postgres \
  < supabase/migrations/20260714160000_geo_daily_runs.sql
docker exec -i supabase_db_n8n-repo psql -U postgres -d postgres \
  < supabase/migrations/20260723120100_geo_daily_runs_cover.sql
docker exec -i supabase_db_n8n-repo psql -U postgres -d postgres \
  < supabase/migrations/20260723120000_geo_citation_scores.sql

# Prod: SQL editor veya proxy’nin desteklediği DDL
```

### 2. Env

Blog ile aynı SMTP + Vertex env. Ek:

```bash
GEO_NOTIFY_TO=enes.ceylan190758@gmail.com,akadirysr@gmail.com
# yoksa BLOG_NOTIFY_TO kullanılır
```

Landing Vercel: `SUPABASE_URL` / `SUPABASE_SERVICE_ROLE_KEY` veya N8N supabase-proxy
(`geo_daily_runs` table okuması gerekli — anon SELECT policy mevcut).

### 3. Cron (yol A)

```bash
bash execution/setup-geo-cron.sh    # 09:15 + Pazar 10:00
bash execution/setup-blog-cron.sh   # 09:05
# n8n-18 / n8n-19 schedule KAPALI olmalı
```

## Manuel test

```bash
python3 execution/publish-daily-geo.py --dry-run
python3 execution/publish-daily-geo.py
python3 execution/publish-daily-geo.py --skip-notify

# Offline kalite birimleri
python3 execution/test-geo-quality.py

# Public smoke
python3 execution/smoke-geo-public.py
```

## Mevcut paketleri yeniden yaz (blog dili temizliği)

SSH gerekmez; `supabase-proxy` üzerinden yazar:

```bash
export NEFALIX_INTERNAL_KEY=...
python3 execution/rewrite-geo-packs.py --dry-run
python3 execution/rewrite-geo-packs.py
# tek gün:
python3 execution/rewrite-geo-packs.py --date 2026-07-20
```

Zayıf Geo SEO **blog** playbook’ları:

```bash
python3 execution/rewrite-geo-seo-blogs.py --dry-run
python3 execution/rewrite-geo-seo-blogs.py
```

Proxy: `POST https://api.nefalixai.com/webhook/nefalix/supabase-proxy` + header `X-Nefalix-Internal-Key`.

Log: `/var/log/nefalix-geo.log`

Mail subject satırında paket adı; body’de **Public URL** zorunlu. CDN/HTML stale ise `?v=` query-bust.

## Tamamlanma kontrol listesi

- [ ] `geo_daily_runs` + `cover_image_url` + `geo_citation_scores` prod’da
- [ ] Tek otomasyon yolu seçili (cron **veya** n8n; ikisi değil)
- [ ] Bugünün URL’si 200: `/geo/YYYY-MM-DD`
- [ ] `/geo` listesinde paket + cover görünüyor
- [ ] `smoke-geo-public.py` yeşil
- [ ] Cevap blog/satış dili değil (kalite kapısı)
- [ ] İç linkler allowlist
- [ ] Pazar maili 25 prompt + DB eksik satır sayısı

## Haftalık ölçüm (citation DB)

Kaynak skorlar: tablo `geo_citation_scores`.  
Şablon: `docs/geo-prompt-baseline.md` (25 prompt listesi).

```bash
python3 execution/record-geo-citation.py --week 2026-W30 --prompt-id 1 \
  --prompt "..." --engine chatgpt --mention --citation-url https://nefalix.com/geo/2026-07-20
python3 execution/record-geo-citation.py --csv .tmp/geo-scores.csv
python3 execution/report-geo-citation.py --week 2026-W30 --format md
```

Pazar maili (`send-geo-weekly-reminder.py`): “25 prompt × 3 motor” + DB’deki eksik satır sayısı.
Ölçümde URL olarak `/geo/YYYY-MM-DD` kullan (GEO etiketli blog slug değil).
ChatGPT/Perplexity otomatik scrape yok (ToS); CLI/CSV ile girilir.

## Edge case

| Durum | Çözüm |
|-------|--------|
| `ACCESS_TOKEN_EXPIRED` | `vertex_gemini` SA mint; blog 09:05 / geo 09:15 |
| Aynı gün çift GEO | `run_date` unique → skip; cron+n8n çiftini kapat |
| Mail yok | `BLOG_SMTP_*` / `GEO_NOTIFY_TO` |
| Paket DB’de var ama site 404 | Landing deploy / proxy; migration VPS’te mi? |
| İçerik blog gibi | Kalite kapısı + `--force` (önce eski satırı sil) |
| Cover yok | migration `cover_image_url`; publisher yeniden çalıştır |
| Landing şema | FAQPage (görünür SSS = schema), SoftwareApplication, BlogPosting, llms.txt |

## İlgili dosyalar

| Dosya | Rol |
|-------|-----|
| `execution/lib/content_quality.py` | GEO + blog kalite kapıları |
| `execution/lib/topic_picker.py` | Prompt/tag çeşitlilik + bucket dengesi |
| `execution/publish-daily-geo.py` | Günlük GEO + kapı + cover + public_url mail |
| `execution/rewrite-geo-packs.py` | Mevcut GEO paketlerini PATCH |
| `execution/rewrite-geo-seo-blogs.py` | 10 Geo SEO blog → playbook |
| `execution/record-geo-citation.py` | Citation skor CLI/CSV |
| `execution/report-geo-citation.py` | Citation özet md/JSON |
| `execution/smoke-geo-public.py` | Public 200 smoke |
| `execution/test-geo-quality.py` | Offline birimler |
| `execution/geo-topics.json` | Alıcı soru bankası |
| `execution/setup-geo-cron.sh` | Cron 09:15 + Pazar 10:00 |
| `execution/send-geo-weekly-reminder.py` | 25 prompt + eksik skor mail |
| `docs/geo-prompt-baseline.md` | 25 prompt şablonu (kaynak = DB) |
| `directives/daily_blog.md` | Blog (ayrı kanal; GEO değil) |
