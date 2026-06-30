# Sosyal Medya Otomasyonu (Instagram + LinkedIn)

> Üret → onay (WhatsApp) → yayın. Tam otomatik değil; human-in-the-loop.

## Hedef

NefalixAI marka postlarını haftalık üretmek, yöneticiye WhatsApp ile onaylatmak, onay sonrası Instagram/LinkedIn'e yayınlamak.

## Bileşenler

| Katman | Dosya |
|--------|--------|
| DB şema | `supabase/migrations/20260629130000_social_posts.sql` |
| HTML şablon | `social-templates/base.html` |
| PNG render | `execution/render-social-post.py` |
| Kuyruk üret | `execution/social-generate-next.py` |
| Yayın | `execution/social-publish-approved.py` |
| n8n | `workflows/nefalix-17-social-media.json` (wf-17) |

## Kurulum

### 1. Migration

```bash
# directives/supabase_migrate.md
supabase db push
# veya SQL Editor'de migration dosyasını çalıştır
```

10 şablon `social_post_templates` tablosuna seed edilir.

### 2. VPS bağımlılıkları

```bash
# Chrome + puppeteer (PNG render için)
cd /opt/nefalix/.tmp/sosyal_medya_postlar && npm install puppeteer
# veya repo root'ta puppeteer kurulu olmalı
```

### 3. Env (`.env` / VPS)

```bash
NEFALIX_REPO_ROOT=/opt/nefalix
SOCIAL_DEFAULT_PLATFORM=both          # instagram | linkedin | both
SOCIAL_PUBLIC_BASE_URL=https://api.nefalixai.com/static/social  # IG image_url için

# Instagram (Meta Graph API)
META_PAGE_ACCESS_TOKEN=
INSTAGRAM_BUSINESS_ACCOUNT_ID=

# LinkedIn Marketing API
LINKEDIN_ACCESS_TOKEN=
LINKEDIN_ORGANIZATION_ID=

# Onay bildirimi (mevcut)
CLINIC_MANAGER_WHATSAPP=905491190819
```

Credential yoksa yayın adımı **approved** kalır ve `publish_error` notu düşer — manuel paylaşım yapılabilir.

### 4. Workflow import

```bash
python3 execution/import-workflows.py
```

## Webhook'lar

| Akış | Method | Path |
|------|--------|------|
| Sonraki postu üret | POST | `/webhook/nefalix/social/generate` |
| Onay / red / zamanla | POST | `/webhook/nefalix/social/approve` |
| Onaylı postları yayınla | POST | `/webhook/nefalix/social/publish` |

Tam URL: `https://api.nefalixai.com/webhook/...`

### Üret (manuel)

```bash
curl -X POST https://api.nefalixai.com/webhook/nefalix/social/generate \
  -H "Content-Type: application/json" \
  -d '{}'
```

Belirli şablon:

```bash
curl -X POST https://api.nefalixai.com/webhook/nefalix/social/generate \
  -H "Content-Type: application/json" \
  -d '{"slug":"post_01_brand_hero"}'
```

### Onay

```bash
curl -X POST https://api.nefalixai.com/webhook/nefalix/social/approve \
  -H "Content-Type: application/json" \
  -d '{"token":"<approval_token>","action":"approve"}'
```

Zamanlama:

```json
{"token":"...","action":"schedule","scheduled_at":"2026-07-01T10:00:00Z"}
```

### Yayın

```bash
curl -X POST https://api.nefalixai.com/webhook/nefalix/social/publish \
  -H "Content-Type: application/json" \
  -d '{"post_id":"<uuid>"}'
```

## Akış

```
Pazartesi 09:00 (cron)
  → social-generate-next.py
      → sıradaki şablonu seç (round-robin)
      → social_posts kaydı (pending_approval)
      → HTML → PNG render
      → yöneticiye WA onay mesajı

Yönetici onaylar (webhook / dashboard ileride)
  → status = approved
  → otomatik publish webhook tetiklenir

Saatlik cron
  → social-publish-approved.py
      → approved/scheduled postları Instagram + LinkedIn API
```

## Manuel scriptler (n8n dışında)

```bash
python3 execution/social-generate-next.py --dry-run
python3 execution/social-generate-next.py --slug post_01_brand_hero
python3 execution/render-social-post.py --post-id <uuid>
python3 execution/social-publish-approved.py --dry-run
```

## İletişim kuralları (postlarda)

- **Mail:** `nefalixai@gmail.com`
- **Tel:** yazılmaz
- **Site:** `nefalixai.com`

## Edge cases

| Sorun | Çözüm |
|-------|--------|
| PNG render fail | `--skip-render` ile üret; Manus PNG'yi elle yükle, `image_path` güncelle |
| Execute Command node yok | n8n self-hosted; cloud'da scriptleri VPS cron ile çalıştır |
| IG `image_url` 403 | `SOCIAL_PUBLIC_BASE_URL` nginx static serve ayarla |
| WA onay mesajı gitmiyor | `WHATSAPP_SEND_ENABLED=true`, wf-00 gateway kontrol |

## Self-anneal

- Yeni post teması → `social_post_templates` INSERT veya migration patch
- Görsel layout değişikliği → `social-templates/base.html`
- Caption tonu → `caption_template` alanı veya Gemini polish (ileride wf-17 code node)
