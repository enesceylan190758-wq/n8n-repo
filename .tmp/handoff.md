# Cursor Handoff — Nefalix

**Tarih:** 2026-06-25  
**Pilot `clinic_id`:** `51738ea8-c12e-40ce-a0e2-42869496d76b` (MediDent Kartal)

## Proje özeti

Nefalix, klinik ve hizmet işletmeleri için WhatsApp-first hasta deneyimi, NPS/eNPS, Google yorumları, inbox ve itibar yönetimi platformudur. Bu repo (`n8n-repo`) orchestration katmanıdır: `directives/` SOP, `execution/` deterministik scriptler, `workflows/` n8n JSON, `supabase/migrations/` şema. Canlı stack: VPS `93.127.186.45` (`/opt/nefalix`), API `https://api.nefalixai.com`, site/dashboard `https://nefalixai.com`. Public site ayrı workspace: **`/Users/enesceylan/nefalix-landing`** (Vercel projesi `nefalix-landing`, deploy: `vercel --prod --yes`).

## Bu sohbette yapılanlar

### Landing (`nefalix-landing` — ayrı repo)

- Ana sayfa v2 canlı: sapphire/gold sıvı gradient başlıklar (`.liquid-sapphire-gold`, `.home-refresh-body .showcase-card h3` vb.).
- Guided demo modal (`#guided-demo-modal`, `initGuidedDemo()` → Cal.com `enes-ceylan/15min`).
- Dashboard bölümünde ortalanmış premium `Canlı demoyu başlat` CTA overlay.
- Video bölümü ana sayfaya eklendi (`/nefalix-runway-agent.mp4`, `homepage-video-section`).
- Mobil uyum: hamburger menü (`initMobileNav`), hero orbit/chip gizleme, yatay overflow düzeltmesi, dashboard CTA static stack, video/showcase responsive.
- Yasal sayfalar: `/kvkk`, `/gizlilik-politikasi`, `/kullanici-sozlesmesi`.
- Footer platform logoları, SSS portreleri, çoklu deploy production’a alındı.

### Backend repo (`n8n-repo`)

- Bu oturumda kod değişikliği yapılmadı; workspace’te **commit edilmemiş büyük paket** vardı (workflow 00–16, migrations, directives, execution scriptleri, PayTR env isimleri `.env.example`).

## Yarım kalan işler

1. **PayTR canlı ödeme** — `PAYTR_*` env Vercel’e yazılıp `api/billing.js` uçtan uca test; kullanıcı başvurusu bekleniyor olabilir.
2. **`nefalix-landing` git remote** — Yerel branch `cursor/landing-i18n-and-chat`; uzak repo bağlı değilse push yapılamaz; Vercel CLI ile prod deploy yapıldı ama Git senkronu eksik olabilir.
3. **Mobil menü** — Açılıyor; `Platformlar` alt linkleri uzun menüde scroll ile erişiliyor (ilk fold altında).
4. **Benefit kartları** — Sadece bazı `h3`’lere `liquid-sapphire-gold` class verildi; diğer 4 kart hâlâ genel selector’a bağlı.
5. **n8n-repo** — Tüm yeni workflow/migration’ların prod VPS’e import + `supabase db push` / migrate doğrulanmadı (bu handoff commit’inden sonra yapılmalı).
6. **Stripe** — Kod var, env yok; öncelik PayTR.

## Bilinen hatalar / dikkat

- **`.tmp/`** gitignore’da; sadece `handoff.md` `-f` ile commit edilir.
- **n8n Docker → Supabase:** `host.docker.internal:54321`, `127.0.0.1` değil.
- **`.env` / secret commit etme.**
- Landing CSS’te **çift `@media` blokları** var (dosya sonunda ve ortada); mobil kurallar çakışabilir — değişiklikten sonra 390px kontrol et.
- `background-clip: text` için **`-webkit-text-fill-color: transparent`** gerekli (Safari).
- `nefalix-site-v2/` bu repoda kopya; canlı site kaynağı **`nefalix-landing`**.
- WhatsApp gönderim: `WHATSAPP_SEND_ENABLED`, rate limit env’leri VPS’te kontrol et.

