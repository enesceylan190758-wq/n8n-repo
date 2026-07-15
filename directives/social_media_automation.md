# Sosyal Medya Otomasyonu (Instagram + LinkedIn — onaylı otomatik)

> Sistem üretir → size mail/WhatsApp ile onay sorar → onaylayınca IG + LinkedIn'e otomatik yayınlar.

## Hedef

Her gün **09:30 (İstanbul)**:
1. Şablon sırasıyla konu seç → **GPT-5 metin** (caption, headline, Manus alanları) → **gpt-image-2** arka plan (logo yok)
2. **Pillow overlay** — gerçek logo + wordmark + tek footer `nefalix.com`
3. Supabase Storage'a yükle (public URL)
4. `pending_approval` olarak kaydet
5. Yöneticilere **Onayla / Reddet** linki gönder
6. Onay → Instagram + LinkedIn API ile yayın

**Cursor / AI açık olması gerekmez.** VPS cron çalıştırır.

## Akış

```
VPS cron 09:30 Europe/Istanbul
    ↓
python3 -u execution/publish-daily-social.py
    ↓
social-generate-next.py → social-ai-generate.py (GPT-5)
    → render-social-image.py (gpt-image-2 → _raw.png)
    → social-brand-overlay.py (logo + wordmark) → final PNG
    → Storage upload
    ↓
Supabase social_posts (pending_approval)
    ↓
send-social-notification.py → mail + WhatsApp
    ↓
Siz: Onayla linki (nefalix.com/api/social/approve?token=...)
    ↓
Vercel api/social.js → approved
    ↓
VPS webhook → social-publish-approved.py
    ↓
Instagram Graph API + LinkedIn UGC API
```

n8n wf-17 **ana motor değil** (`executeCommand` desteklenmiyor, kapalı bırakın).

## Kurulum (tek sefer)

### 1. Migration

```bash
docker exec -i supabase_db_n8n-repo psql -U postgres -d postgres \
  < supabase/migrations/20260629130000_social_posts.sql
docker exec -i supabase_db_n8n-repo psql -U postgres -d postgres \
  < supabase/migrations/20260629140000_social_posts_ready_status.sql
docker exec -i supabase_db_n8n-repo psql -U postgres -d postgres \
  < supabase/migrations/20260710100000_social_images_storage.sql
```

### 2. Referans stil analizi (tek sefer + yeni görsel eklenince)

```bash
# assets/social-references/ altına @nefalix_ örnek PNG'leri koy
python3 execution/social-style-analyze.py   # Gemini vision → social-style-guide.json
```

### 3. Env (VPS `/opt/nefalix/.env`)

```bash
# Üretim — Manus 2 aşama: GPT görsel (logo yok) + Pillow logo overlay
SOCIAL_TEXT_PROVIDER=openai
SOCIAL_OPENAI_TEXT_MODEL=gpt-5
SOCIAL_OPENAI_TEXT_FALLBACKS=gpt-4.1,gpt-4o,gpt-4o-mini
SOCIAL_GPT5_MAX_TOKENS=16000
SOCIAL_IMAGE_PROVIDER=openai
SOCIAL_OPENAI_IMAGE_MODEL=gpt-image-2
SOCIAL_OPENAI_IMAGE_FALLBACKS=gpt-image-1.5,gpt-image-1
SOCIAL_OPENAI_IMAGE_QUALITY=high
SOCIAL_LOGO_PATH=assets/brand/nefalix-logo.png
SOCIAL_LOGO_SIZE=96
SOCIAL_NOTIFY_TO=enes.ceylan190758@gmail.com,akadirysr@gmail.com
SOCIAL_APPROVE_BASE_URL=https://nefalix.com/api/social
SOCIAL_PUBLISH_WEBHOOK_URL=https://api.nefalix.com/internal/social/publish
NEFALIX_INTERNAL_KEY=...            # Vercel ile aynı değer

# Mail (blog ile paylaşımlı)
BLOG_SMTP_HOST=smtp.hostinger.com
BLOG_SMTP_USER=info@nefalix.com
BLOG_SMTP_PASSWORD=...

# Instagram (Meta Business + Facebook Page bağlantısı)
META_PAGE_ACCESS_TOKEN=
INSTAGRAM_BUSINESS_ACCOUNT_ID=

# LinkedIn (şirket sayfası)
LINKEDIN_ACCESS_TOKEN=
LINKEDIN_ORGANIZATION_ID=

# Opsiyonel Drive yedek
SOCIAL_DRIVE_FOLDER_ID=
GOOGLE_APPLICATION_CREDENTIALS=.tmp/gcp-service-account.json
```

