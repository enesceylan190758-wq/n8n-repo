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

> **Kritik:** AI motorları yalnızca public crawlable sayfaları alıntılar.
> Supabase + yönetici maili GEO değildir. “GEO” etiketli blog yazısı da GEO değildir.
> Başarı kriteri = `https://nefalix.com/geo/YYYY-MM-DD` 200 + answer-first/SSS + `geo-sitemap.xml` + `llms.txt`.

## Kalite kapısı (`publish-daily-geo.py`)

Üretim sonrası otomatik reddeder / yeniden dener:

- `direct_answer` 40–70 kelime
- Blog/satış kalıpları yok (`Nefalix ile kolaylaşır`, playbook, demo CTA…)
- marka kovası dışında en fazla 1× “Nefalix”
- FAQ ≥ 3; bullets ≥ 3
- `internal_links` yalnızca allowlist path (uydurma `/klinikler` vb. düşer)

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
kalite kapısı (blog dili → retry)
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

BLOG_SMTP_HOST=smtp.hostinger.com
BLOG_SMTP_PORT=465
BLOG_SMTP_USER=info@nefalix.com
BLOG_SMTP_FROM=info@nefalix.com
BLOG_SMTP_PASSWORD=...
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

# Offline kalite birimleri
python3 execution/test-geo-quality.py

# Public smoke
curl -sI https://nefalix.com/geo
curl -sL -o /dev/null -w '%{http_code}\n' https://nefalix.com/geo/$(date +%F)
curl -sL https://nefalix.com/api/geo/list?limit=3
curl -sL https://nefalix.com/geo-sitemap.xml | head
curl -sL https://nefalix.com/llms.txt | head
# Stil kırığı (shared.css 404) — directives/site_assets.md
python3 execution/smoke-site-assets.py
```

## Mevcut paketleri yeniden yaz (blog dili temizliği)

SSH gerekmez; Vercel/landing ile aynı DB’ye `supabase-proxy` üzerinden yazar:

```bash
export NEFALIX_INTERNAL_KEY=...   # VPS / Vercel ile aynı
python3 execution/rewrite-geo-packs.py --dry-run
python3 execution/rewrite-geo-packs.py
# tek gün:
python3 execution/rewrite-geo-packs.py --date 2026-07-20
```

Proxy: `POST https://api.nefalixai.com/webhook/nefalix/supabase-proxy` + header `X-Nefalix-Internal-Key`.

Log: `/var/log/nefalix-geo.log`

Mail subject satırında paket adı; body’de **Public URL** zorunlu.

## Tamamlanma kontrol listesi

- [ ] `geo_daily_runs` migration prod’da
- [ ] VPS’te `setup-geo-cron.sh` kurulu (09:15)
- [ ] Bugünün URL’si 200: `/geo/YYYY-MM-DD`
- [ ] `/geo` listesinde paket görünüyor (`/api/geo/list`)
- [ ] `geo-sitemap.xml` + `llms.txt` 200
- [ ] Cevap blog/satış dili değil (kalite kapısı)
- [ ] İç linkler 404 değil (allowlist)
- [ ] Pazar citation baseline dolduruluyor (`docs/geo-prompt-baseline.md`)

## Haftalık ölçüm

`docs/geo-prompt-baseline.md` — 25 sabit prompt.

Her satır: motor · mention · URL · rakip. İlk sürüm manuel; Pazar maili hatırlatır.
Ölçümde URL olarak `/geo/YYYY-MM-DD` kullan (GEO etiketli blog slug değil).

## Edge case

| Durum | Çözüm |
|-------|--------|
| `ACCESS_TOKEN_EXPIRED` | `vertex_gemini` SA mint; blog 09:05 / geo 09:15 |
| Aynı gün çift GEO | `geo_daily_runs` run_date unique → skip |
| Mail yok | `BLOG_SMTP_*` / `GEO_NOTIFY_TO` |
| Paket DB’de var ama site 404 | Landing deploy / proxy; migration VPS’te mi? |
| Site düz HTML / stil yok | `shared.css` 404 — `directives/site_assets.md` + Mac hotfix |
| İçerik blog gibi | Kalite kapısı + prompt; `--force` ile yeniden üret (unique: önce eski satırı sil) |
| Landing şema | FAQPage (görünür SSS = schema), SoftwareApplication, BlogPosting, llms.txt |

## İlgili dosyalar

| Dosya | Rol |
|-------|-----|
| `execution/publish-daily-geo.py` | Günlük GEO paketi + kalite kapısı + public_url mail |
| `execution/rewrite-geo-packs.py` | Mevcut paketleri GEO formatına PATCH (proxy) |
| `execution/test-geo-quality.py` | Offline kalite birimleri |
| `execution/geo-topics.json` | Alıcı soru bankası |
| `execution/setup-geo-cron.sh` | Cron 09:15 + Pazar 10:00 |
| `execution/send-geo-weekly-reminder.py` | Citation checklist mail |
| `docs/geo-prompt-baseline.md` | 25 prompt skor şablonu |
| `directives/daily_blog.md` | Blog (ayrı kanal; GEO değil) |
| `nefalix-landing/api/blog.js` | Public GEO list / render / sitemap (geo-* actions) |
| `nefalix-landing/geo.html` | İndeks sayfası |
| `nefalix-landing/llms.txt` | AI crawler özeti |
