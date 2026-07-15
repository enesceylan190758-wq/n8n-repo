# Nefalix — Site & Dashboard (Geliştirici Özeti)

Kısa referans: canlı adresler, giriş/çıkış mantığı, dosyalar ve secret'ların nerede tutulduğu.

**Gerçek şifreler ve API anahtarları bu dosyada yok.** Değerler Vercel env, Supabase ve ekip içi paylaşımdan alınır.

---

## Mimari (tek bakışta)

```
nefalix.com (Vercel)          api.nefalix.com (VPS)
├── Statik site (HTML/CSS/JS)   ├── n8n workflow'ları
├── Dashboard UI                ├── Supabase proxy webhook
└── /api/* serverless           └── Evolution API (WhatsApp)
         │
         └── Supabase (tek veri katmanı — klinik, inbox, NPS, kullanıcılar)
```

| Repo | Yerel yol | Ne var |
|------|-----------|--------|
| **Landing + Dashboard UI** | `/Users/enesceylan/nefalix-landing` | Site, panel, Vercel API route'ları |
| **Orchestration** | `/Users/enesceylan/n8n-repo` | n8n workflow JSON, Supabase migration, script'ler |

Pilot klinik `clinic_id`: `51738ea8-c12e-40ce-a0e2-42869496d76b` (MediDent Kartal)

---

## Canlı URL'ler

| Sayfa | URL |
|-------|-----|
| Ana site | https://nefalix.com |
| Dashboard giriş | https://nefalix.com/dashboard/login |
| Dashboard panel | https://nefalix.com/dashboard |
| İlk şifre kurulumu | https://nefalix.com/dashboard/setup?token=… |
| API (backend) | https://api.nefalix.com |

Vercel projesi: `nefalix-landing` · Deploy: `vercel --prod --yes` (landing repo kökünden)

---

## Site — Demo CTA akışı

| Buton sınıfı | Davranış |
|--------------|----------|
| `.guided-demo-trigger` | Ana sayfadaki 7 adımlı modal (`#guided-demo-modal`); modal yoksa Cal.com |
| `.cal-demo` / `.btn-demo` | Doğrudan Cal.com takvim (`enes-ceylan/15min`) |
| Modal form sonu | Cal.com, lead bilgileriyle açılır |

Kod: `nefalix-landing/shared.js` · Nav şablonu: `partials/site-nav.html` · Sync script: `scripts/sync-site-nav.js`

Footer sosyal: LinkedIn, Instagram, WhatsApp (`SOCIAL_LINKS` in `shared.js`) · Güven şeridi: KVKK + Veriler TR'de (`initFooterTrust()`)

---

## Giriş / çıkış mantığı

### Oturum modeli

- **Cookie tabanlı**, stateless JWT benzeri imzalı token
- Cookie adı: `nefalix_session`
- Süre: **7 gün** (`HttpOnly`, `SameSite=Lax`, production'da `Secure`)
- İmzalama: `DASHBOARD_SESSION_SECRET` (Vercel env)

### Giriş yolları

**1) Normal giriş** — `/dashboard/login`

1. Kullanıcı e-posta + şifre girer
2. `POST /api/auth` → `findUser()` çalışır
3. Doğrulama sırası:
   - Önce Vercel env `DASHBOARD_USERS` (JSON, eski admin hesapları)
   - Sonra Supabase `dashboard_users` tablosu (`status = active`)
4. Başarılıysa cookie set edilir → `/dashboard`

**2) Firma ilk kurulum** — `/dashboard/setup?token=…`

1. Admin panelden yeni firma eklenince `api/firms.js` pending kullanıcı oluşturur
2. Tek kullanımlık setup token (7 gün geçerli) hash olarak DB'de tutulur
3. Link ile gelen kullanıcı şifre belirler → `status: active` → otomatik giriş

**3) Demo giriş (opsiyonel, şu an kapalı)**

- `/dashboard/demo?token=…` → `GET /api/auth?action=demo&token=…`
- Vercel'de `DASHBOARD_DEMO_TOKEN` tanımlı değilse çalışmaz
- Açıkken admin yetkili demo oturumu açar — prod'da dikkatli kullan

### Çıkış

- Panel sağ üst menü → **Çıkış**
- `POST /api/auth?action=logout` → cookie silinir → `/dashboard/login`

### Oturum kontrolü

- Panel açılışında: `GET /api/auth?action=me`
- API route'ları: `requireAuth()` (`api/_lib/auth.js`)
- 401 → login sayfasına yönlendirme

---

## Roller

| Rol | Ne görür |
|-----|----------|
| `admin` | Tüm firmalar, sektörler (klinik/otel/oto), firma ekleme, AI bütçe widget |
| `manager` | Sadece kendi `clinic_id` verisi (NPS, inbox, yorumlar vb. filtrelenir) |

---

## Nerede ne tutuluyor?

### Vercel env (production — `nefalix-landing`)

| Değişken | Amaç |
|----------|------|
| `DASHBOARD_SESSION_SECRET` | Oturum cookie imzası (rotasyon = herkes çıkış) |
| `DASHBOARD_USERS` | Eski admin JSON `[{email, salt, hash, role, …}]` |
| `NEFALIX_INTERNAL_KEY` | Vercel → VPS Supabase proxy auth header |
| `N8N_DASHBOARD_URL` | Dashboard veri webhook (n8n) |
| `N8N_SUPABASE_PROXY_URL` | Auth/DB istekleri için proxy |
| `N8N_INBOX_SEND_URL` / `CLEAR` / `GOOGLE_REVIEW_APPROVE` | Panel aksiyonları |
| `N8N_WHATSAPP_CONNECT_URL` | QR bağlantı |
| `EVOLUTION_API_URL` / `EVOLUTION_API_KEY` | WhatsApp |
| `WHATSAPP_SEND_ENABLED` | Gönderim açık/kapalı |
| `DASHBOARD_DEMO_TOKEN` | (Opsiyonel) şifresiz demo link — şu an tanımlı değil |
| `DEV_DASHBOARD_EMAIL` | **Geçici** yazılımcı giriş e-postası |
| `DEV_DASHBOARD_PASSWORD` | **Geçici** yazılımcı şifresi (düz metin, kaldırılınca giriş kapanır) |
| `DEV_DASHBOARD_ROLE` | (Opsiyonel) varsayılan `admin` |