### 3. Vercel env (`nefalix-landing`)

| Değişken | Açıklama |
|----------|----------|
| `NEFALIX_INTERNAL_KEY` | VPS webhook auth |
| `SOCIAL_PUBLISH_WEBHOOK_URL` | `https://api.nefalix.com/internal/social/publish` |
| `SUPABASE_URL` + `SUPABASE_SERVICE_ROLE_KEY` | Onay API |

### 4. Publish webhook (Docker)

```bash
docker compose -f docker-compose.yml -f docker-compose.evolution.yml -f docker-compose.prod.yml up -d social-webhook caddy
```

Health: `curl -s http://127.0.0.1:8791/health`

### 5. Cron

```bash
bash execution/setup-social-cron.sh
```

## Manuel test

```bash
python3 execution/publish-daily-social.py --dry-run
python3 execution/publish-daily-social.py --skip-notify
python3 execution/publish-daily-social.py --force

# Onay maili tekrar
python3 execution/send-social-notification.py --post-id <uuid>

# Yayın (API key'ler doluysa)
python3 execution/social-publish-approved.py --post-id <uuid>
python3 execution/social-publish-approved.py --token <approval_token>
```

Log: `/var/log/nefalix-social.log`

## Günlük rutin (yönetici)

1. 09:30 — mail/WhatsApp gelir (görsel + metin)
2. **Onayla ve yayınla** (~10 sn)
3. “Yayınlandı” onay maili gelir
4. Reddet → o gün paylaşım yok

## Meta / LinkedIn kurulum (tek sefer)

**Instagram:** Business hesap → Facebook Page → Meta Developer → Page Access Token + IG Business Account ID

**LinkedIn:** Şirket sayfası yönetici → Developer App → `w_organization_social` token + Organization ID

Token yoksa sistem üretir + onaya gönderir; otomatik yayın atlanır.

## Edge cases

| Durum | Çözüm |
|-------|--------|
| Onay maili yok | `/var/log/nefalix-social.log`, `BLOG_SMTP_PASSWORD` |
| Onay linki 502 | `social-webhook` container + `NEFALIX_INTERNAL_KEY` eşleşmesi |
| Instagram image_url hatası | Storage migration + `social-upload-storage.py`; **görsel URL internetten erişilebilir olmalı** (cloud Supabase veya public CDN — localhost Meta’ya uymaz) |
| LinkedIn sadece metin | `image_url` eksik — Storage upload kontrol |
| Bugün zaten post var | `--force` ile yeniden üret |
| wf-17 açmayın | executeCommand çalışmaz |

## İlgili dosyalar

| Dosya | Rol |
|-------|-----|
| `execution/publish-daily-social.py` | Günlük orkestrasyon |
| `execution/social-generate-next.py` | Şablon seç + YZ içerik + render |
| `execution/social-style-analyze.py` | Referans görselleri YZ ile analiz |
| `execution/social-style-guide.json` | Feed stil rehberi (Gemini çıktısı) |
| `execution/social_manus_prompt.py` | Manus Swell CX görsel prompt şablonu (logo yok) |
| `execution/social-manus-generate.py` | Opsiyonel Manus API task.create görsel (SOCIAL_IMAGE_PROVIDER=manus) |
| `execution/social-ai-generate.py` | GPT-5 caption + Manus alanları (subject, composition, ui_cards, headline, subtitle) |
| `execution/render-social-image.py` | gpt-image-2 veya Manus API + Pillow overlay |
| `execution/social-brand-overlay.py` | Pillow: logo, wordmark #1A1A2E, footer nefalix.com |
| `execution/social-upload-storage.py` | Public görsel URL |
| `execution/send-social-notification.py` | Onay maili |
| `execution/social-publish-approved.py` | IG + LinkedIn yayın |
| `execution/social-publish-webhook.py` | VPS internal webhook |
| `execution/setup-social-cron.sh` | Cron kurulumu |
| `nefalix-landing/api/blog.js` | Blog API + sosyal onay (`/api/social/approve`) |
