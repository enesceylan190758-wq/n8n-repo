# Cursor Handoff — Nefalix

**Tarih:** 2026-07-29 (Stella import lead filtresi + danışan limit fix live)  

**Pilot `clinic_id`:** `51738ea8-c12e-40ce-a0e2-42869496d76b` (MediDent Kartal)

## Takım ayrımı + n8n → Next.js (Arif brief)

İş büyürse sistem taşınabilir. Karar:

| Rol | Kim | Ne |
|-----|-----|-----|
| PM / vibe coding / mimari | Bu taraf | İşin *ne* olduğu — spec, iş kuralları |
| Next.js geçişi | **Arif** | n8n + HTML/Vercel işlerinin Next.js’te *gerçekleştirilmesi* |

**Arif tek kaynak (PDF + MD):**
- `docs/Nefalix_Urun_Mimarisi.md`
- `docs/Nefalix_Urun_Mimarisi.pdf`
- Yeniden üret: `/usr/bin/python3 execution/generate-urun-aktarim-pdf.py`

Cursor agent sessizce paralel Next codebase kurmaz; spec bu dokümanda yaşatılır.

## Proje özeti

Nefalix, klinik ve hizmet işletmeleri için WhatsApp-first hasta deneyimi, NPS/eNPS, Google yorumları, inbox ve itibar yönetimi platformudur. Bu repo (`n8n-repo`) orchestration katmanıdır: `directives/` SOP, `execution/` deterministik scriptler, `workflows/` n8n JSON, `supabase/migrations/` şema. Canlı stack: VPS `93.127.186.45` (`/opt/nefalix`), API `https://api.nefalixai.com`, site/dashboard `https://nefalixai.com`. Public site ayrı workspace: **`/Users/enesceylan/nefalix-landing`** (Vercel projesi `nefalix-landing`, deploy: `vercel --prod --yes`).

## Blog / GEO kalite (2026-07-17)

Swell CX Resources seviyesine yaklaştırma yapıldı (canlı):

- **Kapaklar:** v5 — Unsplash insan figürü + markalı SVG overlay (`/api/blog?action=cover&v=5`).
- **Batch SEO/AI:** 10 blog + 10 GEO (18–27 Temmuz) canlı; **tek digest mail** gitti (enes + akadir).
- Komut: `python3 execution/publish-batch-seo-geo.py`
- Log: `/var/log/nefalix-batch-seo-geo.log`

### SEO/GEO ajan planı (2026-07-29)

- Araştırma planı: `docs/nefalix-seo-geo-ajan-plani.md`
- Gap notları: `docs/nefalix-seo-geo-gap-notes.md`
- Faz 0: API’de blog + GEO var; **indeks SSR** landed (`action=blog-index` / `geo-index`, rewrite `/blog` + `/geo`). Detay SSR + sitemap önceki gibi.
- Sonraki: GSC indeks doğrulama (plan §9); Vertex batch bu turda yok.

## Abdülkadir — Klinik CRM düzenlemesi

**Sorumlu:** Abdülkadir Yaşar (Medident pilot)  
**Directive:** `directives/clinic_crm.md`  
**Canlı panel:** `https://nefalix.com/klinik-crm` — giriş kodu: `abdulkadir`

| CRM | Durum | Abdülkadir ne yapar |
|-----|--------|---------------------|
| **Klinik CRM** (`/klinik-crm`) | Açık (arşivden geri) | Lead, atama, dinamik arama, not, randevu |
| **Saha CRM** (`/crm`, `/saha`) | Açık (arşivden geri) | Nefalix saha pipeline |
| **Kurum CRM** (`/nefalix-crm`) | Ana canlı | Yeni kurum CRM |
| **Hasta CRM** (`/hasta-crm`) | Canlı (2026-07-27) | DC klinik UI — HastaKarti / Danışan |
| **Estesoft HBYS** | Pilot | Randevu tamamlandı → NPS taslak → dashboard onay |

**Düzenleme dosyaları (Cursor):**
- `nefalix-landing/klinik-crm.html` — arayüz
- `nefalix-landing/api/_lib/clinic-crm.js` — API + Dinamik Arama kuralları
- Supabase `crm_segments` / `crm_users` — segment offset, yeni temsilci

**Deploy:** `cd nefalix-landing && vercel --prod --yes` (onaylı)

**Abdülkadir Cursor ilk prompt:** `directives/clinic_crm.md` sonundaki blok.

### CRM — Dinamik sıfırlama (2026-07-27)

- Saha CRM tüm ekip Dinamik → Havuz: **62 klinik** (`execution/saha-crm-dinamik-to-havuz.py --all` VPS `nefalix_state` id=1)
- Sonra: en/ak/kd/mi dinamik = 0

## Bu sohbette yapılanlar

### Stella import — lead filtresi + danışan limit (2026-07-29)

