# Günlük Blog Otomasyonu

## Hedef

Her gün **09:05 (İstanbul)** otomatik:
1. Vertex Gemini ile 1 Türkçe operasyon playbook’u (answer-first intro + H2 + SSS)
2. Kapak + alt görsel
3. Supabase `blog_posts` kaydı → sitede yayın
4. `info@nefalix.com` ile yöneticilere mail

> **Blog ≠ GEO.** Blog uzun rehberdir (`/blog/:slug`). AI alıntı paketi ayrı kanaldır:
> sabah **09:15** `directives/geo.md` → `/geo/YYYY-MM-DD`.
> “GEO” etiketli blog yazısı GEO sayılmaz.

**Cursor / AI açık olması gerekmez.** VPS cron çalıştırır.

- Liste: https://nefalix.com/blog
- Yazı: https://nefalix.com/blog/{slug}
- Site haritası: https://nefalix.com/blog-sitemap.xml

## Akış

```
VPS cron 09:05 Europe/Istanbul
    ↓
python3 -u execution/publish-daily-blog.py
    ↓
Vertex Gemini → JSON (başlık, özet, paragraflar)
    ↓
blog-images.json → cover + footer
    ↓
Supabase blog_posts INSERT
    ↓
SMTP (Hostinger info@nefalix.com) → yöneticiler
```

## Kurulum (tek sefer)

### 1. Migration

```bash
docker exec -i supabase_db_n8n-repo psql -U postgres -d postgres \
  < supabase/migrations/20260709120000_blog_posts.sql
docker exec -i supabase_db_n8n-repo psql -U postgres -d postgres \
  < supabase/migrations/20260709140000_blog_images.sql
```

### 2. Env (VPS `/opt/nefalix/.env`)

```bash
# Zaten var olmalı
SUPABASE_URL=...
SUPABASE_SERVICE_ROLE_KEY=...
GCP_PROJECT_ID=...
GOOGLE_APPLICATION_CREDENTIALS=.tmp/gcp-service-account.json

# Mail (Hostinger)
BLOG_SMTP_HOST=smtp.hostinger.com
BLOG_SMTP_PORT=465
BLOG_SMTP_USER=info@nefalix.com
BLOG_SMTP_FROM=info@nefalix.com
BLOG_SMTP_PASSWORD=...
BLOG_NOTIFY_TO=enes.ceylan190758@gmail.com,akadirysr@gmail.com
```

### 3. Cron kur

```bash
bash execution/setup-blog-cron.sh
```

## Manuel test

```bash
python3 execution/publish-daily-blog.py --dry-run
python3 execution/publish-daily-blog.py
# sadece yazı, mail yok:
python3 execution/publish-daily-blog.py --skip-notify
```

Log: `/var/log/nefalix-blog.log`

## Zamanlanmış yayın (2 saat arayla)

`schedule-blog-batch.py` yazıları **şimdi DB'ye yazar**, `published_at` geleceğe koyar.
Site API `published_at <= now()` filtreler → saat gelince otomatik görünür.
Ayrı cron gerekmez.

```bash
python3 execution/schedule-blog-batch.py --count 3 --interval-hours 2
```

## Edge case

| Durum | Çözüm |
|-------|--------|
| Sabah mail yok | Log'a bak; SMTP şifre / `BLOG_NOTIFY_TO` |
| Cron boş log | `PYTHONUNBUFFERED=1` + hata JSON loglanır |
| `Vertex 401 ACCESS_TOKEN_EXPIRED` | `vertex_gemini` SA JWT ile mint eder (bayat `GCP_ACCESS_TOKEN` kullanmaz). Blog cron **09:05** (saatlik refresh `0 * * * *` sonrası). Gerekirse: `WRITE_GCP_TOKEN_TO_ENV=1 python3 execution/refresh-gcp-access-token.py` |
| Görsel 404 | `execution/blog-images.json` URL'lerini güncelle |
| AI açık değil | Normal — VPS cron bağımsız |

## İlgili dosyalar

| Dosya | Rol |
|-------|-----|
| `execution/publish-daily-blog.py` | Üret + kaydet + mail |
| `execution/send-blog-notification.py` | Hostinger SMTP |
| `execution/setup-blog-cron.sh` | Cron kurulumu |
| `execution/schedule-blog-batch.py` | Toplu / aralıklı yayın |
| `execution/blog-images.json` | Kapak görselleri |
| `nefalix-landing/api/blog.js` | Site API |
| `nefalix-landing/blog.html` | Blog listesi |