## Sonraki 3 adım

1. **Yeni hesapta:** `.tmp/handoff.md` + `AGENTS.md` + ilgili `directives/` oku; `git pull` sonra durumu doğrula.
2. **`nefalix-landing`:** `git status` → remote varsa push; yoksa GitHub repo oluştur/bağla; mobil menü + kalan başlık gradientlerini bitir.
3. **`n8n-repo`:** `directives/supabase_migrate.md` + `import_workflows.md` ile migration import ve `execution/test-all-workflows.sh`; PayTR secret gelince Vercel env + fiyatlar checkout test.

## Önemli env değişkenleri (sadece isimler)

**Ortak / local (`.env.example`):**  
`MCP_AUTH_TOKEN`, `MCP_PORT`, `LOG_LEVEL`, `GCP_PROJECT_ID`, `GCP_REGION`, `VERTEX_GEMINI_MODEL`, `GOOGLE_APPLICATION_CREDENTIALS`, `GCP_ACCESS_TOKEN`, `GOOGLE_PLACES_API_KEY`, `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `EVOLUTION_PORT`, `EVOLUTION_MANAGER_PORT`, `EVOLUTION_SERVER_URL`, `EVOLUTION_API_KEY`, `EVOLUTION_POSTGRES_PASSWORD`, `CLINIC_MANAGER_WHATSAPP`, `ESTESOFT_API_USERNAME`, `ESTESOFT_API_KEY`, `ESTESOFT_TENANT_ID`, `ESTESOFT_STELLA_API_BASE`, `ESTESOFT_API_PASSWORD`, `DASHBOARD_SESSION_SECRET`, `NEFALIX_INTERNAL_KEY`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PRICE_STANDARD`, `STRIPE_PRICE_PROFESSIONAL`, `STRIPE_SUCCESS_URL`, `STRIPE_CANCEL_URL`, `PAYTR_MERCHANT_ID`, `PAYTR_MERCHANT_KEY`, `PAYTR_MERCHANT_SALT`, `PAYTR_TEST_MODE`, `PAYTR_DEBUG`, `PAYTR_OK_URL`, `PAYTR_FAIL_URL`

**VPS (`.env.vps.example`):**  
`EVOLUTION_PUBLIC_HOST`, `ACME_EMAIL`, `WHATSAPP_SEND_ENABLED`, `WHATSAPP_MIN_INTERVAL_SEC`, `WHATSAPP_MAX_PER_HOUR`, `ESTESOFT_POLL_MAX_PER_RUN`, `ESTESOFT_POLL_HOURS`, `OPENAI_API_KEY`, (+ yukarıdakilerin VPS karşılıkları)

**Vercel (landing/dashboard):** Supabase + `DASHBOARD_SESSION_SECRET`, `NEFALIX_INTERNAL_KEY`, `PAYTR_*`, Stripe alanları (kullanılıyorsa).

## Yeni hesapta ilk prompt

```text
Proje: /Users/enesceylan/n8n-repo
Önce .tmp/handoff.md ve AGENTS.md oku.
Pilot clinic_id: 51738ea8-c12e-40ce-a0e2-42869496d76b
Kurallar: directives/ + execution/ önce; .env commit etme; deploy/migration için onay iste.
Landing ayrı repo: /Users/enesceylan/nefalix-landing
Durumu özetle ve handoff’taki “Sonraki 3 adım”dan devam et.
```

## İlgili dosyalar

| Konu | Yol |
|------|-----|
| Agent SOP | `AGENTS.md`, `directives/` |
| Antigravity read-only handoff | `ANTIGRAVITY_HANDOFF.md` |
| Landing ana sayfa | `nefalix-landing/index.html`, `shared.css`, `shared.js` |
| Workflow kaynak | `workflows/nefalix-*.json` |
| DB | `supabase/migrations/` |