**Status:** pack + **vercel --prod OK**  
**Deploy:** `dpl_6zvUNmFzVU8vUxw7AJ4QZX2brXgw` → `https://nefalix.com/hasta-crm`

**Veri sayıları (import raporu 2b674594):**

| Kaynak | Adet |
|--------|------|
| Stella API | ~7501 |
| VPS `crm_contacts` (stage=danisan) | 7655 |
| Lead (yeni segment) | 1 |
| Danışan aktif | ~1997 |

**Fix:**
- `isNewLeadSegment`: segmentsiz kayıt artık lead **değil** — yalnızca `NEW_LEAD_LABELS` (YENİ DATA / Yeni Lead / Yeni Gelen)
- `refreshData`: `clinic-leads` fetch limit **10000** (önce 300/5000; ~7654 danışan yüklenemiyordu)
- Pack: `python3 execution/pack-nefalix-hasta-crm.py`
- Prod bundle doğrulandı: `_assets/a90a0ed2…js` → `limit=10000`, `NEW_LEAD_LABELS.has(s)` (eski `!s ||` yok)

### CRM Next.js geçiş kararı (2026-07-27)

- Plan: `docs/CRM_NextJS_Gecis_Plani.md`
- Karar: **CRM kalıcı = Next; Stella kesimi şimdi P0 HTML ile** (`/hasta-crm` paralel koşu; Next Stella’yı bloke etmez)

### Stella discovery paket (2026-07-27) — adım 1+2 tamam

| Yer | Path | Doğrulama |
|-----|------|-----------|
| Git LFS | `discovery/stella-discovery-2026-07-27.zip` | `0aae4bc` (~171MB) |
| Cloud `.tmp` | `.tmp/stella-discovery/` | unzip sonrası 390 PNG + 4 XLSX + Onat |
| VPS | `root@93.127.186.45:/opt/nefalix/.tmp/stella-discovery/` | 397 dosya (yedek) |
| Gap map | `docs/Stella_Gap_Action_Map.md` | stage crawl + Excel + Onat |
| Path doc | `docs/stella_discovery_assets.md` | |
| **Crawl orchestrator** | `.tmp/stella-crawl-state.json` | **13/13 done** (2026-07-28); lock **off** |
| Stage docs | `docs/stella_crawl/stage-01` … `stage-13` | SOP: `directives/stella_screenshot_crawl.md` |


### Hasta CRM P1c LIVE (2026-07-28)

**Status:** Transfer Takvimi + clinic-reports segment/temsilci · vercel OK  
**Deploy:** `dpl_ERPXbhQGJNorYPWdhDKBVwMVCetG` → `https://nefalix.com/hasta-crm`  
**State:** `.tmp/hasta-crm-p1c-state.json` · `docs/hasta_crm_p1c_backlog.md`

- `TransferTakvim.dc.html` — teklif hotel/transfer + tip=Transfer randevu
- HastaKarti **Transfer & Konaklama** sekmesi wired
- `clinic-reports`: `by_segment`, `by_temsilci` → Raporlar Ay Sonu panelleri

### Hasta CRM P1b LIVE (2026-07-28)

**Status:** Son İşlemler + Bakiye + Raporlar ay sonu · pack + vercel OK  
**Deploy:** `dpl_CMvaSdJ5asH712bNdLLK6TBwZhGC` → `https://nefalix.com/hasta-crm`  
**State:** `.tmp/hasta-crm-p1b-state.json` · `docs/hasta_crm_p1b_backlog.md`

- `getRecentActivity` — fake audit kaldırıldı
- `getBakiye` — kabul teklif − tahsilat
- Raporlar: indeks kartları + `clinic-reports` Ay Sonu sekmesi

### Hasta CRM P1 daily-ops COMPLETE (2026-07-28)

**Status:** p1-01…p1-05 **done** · 2× vercel prod · smoke OK  
**Latest deploy:** `dpl_6exgkcuGbMz1sofgVZ6WW8UvqYKi` → `https://nefalix.com/hasta-crm`  
**State:** `.tmp/hasta-crm-p1-state.json` · Backlog: `docs/hasta_crm_p1_backlog.md`

| ID | Özet |
|----|------|
| p1-01 | Dashboard KPI canlı (`dashboardKpis`) — fake kaldırıldı |
| p1-02 | Lead segment/temsilci/ülke filtre |
| p1-03 | Giderler TRY/EUR/yöntem kartları |
| p1-04 | Salesline pack + 5 kolon |
| p1-05 | Firma LS CRUD + Firma Ödemesi → `clinic-payments` (`Firma:` description) |

**Sonraki öneri:** Son İşlemler · Bakiye · Rapor indeks · WA inbox

### Hasta CRM P0 cutover LIVE (2026-07-28 18:23 TR)

