# Saha CRM (iç ekip)

## Ne bu?
Nefalix satış/saha CRM'i. Klinik paneli (`/dashboard`) değil.

## Adres
- Canlı: https://nefalix.com/crm
- Kısa: https://nefalix.com/saha

## Giriş (iç ekip)
Girişte yalnızca kullanıcı adı sorulur: `enes` · `abdulkadir` · `kader` · `destek`

API: `POST /api/crm/login` body `{ "kod": "enes" }` — şifre yok.

## Randevu maili
Yeni randevu / iptal → Enes + Abdülkadir e-postası (`CRM_NOTIFY_TO` yoksa `BLOG_NOTIFY_TO`).

Akış: `crm.html` → `POST /api/crm/notify-randevu` → VPS `https://api.nefalix.com/internal/crm/randevu-mail` → `execution/send-crm-randevu-notification.py` (Hostinger SMTP).

Webhook: Docker `social-webhook` (port 8791). Caddy: `/internal/crm/*` → `social-webhook:8791`.

## Ortak veri
- Tablo: `public.nefalix_state` (tek satır `id=1`, jsonb)
- Migration: `supabase/migrations/20260714150000_saha_crm_state.sql`
- API (Vercel → n8n Supabase proxy):
  - `POST /api/crm/login`
  - `GET /api/crm/state`
  - `POST /api/crm/save`
  - `POST /api/crm/logout`
  - `POST /api/crm/notify-randevu`

Herkes aynı klinik/not/randevu verisini görür (~15 sn poll).

## Dosyalar
- `nefalix-landing/crm.html` — arayüz
- `nefalix-landing/api/blog.js` — CRM action'ları (Hobby function limiti)
- `execution/send-crm-randevu-notification.py` — SMTP mail
- `execution/social-publish-webhook.py` — `/randevu-mail` route