Liste: `vercel env ls` (landing repo içinde)

### Supabase tablosu: `dashboard_users`

Migration: `n8n-repo/supabase/migrations/20260628100000_dashboard_users_billing_metrics.sql`

| Alan | Açıklama |
|------|----------|
| `email` | Giriş e-postası (unique) |
| `salt` + `password_hash` | scrypt ile hash (şifre düz metin tutulmaz) |
| `role` | `admin` veya `manager` |
| `clinic_id` | Manager için firma bağlantısı |
| `status` | `pending` → `active` → `disabled` |
| `setup_token_hash` | İlk şifre linki (tek kullanımlık) |

RLS: sadece `service_role` erişir. Panel API'leri Vercel üzerinden service role veya n8n proxy ile konuşur.

### İş verisi (dashboard içeriği)

Supabase tabloları: `clinics`, `inbox_messages`, `nps_responses`, `google_reviews`, `recall_campaigns`, `enps_responses`, `reputation_mentions`, …

Şema kaynağı: `n8n-repo/supabase/migrations/`

---

## Önemli dosyalar (landing repo)

| Dosya | Rol |
|-------|-----|
| `login.html` + `nefalix-login.js` | Giriş ekranı |
| `setup-password.html` + `nefalix-setup-password.js` | İlk şifre |
| `dashboard.html` + `nefalix-dashboard.js` | Panel UI |
| `api/auth.js` | Giriş, çıkış, setup, demo, `me` |
| `api/_lib/auth.js` | Cookie, hash, session imza |
| `api/dashboard.js` | Panel verisi (n8n + Supabase metrics) |
| `api/firms.js` | Firma CRUD + setup link üretimi |
| `vercel.json` | URL rewrite (`/dashboard` → `dashboard.html` vb.) |

---

## API özeti

| Endpoint | Method | Açıklama |
|----------|--------|----------|
| `/api/auth` | POST | E-posta/şifre giriş |
| `/api/auth?action=me` | GET | Oturum kontrolü |
| `/api/auth?action=logout` | POST | Çıkış |
| `/api/auth?action=setup` | GET/POST | İlk şifre kurulumu |
| `/api/auth?action=demo` | GET | Şifresiz demo (env gerekli) |
| `/api/dashboard` | GET | Panel verisi (auth zorunlu) |
| `/api/firms` | CRUD | Firma yönetimi (admin) |
| `/api/inbox/send`, `/api/inbox/clear` | POST | Inbox aksiyonları |
| `/api/billing` | * | PayTR / Stripe checkout |

Korumalı route'lar `requireAuth()` kullanır; manager için `clinic_id` scope uygulanır (`api/dashboard.js` → `scopeBody()`).

---

## Yeni firma / kullanıcı akışı

1. Admin panel → Firmalar → yeni firma (e-posta zorunlu)
2. `api/firms.js` → `dashboard_users` satırı `pending` + setup token
3. Admin'e dönen link: `https://nefalix.com/dashboard/setup?token=…`
4. Firma yöneticisi şifre belirler → `active` → normal giriş

---

## Lokal geliştirme

```bash
cd nefalix-landing
npm run preview   # http://localhost:3000
```

Lokal auth için `.env` veya Vercel env pull gerekir (`DASHBOARD_SESSION_SECRET` minimum).

Backend stack (n8n + Supabase): `n8n-repo` → `directives/start_stack.md`

---

## Güvenlik notları

- `.env` ve secret'lar **git'e commit edilmez**
- `DASHBOARD_SESSION_SECRET` değişirse tüm kullanıcılar yeniden giriş yapar
- Setup token tek kullanımlık; süresi dolunca yeni link üretilmeli
- Demo token (`DASHBOARD_DEMO_TOKEN`) admin yetkisi verir — paylaşımda dikkat
- Detay: `n8n-repo/directives/security.md`

---

## Geçici yazılımcı girişi (kaldırılacak)

Vercel env ile açılan geçici hesap. Env silinince giriş tamamen kapanır.

| Alan | Değer |
|------|-------|
| Giriş sayfası | https://nefalix.com/dashboard/login |
| E-posta | `yazilimci@nefalix.com` |
| Şifre | `nefalix123` |
| Yetki | `admin` (tüm panel) |

**Kapatmak için** (Vercel → `nefalix-landing` → Settings → Environment Variables):

```bash
vercel env rm DEV_DASHBOARD_EMAIL production --yes
vercel env rm DEV_DASHBOARD_PASSWORD production --yes
vercel --prod --yes
```

Kod: `nefalix-landing/api/_lib/auth.js` → `findDevUser()`

---

## İlgili dokümanlar

- `n8n-repo/AGENTS.md` — agent / çalışma kuralları
- `n8n-repo/docs/ARCHITECTURE.md` — genel mimari (varsa)
- `n8n-repo/directives/supabase_migrate.md` — DB migration
- `n8n-repo/.tmp/handoff.md` — güncel oturum notları