**Status:** VPS apply OK · pack OK · **vercel --prod OK** · smoke `/hasta-crm` **HTTP 200**

Deploy: `dpl_CczCEmnLvySNAPWUHckGWfiZpoWW` → aliased `https://nefalix.com`  
URL: **https://nefalix.com/hasta-crm** (bundle 267000 bytes)  
State: `.tmp/hasta-crm-p0-state.json` → `cutover_live: live`

### Hasta CRM P0-01 — Lead + Dinamik parity (2026-07-28)

**Status:** code done · pack done · **LIVE**

Acceptance:
- [x] Landing `LeadListesi`: Ülke + Temsilci + Referans + işlem menü (Görüntüle / Danışana Aktar / WA)
- [x] `YeniLead`: Dil, Konu, Mesaj (+ E-Posta, Ülke TR default) → `store.addDanisan` → `clinic-leads`
- [x] Persist: `email` kolonu; Dil/Konu → `kampanya` meta (`Dil: … | Konu: …`); Mesaj → `clinic-note-save` (yeni DB kolonu yok)
- [x] `DinamikArama`: Ülke kolonu
- [x] Pack: `YeniLead` + `DinamikArama` eklendi → `nefalix-hasta-crm.html`
- [x] Prod deploy 2026-07-28

Dosyalar: `hasta-crm-app/{LeadListesi,YeniLead,DinamikArama,store}.js|html`, landing sync, `api/_lib/clinic-crm.js` (email), `execution/pack-nefalix-hasta-crm.py`

### Stella screenshot aşamalı crawl (2026-07-28)

- SOP: `directives/stella_screenshot_crawl.md`
- Orchestrator: `python3 execution/stella-screenshot-stage.py` (state `.tmp/stella-crawl-state.json`)
- Stage 01 CRM/Lead: **done** → `docs/stella_crawl/stage-01-crm_lead.md` (17/17)
- Stage 02 Hasta kartı: **in_progress** (33 PNG, sample 25)
- Stella UI tıkla: bu ortamda browser MCP yok; API token OK (`.env` ESTESOFT_*). Panel için ayrı kullanıcı+browser lazım.

**Sonraki:** Stella crawl stage zinciri; UI smoke (teklif otel / kasa EUR) manuel.

### Hasta CRM hotfix (2026-07-27) — kart + Lead filtresi

Canlı doğrulandı (`https://nefalix.com/hasta-crm` bundle):

- `patientHistory` senkron return + notlar fire-and-forget (HastaKarti `.slice` kırığı yok)
- `getLeads` → `NEW_LEAD_LABELS` (YENİ DATA / Yeni Lead / Yeni Gelen); segmentsiz lead **değil** (2026-07-29 düzeltildi)
- Stage: atanmış non-yeni → danisan (reclassify 0 bekleyen; `execution/reclassify-crm-stages.py`)
- Pack: `execution/pack-nefalix-hasta-crm.py` (`NEFALIX_LANDING` veya `.tmp/nefalix-landing-extract`)


### Onat plan doğrulama (2026-07-28)

- Transkript + teklif otel/transfer + kasa EUR: `hasta-crm-app/` (commit `a7e35aa`+)
- Extract yeniden: canlı HTML unpack + patch overlay + `pack-nefalix-hasta-crm.py`
- Gap #7/#14 / sonraki adımlar güncellendi
- **Mac DONE (2026-07-28):** apply offers/payments + `vercel --prod`

### Hasta kartı not+segment + randevu durum (2026-07-27 gece)

- `HastaKarti`: not kaydında segment select (boot `getSegments`) → `clinic-note-save` + gun_offset
- `RandevuListe` + kart sekmesi: durum select (Geldi/Gelmedi/…) renkli; `setRandevuStatus`
- Pack: `RandevuListe`/`RandevuTakvim` eklendi; `hasta-crm-app/` sync
- **Mac DONE (2026-07-28):** VPS apply + vercel prod

### Teklif/Kasa 502 + Lead kolon (2026-07-27 akşam)

- Kök neden: VPS’te `crm_offers` / `crm_payments` eksik → Proxy workflow error
- Düzelt: `bash execution/apply-crm-offers-payments-vps.sh` (Mac SSH)
- Lead listesi: Temsilci + Referans kolonları (`hasta-crm-app/LeadListesi.dc.html`)
- Deploy: `bash execution/deploy-hasta-crm-from-extract.sh`

### Onat + P0 teklif/kasa (2026-07-27)

- Transkript: `docs/Onat_Sk_Transcript.md`
- UI patch (git): `hasta-crm-app/` — otel/transfer, YeniSatış EUR/yöntem/işlem tipi
- Pack extract: `.tmp/nefalix-landing-extract/nefalix-hasta-crm.html`
- **Mac deploy:** `bash execution/deploy-hasta-crm-from-extract.sh` (Vercel token cloud’da yok)

