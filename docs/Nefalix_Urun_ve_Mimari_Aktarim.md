# Nefalix Ürün + Mimari Aktarım Dokümanı

**Sürüm:** 1.0  
**Tarih:** 15 Temmuz 2026  
**Hedef okuyucu:** Arif (Next.js altyapı geçişi) + iç ekip  
**Pilot klinik:** MediDent Kartal — `clinic_id`: `51738ea8-c12e-40ce-a0e2-42869496d76b`

---

## İçindekiler

1. [Karar ve roller](#0-karar-ve-roller)
2. [Sistem haritası](#1-sistem-haritası)
3. [Ortak kavramlar](#2-ortak-kavramlar)
4. [Müşteri CX suite](#3-müşteri-cx-suite)
5. [CRM ürünleri](#4-crm-ürünleri)
6. [Entegrasyonlar](#5-entegrasyonlar)
7. [Büyüme ve marka](#6-büyüme-ve-marka)
8. [Platform](#7-platform)
9. [Ekler](#8-ekler)
10. [Next.js geçiş sırası](#9-nextjs-geçiş-sırası)
11. [Olgunluk matrisi](#10-olgunluk-matrisi)

---

## 0. Karar ve roller

### Neden bu doküman var?

İş büyüdükçe mevcut stack’in baştan taşınması gerekebilir. Karar: **n8n + HTML/Vercel altyapısından Next.js altyapısına geçiş** hedefleniyor. Bu geçişte ürün mantığının eksik aktarılması (ör. Klinik CRM’de Dinamik Arama, NPS dallanması) zayıf ürün üretir. Bu doküman **işin ne olduğunu** tek kaynak olarak tanımlar.

### Bugün vs hedef

| Katman | Bugün | Hedef |
|--------|-------|-------|
| Public site + dashboard UI | `nefalix-landing` — statik HTML + Vercel serverless API | Next.js App Router (sayfalar + route handlers) |
| Otomasyon / iş akışları | n8n (VPS) + Python cron scriptleri | Next.js background jobs / route handlers / queue (kademeli) |
| Veri | Supabase (self-host VPS + REST) | Supabase kalır — tek doğruluk kaynağı |
| WhatsApp | Evolution API (pilot, WhatsApp Web protokolü) | Evolution veya Meta WABA — karar ayrı |
| AI | Vertex Gemini (GCP) | Aynı |

### Roller

| Rol | Kim | Sorumluluk |
|-----|-----|------------|
| PM / vibe coding / mimari | Bu taraf (Cursor + ekip) | İş kuralları, SOP, modül sınırları, bu doküman |
| Next.js uygulama | Arif | Bu dokümana göre Next.js’te gerçekleştirme |

**Kural:** Arif bu PDF/MD’yi okumadan kod yazmaya başlamasın. Paralel sessiz “ikinci codebase” kurulmaz.

### Okuma sırası

1. Ortak kavramlar (Bölüm 2)  
2. CX suite (Bölüm 3)  
3. CRM — Dashboard CX’ten ayrı (Bölüm 4)  
4. Entegrasyonlar (Bölüm 5)  
5. Büyüme + platform (Bölüm 6–7)  
6. Ekler + geçiş sırası (Bölüm 8–9)

---

## 1. Sistem haritası

### Canlı bileşenler

| Bileşen | Konum | URL / erişim |
|---------|-------|--------------|
| Public site + API | Vercel — `nefalix-landing` | https://nefalix.com |
| n8n + Evolution + Supabase | VPS `93.127.186.45` — `/opt/nefalix` | https://api.nefalixai.com |
| Pilot klinik verisi | Supabase tabloları | `clinic_id` ile scope |

### Veri merkezi: Supabase

Tüm modüller aynı DB’ye yazar/okur. n8n workflow’ları **ayrı ayrı** tutulur (monolith workflow önerilmez — bkz. `docs/ARCHITECTURE.md`). Next.js’te de **domain modülleri** tercih edilir; `api/blog.js` monolith’i taşınmamalı.

### Mimari özet

```
HBYS / WhatsApp / Google / Web
         │
         ▼
   n8n workflows (00–18) + Python crons
         │ read/write
         ▼
      SUPABASE ◄──── Vercel API (dashboard, CRM, blog, geo)
         │
         ▼
   Dashboard / Klinik CRM / Saha CRM / Marketing pages
```

### Üç ayrı ürün yüzeyi (karıştırma)

| Ürün | URL | Auth |
|------|-----|------|
| Klinik Dashboard (CX) | `/dashboard` | E-posta + şifre → `nefalix_session` cookie |
| Klinik CRM (Stella) | `/klinik-crm` | Kullanıcı kodu → `nefalix_clinic` cookie |
| Saha CRM (iç satış) | `/crm`, `/saha` | Kullanıcı kodu → `nefalix_crm` cookie |

---

## 2. Ortak kavramlar

### Multi-tenant: `clinic_id`

Her klinik/firma bir `clinics` satırı. Dashboard kullanıcıları `clinic_id` ile scope’lanır (`role: admin` tümünü görür). n8n webhook’ları gövdede `clinic_id` taşır.

### NPS skor bandı (hasta)

Kaynak: `directives/product_roadmap.md`, `directives/appointment_trigger.md`

1. Randevu biter → WhatsApp’ta **1–10** puan sorulur  
2. **8–10 (promoter):** Google yorum linki gönderilir  
3. **≤7 (detractor):** Google istenmez; şikayet formu + **yönetici WhatsApp alarmı**

**Senaryo:** Hasta 9 verdi → `flow=promoter` → Google Maps yorum URL’si WA ile gider. Hasta 5 verdi → `flow=detractor` → yönetici alarmı + inbox’ta `nps_alert` kaydı; Google linki yok.

### Onay-sonra-gönder (Estesoft pilot)

Medident’te NPS mesajı otomatik gitmez: Estesoft tamamlanan randevu → AI taslak → **dashboard Inbox’tan onay** → wf-08 → WhatsApp Gateway. `WHATSAPP_SEND_ENABLED=true` olmadan gönderim yapılmaz.

### WhatsApp güvenlik kapısı

- `WHATSAPP_SEND_ENABLED` — prod’da false iken mesaj loglanır ama gönderilmez  
- Rate limit: `WHATSAPP_MIN_INTERVAL_SEC`, `WHATSAPP_MAX_PER_HOUR`  
- Evolution pilot — resmi Meta WABA değil; ban/İYS riski klinikte

### İYS / KVKK

- `patients.iys_consent` alanı var  
- Yasal sayfalar: `/kvkk`, `/gizlilik-politikasi`, `/iys-izin`, `/veri-guvenligi`  
- Otomatik İYS API entegrasyonu **yok** (içerik + şema düzeyinde)

### Vercel Hobby kısıtı

CRM, blog, geo, social, saha CRM endpoint’leri tek function’a rewrite edilir (`vercel.json` → `/api/blog?action=...`). Next.js’te her domain kendi `app/api/...` route’una ayrılmalı.

---

## 3. Müşteri CX suite

Her modül aynı şablonda: Ne / Kim / Nasıl / İş kuralları / Veri / Akış / Teknik / Olgunluk / Next notu.

---

### 3.1 Feedback / Akıllı Geri Bildirim (NPS)

**Ne bu?** Randevu sonrası hasta memnuniyeti (1–10). Promoter’ları Google’a yönlendirir; detractor’ları içeride tutar ve yöneticiyi uyarır.

**Kim kullanır?** Hasta (WA); klinik yöneticisi (dashboard NPS sekmesi, alarm).

**Nasıl kullanılır?**
1. HBYS/Estesoft “randevu tamamlandı” sinyali gelir  
2. (Pilot) Inbox’ta NPS taslağı görünür → personel onaylar  
3. Hasta WA’da puanlar  
4. Skora göre Google linki veya kriz akışı işler  
5. Detractor için yönetici dashboard’dan `resolution` notu yazar (`api/nps/resolve.js`)

**İş kuralları**
- Skor 8–10 → promoter  
- Skor ≤7 → detractor, Google yok  
- `CLINIC_MANAGER_WHATSAPP` — düşük puan alarmı  
- Generic webhook: `POST .../webhook/nefalix/hbys/appointment-completed`

**Veri modeli**
- `patients`, `appointments`  
- `nps_responses`: `score`, `flow`, `patient_phone`, `resolution_status`, `manager_note`, `resolved_at`  
- `whatsapp_send_log` — gönderim izi  
- `inbox_messages` — `message_kind=nps_alert` (detractor alarmı)

**Akış**
```
Estesoft webhook / HBYS webhook / wf-12 poll
  → AI NPS metni (Vertex)
  → inbox draft veya wf-01 outbound
  → onay → wf-08 → wf-00 Evolution
  → hasta yanıtı → wf-01 skor parse
  → promoter: Google URL | detractor: alarm + şikayet formu
```

**Bugünkü teknik**
- wf-01 Feedback & Reviews Loop  
- wf-08 Inbox Yanıt Gönder  
- wf-12 Estesoft HBYS Adapter, wf-13 Estesoft Poll  
- `directives/estesoft_integration.md`, `directives/appointment_trigger.md`  
- `api/nps/resolve.js`

**Olgunluk:** **Canlı pilot** (Medident). Gönderim env kapısına bağlı.

**Next.js hedef notu:** Route handlers: HBYS webhook receiver, NPS state machine, onay kuyruğu. wf-01/08 mantığı TypeScript job’lara taşınır. Idempotency: `appointmentId` + `external_id` dedup.

---

### 3.2 Inbox (Omnichannel)

**Ne bu?** Gelen/giden mesajların tek panelde toplanması; AI taslak; WA cevap; Estesoft NPS taslakları da burada.

**Kim kullanır?** Klinik personel / yönetici.

**Nasıl kullanılır?**
1. Dashboard → Inbox sekmesi  
2. Gelen WA mesajı listelenir (wf-06 routing)  
3. Personel yanıt yazar → Gönder  
4. Estesoft NPS taslakları aynı listede onaylanır

**İş kuralları**
- `message_kind`: normal, `nps_alert`, vb.  
- Gönderim `N8N_INBOX_SEND_URL` → wf-08  
- `whatsapp_disabled` → 403, kullanıcıya “gönderim kapalı” mesajı  
- Rate limit → 429 + `retryAfterSec`

**Veri modeli**
- `inbox_messages`: `clinic_id`, `channel`, `direction`, `body`, `status`, `sender_phone`, `message_kind`

**Akış**
```
Evolution inbound → wf-06 (AI routing, lead upsert CRM)
Dashboard reply → api/inbox/send.js → wf-08 → wf-00
```

**Bugünkü teknik**
- wf-06, wf-08, wf-00, wf-15 (QR bağlantı)  
- `api/inbox/send.js`, `api/inbox/clear.js`

**Olgunluk:** **Canlı kısmi** — WhatsApp ana kanal; SMS/Telegram/omnichannel tam değil.

**Next.js hedef notu:** Real-time inbox (Supabase realtime veya polling). Send path Evolution adapter modülü. CRM lead upsert wf-06’dan ayrı domain event olmalı.

---

### 3.3 Google Review AI

**Ne bu?** Google Maps yorumlarını çeker, AI taslak yanıt üretir, yönetici onaylar.

**Kim kullanır?** Klinik yöneticisi.

**Nasıl kullanılır?**
1. wf-09 / cron — Places API sync  
2. wf-10 — düşük puanlar için AI taslak  
3. Dashboard → Reviews → düzenle → Onayla  
4. `api/reviews/approve.js` → wf-11

**İş kuralları**
- Places API son 5 yorum limiti  
- Rating ≤4 yeni yorum → otomatik Sentinel (wf-04) tetiklenebilir  
- GBP otomatik publish **yok** — panoya kopyala + Maps aç

**Veri modeli**
- `clinics.google_place_id`, `google_rating`, `google_review_count`  
- `google_reviews`: `draft_reply`, `status` (pending_approval → published)

**Akış**
```
sync (6h) → google_reviews insert
→ draft AI → dashboard onay → wf-11
```

**Bugünkü teknik**
- wf-02, wf-09, wf-10, wf-11  
- `execution/sync-google-reviews.py`, `execution/draft-google-reviews.py`  
- `directives/google_reviews_sync.md`

**Olgunluk:** **Canlı pilot** — sync + taslak + onay; otomatik GBP publish plan.

**Next.js hedef notu:** Cron → Next scheduled job veya VPS script kalır. Onay UI + webhook handler Next’te.

---

### 3.4 Inside eNPS

**Ne bu?** Çalışan bağlılık anketi (1–10), anonim.

**Kim kullanır?** Klinik çalışanları (teorik); yönetim raporu.

**Nasıl kullanılır?** Aylık cron (wf-03) → webhook yanıt → promoter ise Glassdoor teşviki / değilse yönetim raporu.

**İş kuralları** — Hasta NPS ile aynı skor bandı mantığı benzer.

**Veri modeli** — `enps_responses`: `score`, `department`, `feedback`

**Akış** — wf-03: Aylık Anket → eNPS Webhook → Supabase

**Bugünkü teknik** — wf-03, dashboard `enps` sekmesi

**Olgunluk:** **Pilot** — workflow + UI var; operasyonel derinlik hasta NPS kadar değil.

**Next.js hedef notu:** Düşük öncelik; delivery kanalı netleştirilmeden taşıma.

---

### 3.5 Sentinel (İtibar Koruma)

**Ne bu?** Marka mention’larını (şikayet siteleri) tarar, duygu/risk analizi, yöneticiye WA özeti.

**Kim kullanır?** Klinik yöneticisi.

**Nasıl kullanılır?** Otomatik sync → dashboard Sentinel sekmesi → kritik olanlar `alert_urgent`

**İş kuralları**
- Her mention sonrası yöneticiye WA: duygu, risk, özet, link  
- Kritik → `alert_urgent`  
- Pazarlama “Ekşi + web crawl” iddiası — **kod gerçeği:** Şikayetvar sync canlı (`wf-14`); genel web crawl kanıtı yok

**Veri modeli** — `reputation_mentions`, `clinics.sikayetvar_url`

**Akış**
```
wf-14 (4h) → HTML parse → wf-04 AI → Supabase + manager WA
```

**Bugünkü teknik**
- wf-04, wf-14, `execution/sync-sikayetvar.py`  
- `directives/sikayetvar_sync.md`

**Olgunluk:** **Kısmi canlı** — Şikayetvar evet; tam omnichannel mention hayır.

**Next.js hedef notu:** Scraper job ayrı servis kalabilir; analiz + notify Next’e.

---

### 3.6 Recall (Kayıp Hasta)

**Ne bu?** Uzun süredir gelmeyen hastaları bulup WA ile geri kazanma.

**Kim kullanır?** Klinik pazarlama / yönetici.

**Nasıl kullanılır?** Dashboard Recall sekmesi → kampanya listesi → (pilot) otomasyon tetikler

**İş kuralları** — `patients` + `appointments` üzerinden inaktivite hesabı

**Veri modeli** — `recall_campaigns`

**Akış** — wf-05: inactive query → AI mesaj → wf-00

**Bugünkü teknik** — wf-05, dashboard `recall` tab

**Olgunluk:** **Pilot / stub-leaning** — veri yoksa demo satırlar UI’da görünebilir.

**Next.js hedef notu:** İş kuralı netleştirilmeden prod kampanya açma. Query + consent (İYS) zorunlu.

---

### 3.7 Klinik Dashboard SaaS

**Ne bu?** CX modüllerinin tek paneli: NPS, Inbox, Reviews, eNPS, Sentinel, Recall, Firmalar, Billing, WhatsApp QR.

**Kim kullanır?** Klinik yöneticisi, Nefalix admin.

**Nasıl kullanılır?**
1. `/dashboard/login` — e-posta/şifre  
2. İlk girişte şifre kurulumu (`setup-password`)  
3. Sekmeler arası gezinme; firma admin’i WhatsApp QR bağlar

**İş kuralları**
- Auth: `dashboard_users` (Supabase) veya `DASHBOARD_USERS` env JSON  
- `requireAuth` — `nefalix_session` HMAC cookie, 7 gün  
- Veri: `N8N_DASHBOARD_URL` → wf-07 aggregate; yoksa 503  
- Metrikler: son 30 gün anket, ortalama NPS, Google yorum sayısı

**Veri modeli**
- `dashboard_users`, `clinics` (plan_tier, subscription_status, stripe_*), `firm_onboarding`

**Akış**
```
dashboard.js → wf-07 (n8n) → Supabase read
veya wf-16 proxy (Vercel → VPS Supabase)
```

**Bugünkü teknik**
- `dashboard.html`, `nefalix-dashboard.js`, `api/dashboard.js`, `api/auth.js`, `api/firms.js`  
- wf-07, wf-16

**Olgunluk:** **Canlı**

**Next.js hedef notu:** İlk taşınacak iskelet. Auth middleware + RLS-aware data layer. wf-07 aggregate’i Next server action’a.

---

## 4. CRM ürünleri

> **Uyarı:** Klinik CRM ve Saha CRM, Dashboard CX’ten tamamen ayrı ürünlerdir.

---

### 4.1 Klinik CRM (Stella mantığı)

**Ne bu?** Estesoft Stella iş mantığının Nefalix kopyası: lead → atama → not/segment → **Dinamik Arama** → randevu. Medident pilot için klinik operasyon aracı.

**Kim kullanır?** Klinik temsilcisi (`temsilci`), yönetici (`yonetici`).

**Nasıl kullanılır?**
1. `/klinik-crm` → kullanıcı **kodu** ile giriş (`crm_users` tablosu)  
2. **Lead listesi** — manuel kayıt veya web formu (`lead-intake`)  
3. Lead **atama** → `stage=danisan`, `next_call_date=bugün`  
4. **Not + segment** kaydı → `next_call_date` otomatik hesaplanır  
5. **Dinamik Arama** — bugün aranacaklar listesi  
6. **Randevu** oluştur/güncelle  
7. **Danışan kartı** — not geçmişi + randevular

**İş kuralları — Dinamik Arama (kritik)**

Cron **yok**. Mantık tamamen `next_call_date` alanına dayanır:

- Not kaydında segment seçilince:  
  `next_call_date = (not_tarihi || bugün) + segment.gun_offset`  
  (`gun_offset` minimum 1 gün)
- **Dinamik segment** (`show_in_dynamic=true`): Ulaşılamadı (+1), Teklif Verildi (+1), Takip (+2), Orta Vadede (+7)…  
- **Kapanış segmenti** (`show_in_dynamic=false`): Satıldı, Süreci Biten, Tedaviye Uygun Değil → `next_call_date=null`; bu üçünde ayrıca `status=arsiv`  
- Dinamik Arama sorgusu: `status=aktif AND next_call_date <= bugün`  
- Temsilci kendi atananlarını görür; yönetici `?all=1` ile hepsini  
- Havuz (`?pool=1`): `assigned_to IS NULL`

**İş kuralları — Atama**

- `assign` → `stage=danisan`, `assigned_to=user_id`, `next_call_date=bugün` (hemen arama listesine düşer)

**İş kuralları — Lead intake (public)**

- `POST /api/clinic/lead-intake` — oturum yok  
- Honeypot alanı (`website`) doluysa sessiz OK (bot)  
- Aynı telefon varsa `existing: true`, yeni insert yok

**Veri modeli**

| Tablo | Açıklama |
|-------|----------|
| `crm_users` | `kod`, `ad`, `rol`, `aktif` |
| `crm_segments` | `code`, `label`, `show_in_dynamic`, `gun_offset`, `sira` |
| `crm_contacts` | `stage` (lead/danisan), `status` (aktif/arsiv), `next_call_date`, `assigned_to`, … |
| `crm_contact_notes` | `body`, `segment_code`, `note_date` |
| `crm_appointments` | `start_at`, `hizmet`, `personel`, `durum`, … |

Erişim: `service_role` (RLS yok).

**Akış örneği**

Temsilci “Teklif Verildi” segmenti ile not kaydeder → `next_call_date = yarın` → yarın Dinamik Arama’da görünür → arama yapar → “Satıldı” seçer → `arsiv`, kuyruktan çıkar.

**Bugünkü teknik**
- `api/_lib/clinic-crm.js` — tüm iş mantığı  
- `vercel.json` rewrites → `api/blog?action=clinic-*`  
- `klinik-crm.html`  
- wf-06: WA inbound → CRM lead upsert (inbox ile kesişim)

**Olgunluk:** **P0 canlı** — lead, atama, dinamik arama, not, randevu. P1/P2 (kasa, teklif PDF, raporlar, WA panel) **plan**.

**Next.js hedef notu:** `app/(clinic-crm)/` ayrı layout + auth. `note-save` ve `dynamic` iş kuralları birebir taşınmalı — test: segment offset + arşiv. `blog.js` monolith’ten çıkar.

---

### 4.2 Saha CRM (iç satış)

**Ne bu?** Nefalix ekibinin saha satış pipeline’ı — hedef klinikler, notlar, randevular. Klinik CRM veya Dashboard değil.

**Kim kullanır?** Nefalix iç ekip (Abdülkadir, Enes, Kader, Destek).

**Nasıl kullanılır?**
1. `/crm` veya `/saha`  
2. Kullanıcı **kodu** ile giriş (sabit kullanıcı listesi — kod eşleşmesi)  
3. Klinik kartları, notlar, randevu — tüm state tek JSON blob  
4. Randevu oluştur/iptal → e-posta bildirimi (`crm-notify-randevu`)

**İş kuralları**
- State: `nefalix_state` tablosu `id=1`, `data` JSON, `rev` optimistic lock  
- Kaydet: `POST /api/crm/save` — tüm `data` gövdesi  
- Mail: `NEFALIX_INTERNAL_KEY` + webhook URL

**Veri modeli** — `nefalix_state (id, data jsonb, rev int)`

**Akış**
```
crm.html UI → crm-get / crm-save → Supabase nefalix_state
Randevu event → crm-notify-randevu → VPS mail script
```

**Bugünkü teknik**
- `api/blog.js` — CRM handlers (satır 12–18 kullanıcı listesi; **şifreler dokümanda yok**)  
- `crm.html`

**Olgunluk:** **Canlı** — basit JSON state, passwordless kod girişi.

**Next.js hedef notu:** Normalize edilmiş tablolar düşünülebilir (şu an tek JSON). Auth en azından env-based veya Supabase users’a taşınmalı — hardcoded kullanıcı listesi kaldırılmalı.

---

## 5. Entegrasyonlar

### 5.1 Evolution WhatsApp

**Ne:** WhatsApp Web protokolü ile mesaj gönder/al (pilot).  
**Kurulum:** `directives/evolution_setup.md`, `execution/setup-evolution.sh`  
**Dashboard QR:** `api/whatsapp/connect.js` → wf-15  
**Gateway:** wf-00 — tüm outbound buradan  
**Olgunluk:** Pilot — Meta WABA değil.  
**Next:** Evolution client adapter modülü; multi-tenant `instanceName` per `clinic_id`.

### 5.2 Estesoft HBYS (Medident)

**Ne:** Stella REST + webhook → tamamlanan randevu → NPS taslak.  
**Webhook:** `POST .../webhook/nefalix/estesoft/webhook`  
**Yedek poll:** wf-13 (10 dk)  
**Adapter:** wf-12  
**Onay:** Dashboard inbox → wf-08  
**Kaynak:** `directives/estesoft_integration.md`  
**Next:** Webhook receiver + idempotent appointment dedup (`seed-estesoft-completed-dedup.py` mantığı).

### 5.3 Generic HBYS webhook

**Ne:** Yazılımdan bağımsız sözleşme.  
**URL:** `POST .../webhook/nefalix/hbys/appointment-completed`  
**Minimum gövde:** `clinic_id`, `patientName`, `patientPhone`, `appointmentId`, URL’ler  
**Kaynak:** `directives/appointment_trigger.md`  
**Next:** Tek OpenAPI spec + adapter pattern per CRM.

### 5.4 Google Places

**Ne:** Yorum sync — `execution/sync-google-reviews.py`, wf-09  
**Env:** `GOOGLE_PLACES_API_KEY`  
**Next:** Scheduled job; migration `clinic_google_place_ids` korunur.

### 5.5 Şikayetvar

**Ne:** Marka sayfası scrape → wf-04  
**Alan:** `clinics.sikayetvar_url`  
**Next:** Scraper izole servis; rate limit + ToS dikkat.

### 5.6 Hotel PMS (plan)

Cloudbeds / TheClico — `directives/integrations_hotels.md` — **sadece plan**, kod yok.

---

## 6. Büyüme ve marka

### 6.1 Günlük Blog

**Ne:** Vertex ile Türkçe SEO yazıları → `blog_posts` → `/blog/:slug`  
**UI:** `blog.html`, liste API  
**Render:** `api/blog.js` — `action=render`, SSR HTML  
**Üretim:** Workspace’te `publish-daily-blog.py` git status’ta görülmüş; canlıda VPS cron olabilir — **doğrulanmadı**  
**Tablolar:** `blog_posts`, `blog_images` (migration git’te olabilir)  
**Olgunluk:** Public sayfa + API **canlı**; üretim pipeline ortamda doğrulanmalı.  
**Next:** `app/blog/[slug]/page.tsx` + MDX/HTML render; cron → Next veya VPS.

### 6.2 GEO / Prominence (AI alıntı)

**Ne:** Günlük public cevap sayfaları — ChatGPT/Perplexity/Gemini alıntısı için  
**URL:** `/geo/:date` (YYYY-MM-DD)  
**API:** `api/blog.js` — `geo-list`, `geo-render`, `geo-sitemap`  
**Destek:** `geo.html`, `llms.txt`, sitemap  
**Olgunluk:** Render **canlı**; günlük üretim script workspace’te eksik olabilir.  
**Next:** Static generation + `geo_daily_runs` tablosu (varsa) entegrasyonu.

### 6.3 Sosyal medya

**Ne:** Görsel + caption üret → onay → yayın  
**Directive eski:** Manuel Drive yükleme anlatıyor (`social_media_automation.md`)  
**Kod gerçeği:**
- `social-generate-next.py` — GPT görsel, `social_posts` tablosu  
- `social-publish-approved.py` — IG/LinkedIn (env yoksa skip)  
- `api/social/approve`, `reject` → `blog.js`  
- wf-17 — legacy; Python primary  
**Tablo:** `social_posts` (migration `20260629130000`)  
**Olgunluk:** Üretim **canlı**; otomatik IG env-gated.  
**Next:** Onay UI + publish job; storage Supabase.

### 6.4 Web chatbot

**Ne:** Site ziyaretçisi AI sohbet  
**Akış:** `nefalix-chat.js` → `api.nefalixai.com` webhook → wf web-chatbot  
**Kaynak:** `directives/chat_tunnel.md`  
**Olgunluk:** **Canlı**  
**Next:** Next route proxy veya doğrudan n8n webhook (geçici).

### 6.5 YouTube GEO

**Ne:** Kanal açıklamaları / GEO pack — `youtube-channel.js`, `api/blog?action=youtube-list`  
**Olgunluk:** Liste API var; tam otomasyon doğrulanmadı.

---

## 7. Platform

### 7.1 Auth ve onboarding

- Dashboard: `api/auth.js` — login, logout, setup-password, session verify  
- Firm onboarding: `api/firms.js`, migration `firm_onboarding`  
- Dev bypass: `DEV_DASHBOARD_EMAIL` / `DEV_DASHBOARD_PASSWORD` (prod’da kapalı)

### 7.2 Billing

**Kod:** `api/billing.js`  
- **PayTR:** `startPaytrIframe` — `PAYTR_*` env; callback `paytr-callback`  
- **Stripe:** checkout session + webhook — `STRIPE_*` env  
- Fiyat hesabı: sektör çarpanı, personel çarpanı, Sentinel/Recall eklentileri  
**Olgunluk:** Kod **canlı**; prod’da hangi ödeme aktif **doğrulanmadı** (handoff: PayTR öncelik).

### 7.3 Supabase proxy (wf-16)

Vercel’den VPS Supabase’e erişim — `NEFALIX_INTERNAL_KEY`  
Dashboard firm kayıtları vb.

### 7.4 Güvenlik

`directives/security.md`, `directives/vps_setup.md` — secret rotasyon, VPS harden, WA/İYS riskleri.

### 7.5 Vertex AI

`directives/vertex_ai_setup.md`, `execution/vertex_gemini.py` — Gemini çağrıları, GCP kredi.

### 7.6 AI budget

`api/ai-budget.js` — dashboard’da AI kullanım göstergesi (varsa).

---

## 8. Ekler

### 8.1 Workflow envanteri

| Dosya | Ad | Amaç |
|-------|-----|------|
| nefalix-00 | WhatsApp Gateway | Tüm outbound WA |
| nefalix-01 | Feedback & Reviews Loop | NPS akışı |
| nefalix-02 | Google Review AI Agent | Gelen yorum AI |
| nefalix-03 | Inside eNPS | Çalışan anketi |
| nefalix-04 | Sentinel İtibar Koruma | Mention AI + alarm |
| nefalix-05 | Recall Kayıp Hasta | Geri kazanım |
| nefalix-06 | Inbox Mesaj Yönlendirme | Inbound routing |
| nefalix-07 | Dashboard API | Panel aggregate |
| nefalix-08 | Inbox Yanıt Gönder | Outbound + onaylı NPS |
| nefalix-09 | Google Yorum Senkronu | Places sync |
| nefalix-10 | Google Yorum Taslak AI | Draft replies |
| nefalix-11 | Google Yorum Onayla | Publish onay |
| nefalix-12 | Estesoft HBYS Adapter | Randevu → NPS draft |
| nefalix-13 | Estesoft Randevu Poll | Yedek poll |
| nefalix-14 | Şikayetvar Senkron | Scrape → Sentinel |
| nefalix-15 | WhatsApp QR Bağlantı | Evolution QR |
| nefalix-16 | Supabase Proxy (Vercel) | TR DB tunnel |
| nefalix-17 | Sosyal Medya Otomasyon | Legacy cron |
| nefalix-web-chatbot | Web Chatbot | Site chat |
| nefalix-telegram-chatbot | Telegram Chatbot | Düşük öncelik |

### 8.2 Supabase tablo → modül

| Tablo | Modül |
|-------|-------|
| clinics, patients, appointments | Platform |
| nps_responses | Feedback |
| inbox_messages | Inbox |
| google_reviews | Google AI |
| enps_responses | eNPS |
| reputation_mentions | Sentinel |
| recall_campaigns | Recall |
| dashboard_users, clinics billing cols | Dashboard |
| whatsapp_send_log | WA gateway |
| social_posts | Sosyal |
| blog_posts | Blog |
| nefalix_state | Saha CRM |
| crm_* | Klinik CRM |
| automation_events | Tüm workflow log |

### 8.3 Landing route / API özeti

**Sayfalar (rewrite):** `/dashboard`, `/klinik-crm`, `/crm`, `/blog`, `/geo`, `/fiyatlar`, yasal sayfalar…

**Bağımsız API dosyaları:** `auth.js`, `dashboard.js`, `billing.js`, `firms.js`, `inbox/*`, `nps/resolve.js`, `reviews/approve.js`, `whatsapp/*`, `ai-budget.js`

**Monolith (`api/blog.js`):** blog, geo, youtube, clinic-*, crm-*, social approve/reject

### 8.4 Bilinçli kapsam dışı

- **Insights** modülü — ürün kodu yok  
- GBP otomatik yanıt yayını  
- Meta WABA resmi API (Evolution pilot aşamasında)  
- Otomatik İYS API  
- Otel PMS entegrasyonu (plan only)

---

## 9. Next.js geçiş sırası

1. **Auth + firm model + dashboard iskeleti** — session, multi-tenant, wf-07 yerine Next data layer  
2. **Inbox + NPS** — onay-sonra-gönder, skor state machine, Evolution adapter  
3. **Google reviews** — sync job + onay UI  
4. **Klinik CRM** — `clinic-crm.js` mantığı birebir; ayrı route group  
5. **Saha CRM** — state model kararı (JSON vs normalize)  
6. **Sentinel + Recall**  
7. **Blog + GEO + Social + Chatbot**  
8. **n8n kademeli kapatma** — modül modül; cutover checklist ayrı proje

Her modülde taşınacaklar: UI sayfaları, API route handlers, background jobs, env contract. Geçici n8n’de kalabilecekler: ağır scraper, Evolution bridge (kısa vade).

---

## 10. Olgunluk matrisi

| Modül | Olgunluk | Not |
|-------|----------|-----|
| Dashboard CX | Canlı | wf-07 proxy bağımlı |
| Feedback / NPS | Canlı pilot | WA env kapısı |
| Inbox | Kısmi canlı | WA only |
| Google Review AI | Canlı pilot | Auto-publish yok |
| eNPS | Pilot | Zayıf operasyon |
| Sentinel | Kısmi | Şikayetvar evet, Ekşi hayır |
| Recall | Pilot/stub | Demo veri riski |
| Klinik CRM | P0 canlı | P1/P2 yok |
| Saha CRM | Canlı | JSON blob, kod auth |
| Evolution WA | Pilot | Ban riski |
| Estesoft | Canlı pilot | Onaylı gönderim |
| Blog / GEO render | Canlı | Üretim cron doğrulanmalı |
| Sosyal | Canlı | IG env-gated |
| Billing PayTR/Stripe | Kod hazır | Prod aktif doğrulanmadı |
| Hotel PMS | Plan | — |
| Insights | Yok | Pazarlama only |

---

## Doküman bakımı

- Tek kaynak: bu dosya + PDF türevi  
- Directive ile çelişki → kod gerçeği öncelikli, directive güncellenmeli  
- Secret/şifre bu dokümanda **asla** tutulmaz  
- Değişiklik sonrası: MD güncelle → PDF yeniden üret → Arif’e yeni sürüm

**Son güncelleme:** 2026-07-15 — sürüm 1.0
