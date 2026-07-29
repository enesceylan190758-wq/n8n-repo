# Günlük GEO Otomasyonu

## Hedef

Her gün (İstanbul, Cursor gerekmez):

1. **09:05** — GEO formatlı blog yazısı (`publish-daily-blog.py`) → public `/blog/:slug`
2. **09:15** — 1 alıcı sorusu için GEO paketi (`publish-daily-geo.py`) → Supabase + **public site** `/geo/YYYY-MM-DD` + mail
3. **Pazar 10:00** — citation ölçüm hatırlatma maili (`send-geo-weekly-reminder.py`)

**Entity adı:** `Nefalix` (schema / llms / mail). UI’da NefalixAI kalabilir.

Alıntı yüzeyleri: ChatGPT, Perplexity, Gemini, Google AI Overviews.

> **Kritik:** AI motorları yalnızca public crawlable sayfaları alıntılar.
> Supabase + yönetici maili GEO değildir. Başarı kriteri = `https://nefalix.com/geo/YYYY-MM-DD` 200 + cevap/SSS içeriği.

> **İndeks notu (2026-07-29):** `/geo` ve `/blog` listeleri client-side hydrate (`geo-list.js` / `blog-kaynaklar.js`); curl’de «yükleniyor…» kalır. Detay `/geo/YYYY-MM-DD` SSR + FAQPage. Strateji / sektör araştırması + director prompt: `docs/nefalix-seo-geo-ajan-plani.md`. Çapraz kontrol: `docs/nefalix-seo-geo-gap-notes.md`.

## Akış

```
VPS cron 09:15 Europe/Istanbul
    ↓
python3 -u execution/publish-daily-geo.py
    ↓
geo-topics.json → sıradaki alıcı sorusu
    ↓
Vertex Gemini → answer / FAQ / LinkedIn one-liner
    ↓
Supabase geo_daily_runs INSERT (status=published)
    ↓
Landing (Vercel) /geo + /geo/:date  ← public crawl surface
    ↓
SMTP → yöneticiler (mailde public_url)
```

Public yüzeyler (nefalix-landing):

| URL | Rol |
|-----|-----|
| `/geo` | İndeks listesi |
| `/geo/YYYY-MM-DD` | Günlük paket (answer-first + FAQPage) |
| `/geo-sitemap.xml` | Dinamik sitemap |
| `llms.txt` | AI crawler özeti |

## Kurulum (tek sefer)

### 1. Migration

```bash
# Local
docker exec -i supabase_db_n8n-repo psql -U postgres -d postgres \
  < supabase/migrations/20260714160000_geo_daily_runs.sql

# VPS (prod Supabase URL varsa REST migration veya SQL editor)
```

### 2. Env

Blog ile aynı SMTP + Vertex env. Ek:

```bash
GEO_NOTIFY_TO=enes.ceylan190758@gmail.com,akadirysr@gmail.com
# yoksa BLOG_NOTIFY_TO kullanılır
```

Landing Vercel: `SUPABASE_URL` / `SUPABASE_SERVICE_ROLE_KEY` veya N8N supabase-proxy
(`geo_daily_runs` table okuması gerekli — anon SELECT policy mevcut).

### 3. Cron

```bash
bash execution/setup-geo-cron.sh
```

Blog cron ayrıca:

```bash
bash execution/setup-blog-cron.sh   # 09:05
```

## Manuel test

```bash
python3 execution/publish-daily-geo.py --dry-run
python3 execution/publish-daily-geo.py
python3 execution/publish-daily-geo.py --skip-notify
python3 execution/send-geo-weekly-reminder.py --dry-run

# Public smoke
curl -sI https://nefalix.com/geo
curl -sI https://nefalix.com/geo/$(date +%F)
```

Log: `/var/log/nefalix-geo.log`

Mail subject satırında paket adı; body’de **Public URL** zorunlu.

## Haftalık ölçüm

`docs/geo-prompt-baseline.md` — 25 sabit prompt.

Her satır: motor · mention · URL · rakip. İlk sürüm manuel; Pazar maili hatırlatır.
Ölçümde URL olarak `/geo/YYYY-MM-DD` veya ilgili blog slug kullan.

## Edge case

| Durum | Çözüm |
|-------|--------|
| `ACCESS_TOKEN_EXPIRED` | `vertex_gemini` SA mint; blog 09:05 / geo 09:15 |
| `Unterminated string` / JSON parse | `responseSchema` + `parse_json_relaxed` + 5 retry; log: `/var/log/nefalix-geo.log` |
| Blog patladı GEO çalıştı | Blog daha uzun JSON; GEO kısa — ayrı log takibi |
| Aynı gün çift GEO | `geo_daily_runs` run_date unique → skip (`--force` ile yeniden) |
| Mail yok | `BLOG_SMTP_*` / `GEO_NOTIFY_TO` |
| Paket DB’de var ama site 404 | Landing deploy / proxy; migration VPS’te mi? |
| YouTube embed yok | `youtube_video_id` kolonu + `pick_youtube_video`; backfill: `execution/backfill-youtube-ids.py` |
| Landing şema | FAQPage (görünür SSS = schema), VideoObject, llms.txt |

## İlgili dosyalar

| Dosya | Rol |
|-------|-----|
| `execution/publish-daily-geo.py` | Günlük GEO paketi + public_url mail |
| `execution/geo-topics.json` | Alıcı soru bankası |
| `execution/pick_youtube_video.py` | Konuya video eşlemesi |
| `execution/youtube-videos.json` | @Nefalixai video kataloğu |
| `execution/setup-geo-cron.sh` | Cron 09:15 + Pazar 10:00 |
| `execution/send-geo-weekly-reminder.py` | Citation checklist mail |
| `docs/geo-prompt-baseline.md` | 25 prompt skor şablonu |
| `docs/nefalix-seo-geo-ajan-plani.md` | B2B sektör araştırması + ajan mimarisi + director prompt |
| `docs/nefalix-seo-geo-gap-notes.md` | Plan ↔ canlı sistem gap / Faz 0 |
| `directives/daily_blog.md` | Blog (GEO gövde) |
| `nefalix-landing/api/blog.js` | Public GEO list / render / sitemap (geo-* actions) |
| `nefalix-landing/geo.html` | İndeks sayfası (JS hydrate — SSR backlog) |
| `nefalix-landing/llms.txt` | AI crawler özeti |