### Stella → Hasta CRM P0 (2026-07-27)

- **Spec:** `docs/Stella_Phase1_Spec.md`, `docs/stella_segments.csv`, `docs/stella_reference_sources.csv`
- **Migration:** `supabase/migrations/20260727120000_crm_stella_phase1.sql`
- **API:** `clinic-crm.js` → `sbCrmRequest` (cloud prod); yeni endpoint: `clinic-me`, `clinic-offers`, `clinic-payments`, `clinic-reports`
- **Hasta store:** `nefalix-hasta-crm-app/store.js` — cookie oturum 90 gün, `resumeRoute`, clinic-* API
- **Pack:** `execution/pack-nefalix-hasta-crm.py`
- **Import:** `import-stella-definitions.py --prod`, `import-stella-crm.py --prod`
- **SOP:** `directives/stella_migration.md`

**Prod uygulandı (2026-07-27):**
1. VPS alter migration + 39 segment + 11 referans seed
2. Stella import: ~411 aktif contact (devam arka planda `/var/log/nefalix-stella-import.log`), 13 randevu
3. `clinic-crm.js` → `sbRequest` (VPS proxy; cloud PROD değil)
4. `vercel --prod` → https://nefalix.com/hasta-crm
5. Stella List pagination: `offset` (skip çalışmıyor)

### Hasta CRM canlı (2026-07-27)

- Canlı: **https://nefalix.com/hasta-crm**
- Kaynak: Drive `CRM ÇALIŞMASI/Nefalix CRM - Hasta.html` → `nefalix-landing/nefalix-hasta-crm.html`
- Rewrite: `/hasta-crm` → `nefalix-hasta-crm.html` (HastaKarti / DanisanListesi)

### İletişim / Mail sistemi (2026-07-23)

- Canlı: https://nefalix.com/iletisim (+ `/imza`, `/kilavuz`, `/onizleme`; alias `/mail`)
- Kaynak: `nefalix-landing/iletisim.html` — telefonlar + sosyal dolduruldu; CRM deep-link `?firm=&name=&kart=`
- CRM: Kurum kartı "Mail kalıbı" + menü CRM → İletişim Kalıpları
- SOP: `directives/nefalix_mail.md`


### CRM devri (Abdülkadir)

- `directives/clinic_crm.md` — Klinik CRM düzenleme SOP (giriş, dosya haritası, iş kuralları, Supabase segment/kullanıcı, deploy)
- Handoff’a Abdülkadir bölümü eklendi

### Ürün mimarisi (Arif)

- `docs/Nefalix_Urun_Mimarisi.md` — sürüm 3.0; her CX/CRM modülü tam iş kuralı + durum + veri + kenar
- `docs/Nefalix_Urun_Mimarisi.pdf` — Arif’e gönderilecek PDF
- `execution/generate-urun-aktarim-pdf.py` — MD→PDF (Arial Unicode, `/usr/bin/python3`)
- Secret/şifre PDF’te yok

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
5. **Stella P0 prod** — Migration + import + Vercel deploy (yukarıdaki 4 adım); ardından 2 hafta paralel koşu (`directives/stella_migration.md`).
6. **Stripe** — Kod var, env yok; öncelik PayTR.

## Bilinen hatalar / dikkat

- **`.tmp/`** gitignore’da; sadece `handoff.md` `-f` ile commit edilir.
- **n8n Docker → Supabase:** `host.docker.internal:54321`, `127.0.0.1` değil.
- **`.env` / secret commit etme.**
- Landing CSS’te **çift `@media` blokları** var (dosya sonunda ve ortada); mobil kurallar çakışabilir — değişiklikten sonra 390px kontrol et.
- `background-clip: text` için **`-webkit-text-fill-color: transparent`** gerekli (Safari).
- `nefalix-site-v2/` bu repoda kopya; canlı site kaynağı **`nefalix-landing`**.
- WhatsApp gönderim: `WHATSAPP_SEND_ENABLED`, rate limit env’leri VPS’te kontrol et.

## Hasta CRM P0 director (2026-07-28)

- State: `.tmp/hasta-crm-p0-state.json` · Backlog: `docs/hasta_crm_p0_backlog.md`
- **Coding slice p0-01…p0-06:** DONE
- **cutover_live: live** — VPS `crm_offers`/`crm_payments` apply OK; pack 15 files; `vercel --prod` aliased `nefalix.com`; smoke HTTP 200

## Sonraki 3 adım

### 1. P1+ (opsiyonel)
- Stella satış raporu satır detay · WA inbox (Evolution)

### 2. Paralel koşu go/no-go
- `directives/stella_migration.md`

### 3. Transfer veri
- YeniTeklif’te otel/transfer doldur → Transfer Takvimi satırları görünür

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
