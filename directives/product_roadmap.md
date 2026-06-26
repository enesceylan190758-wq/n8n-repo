# Nefalix AI — MVP Geliştirme & Deployment Yol Haritası

> **Kapsam:** Next.js (Frontend) · Supabase/PostgreSQL (Backend) · FastAPI (MCP Server & AI İşleme) · n8n (Otomasyon)
> **Mimari felsefe:** One Dataset, Every Layer — tek veri modeli, 4 farklı tüketici katmanı.
> **Son güncelleme:** 2026-06-26

---

## Mevcut Durum Özeti (Baseline)

| Bileşen | Durum | Detay |
|---------|-------|-------|
| Supabase şeması | ✅ Canlı | 20+ migration, pilot UUID sabit |
| n8n workflow'ları | ✅ Canlı | NPS, Google Reviews, Inbox, Sentinel |
| WhatsApp (Evolution) | ✅ Aktif | Inbound/outbound, rate-limit korumalı |
| Şikayetvar sync | ✅ Aktif | `sikayetvar_sync` workflow |
| Dashboard UI | ⏳ Statik HTML | `nefalix-site-v2/` — Next.js'e taşınacak |
| FastAPI MCP Server | ❌ Yok | Sprint 2'de kurulacak |
| AI Readiness Skoru | ❌ Yok | Sprint 3'te eklenecek (yeni tablolar) |
| Stripe Billing | 🏗️ Şema var | `dashboard_users` + `clinics.stripe_*` — entegrasyon Sprint 4 |

---

## Mimari Harita

```
┌─────────────────────────────────────────────────────────────┐
│                     INSIGHTS LAYER                          │
│            Next.js 14 App Router (Vercel)                   │
│   /dashboard · /locations · /ai-score · /executive-summary  │
└────────────────────────┬────────────────────────────────────┘
                         │ REST / Server Actions
┌────────────────────────▼────────────────────────────────────┐
│                   HEADLESS LAYER (MCP)                      │
│              FastAPI + Custom MCP Server                    │
│     /mcp/context · /ai/summary · /ai/audit · /ai/score     │
└────────────────────────┬────────────────────────────────────┘
                         │ Supabase Client (service_role)
┌────────────────────────▼────────────────────────────────────┐
│                  UNIFIED DATA LAYER                         │
│            Supabase / PostgreSQL (canlı)                    │
│  clinics · locations · ai_readiness_scores ·                │
│  operational_sentiment · nps_responses · google_reviews ·   │
│  inbox_messages · enps_responses · reputation_mentions      │
└────────────────────────┬────────────────────────────────────┘
                         │ Webhook / Cron / API
┌────────────────────────▼────────────────────────────────────┐
│              EXECUTION & AGENTIC LAYER                      │
│                   n8n (Cloud + Docker)                      │
│  wf-01 NPS · wf-04 Sentinel · wf-09/10/11 Reviews ·        │
│  wf-audit (yeni) · wf-board-summary (yeni)                  │
└─────────────────────────────────────────────────────────────┘
```

---

## Sprint Planı

### Sprint 0 — Altyapı Temeli (Önceden tamamlanmış + doğrulama)

**Hedef:** Tüm servisler ayakta, CI/CD hazır, secrets yönetimi kurulu.

**Görevler:**

- [x] Supabase projesi canlı, migration pipeline çalışıyor
- [x] n8n Cloud: `enkahealthisterr.app.n8n.cloud` aktif
- [x] Evolution API (WhatsApp) Docker üzerinde çalışıyor
- [ ] **Next.js projesi oluştur:** `npx create-next-app@latest nefalix-dashboard --typescript --tailwind --app`
- [ ] **FastAPI projesi oluştur:** `fastapi-mcp/` klasörü, `pyproject.toml` ile
- [ ] **Vercel bağlantısı:** Next.js repo → Vercel otomatik deploy
- [ ] **GitHub Actions:** `supabase db push` → main merge'de migration otomatik çalışsın
- [ ] **Secrets:** Vercel env + GitHub Secrets → `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `OPENAI_API_KEY`

**Ortam değişkenleri (tüm servisler için):**

```bash
SUPABASE_URL=https://<project>.supabase.co
SUPABASE_ANON_KEY=...
SUPABASE_SERVICE_KEY=...          # FastAPI ve n8n için
OPENAI_API_KEY=...                # veya VERTEX_AI credentials
N8N_WEBHOOK_BASE=https://enkahealthisterr.app.n8n.cloud/webhook
NEXTAUTH_SECRET=...               # Next.js auth
STRIPE_SECRET_KEY=...             # Billing (Sprint 4)
STRIPE_WEBHOOK_SECRET=...
```

---

### Sprint 1 — Veri Katmanı Genişletme (Supabase)

**Hedef:** Ürün blueprint'indeki eksik tablolar eklenir; mevcut tablolar GEO/AEO ihtiyaçlarına göre genişletilir.

#### 1A — Yeni Tablolar (migration dosyaları)

**`locations` tablosu** (blueprint'teki çok-şubeli yapı — mevcut `clinics`'ten farklı):

```sql
-- migration: 20260626130000_locations_geo.sql
CREATE TABLE IF NOT EXISTS locations (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  clinic_id     UUID REFERENCES clinics(id) ON DELETE CASCADE,
  business_name VARCHAR(255) NOT NULL,
  branch_name   VARCHAR(255),
  website_url   TEXT,
  nap_address   TEXT,
  nap_phone     VARCHAR(50),
  google_place_id TEXT,
  google_business_status VARCHAR(50) DEFAULT 'Unclaimed'
    CHECK (google_business_status IN ('Claimed','Unclaimed','Verified','Suspended')),
  facebook_business_status VARCHAR(50),
  created_at    TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_locations_clinic ON locations(clinic_id);
```

**`ai_readiness_scores` tablosu** (GEO/AEO skoru):

```sql
-- migration: 20260626140000_ai_readiness_scores.sql
CREATE TABLE IF NOT EXISTS ai_readiness_scores (
  id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  location_id           UUID REFERENCES locations(id) ON DELETE CASCADE,
  overall_score         INT CHECK (overall_score BETWEEN 0 AND 100),
  discoverability_score INT,  -- Bot erişilebilirliği, sayfa hızı
  answer_readiness_score INT, -- LLM için alıntılanabilir metin, FAQ yapısı
  trust_signals_score   INT,  -- Yorum hızı, otorite, güncellik
  llm_txt_present       BOOLEAN DEFAULT FALSE,
  schema_markup_valid   BOOLEAN DEFAULT FALSE,
  nap_consistent        BOOLEAN DEFAULT FALSE,
  page_speed_score      INT,
  grade                 CHAR(1) CHECK (grade IN ('A','B','C','D')),
  audit_details         JSONB DEFAULT '{}',
  audit_date            TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_ai_readiness_location ON ai_readiness_scores(location_id, audit_date DESC);
```

**`operational_sentiment` tablosu** (İç-Dış korelasyon):

```sql
-- migration: 20260626150000_operational_sentiment.sql
CREATE TABLE IF NOT EXISTS operational_sentiment (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  location_id         UUID REFERENCES locations(id) ON DELETE CASCADE,
  period              VARCHAR(10),            -- 'Q2_2026'
  patient_star_rating NUMERIC(3,2),
  negative_review_pct INT,
  staff_pulse_score   INT,
  enps_score          INT,
  burnout_rate        INT,
  turnover_rate       INT,
  correlation_score   NUMERIC(4,3),           -- Hesaplanan korelasyon katsayısı
  executive_summary   TEXT,                   -- AI-generated board summary
  updated_at          TIMESTAMPTZ DEFAULT now()
);
```

#### 1B — Mevcut Tablolara Eklemeler

```sql
-- clinics tablosuna GEO alanları
ALTER TABLE clinics
  ADD COLUMN IF NOT EXISTS llms_txt_url TEXT,
  ADD COLUMN IF NOT EXISTS schema_org_type TEXT DEFAULT 'LocalBusiness',
  ADD COLUMN IF NOT EXISTS geo_grade CHAR(1);

-- google_reviews tablosuna AEO alanları
ALTER TABLE google_reviews
  ADD COLUMN IF NOT EXISTS quote_ready_passage TEXT,  -- LLM alıntısı için optimize metin
  ADD COLUMN IF NOT EXISTS answer_quality_score INT;
```

#### 1C — RLS Politikaları

```sql
-- dashboard_users kendi clinic_id'sine ait verileri görebilir
ALTER TABLE ai_readiness_scores ENABLE ROW LEVEL SECURITY;
CREATE POLICY "manager_reads_own_location"
  ON ai_readiness_scores FOR SELECT TO authenticated
  USING (
    location_id IN (
      SELECT l.id FROM locations l
      JOIN dashboard_users du ON du.clinic_id = l.clinic_id
      WHERE du.id = auth.uid()
    )
  );
```

**Sprint 1 Çıktısı:** 3 yeni tablo, mevcut tablolara 6 yeni kolon, RLS tamamlandı.

---

### Sprint 2 — FastAPI MCP Server

**Hedef:** LLM'lerin ve internal agent'ların Nefalix verisine güvenli, yapılandırılmış erişimi.

**Proje yapısı:**

```
fastapi-mcp/
├── main.py                  # FastAPI app entry
├── routers/
│   ├── mcp.py               # /mcp/context endpoint (MCP Protocol)
│   ├── ai.py                # /ai/summary · /ai/audit · /ai/score
│   ├── webhooks.py          # n8n → FastAPI webhook alıcıları
│   └── health.py
├── services/
│   ├── supabase_client.py   # supabase-py, service_role
│   ├── openai_service.py    # Structured output (GPT-4o / Claude)
│   ├── audit_service.py     # llms.txt + Schema.org checker
│   └── correlation_service.py  # İç-dış korelasyon hesabı
├── models/
│   ├── schemas.py           # Pydantic modeller
│   └── mcp_protocol.py      # MCP mesaj formatları
├── Dockerfile
└── pyproject.toml
```

#### 2A — Temel API Uçları (İlk Sprint'te Açılacaklar)

| Method | Endpoint | Açıklama | Öncelik |
|--------|----------|----------|---------|
| GET | `/health` | Servis durumu | P0 |
| GET | `/mcp/context/{clinic_id}` | Klinik bağlam paketi — LLM'e beslenecek | P0 |
| POST | `/ai/audit` | Web sitesi teknik denetimi (llms.txt, Schema.org, NAP) | P0 |
| POST | `/ai/score` | AI Readiness skoru hesapla → DB'ye yaz | P0 |
| POST | `/ai/summary` | CSV/NPS upload → board-ready özet üret | P1 |
| GET | `/ai/executive/{clinic_id}` | Kaydedilmiş yönetici özetini getir | P1 |
| POST | `/ai/correlate` | Staff eNPS ↔ hasta yıldız korelasyonu | P1 |
| POST | `/webhooks/n8n` | n8n'den gelen event'leri işle | P0 |

#### 2B — `/mcp/context` Endpoint Detayı

Bu endpoint, AI chat/voice agent'larına gerçek zamanlı klinik bağlamı enjekte eder:

```python
# routers/mcp.py
@router.get("/context/{clinic_id}")
async def get_mcp_context(clinic_id: str) -> MCPContextResponse:
    """
    LLM'e beslenecek yapılandırılmış bağlam paketi.
    Kullanım: Web chatbot, WhatsApp bot, Cursor MCP bağlantısı.
    """
    return {
        "clinic": await get_clinic_profile(clinic_id),
        "recent_reviews": await get_recent_reviews(clinic_id, limit=5),
        "nps_summary": await get_nps_summary(clinic_id, days=30),
        "ai_readiness": await get_latest_ai_score(clinic_id),
        "open_complaints": await get_open_inbox(clinic_id),
        "executive_alerts": await get_alerts(clinic_id),
        "metadata": {
            "generated_at": datetime.utcnow().isoformat(),
            "context_version": "1.0"
        }
    }
```

#### 2C — `/ai/audit` Teknik Denetim Servisi

```python
# services/audit_service.py
async def run_technical_audit(website_url: str) -> AuditResult:
    checks = await asyncio.gather(
        check_llms_txt(website_url),          # GET /llms.txt → 200?
        check_robots_txt(website_url),         # AI bot erişimi engellendi mi?
        check_schema_org(website_url),         # LocalBusiness JSON-LD geçerli mi?
        check_nap_consistency(website_url),    # NAP tutarlı mı?
        check_page_speed(website_url),         # Core Web Vitals
        check_faq_structure(website_url),      # FAQ Schema var mı?
    )
    score = calculate_weighted_score(checks)
    grade = score_to_grade(score)  # A/B/C/D
    return AuditResult(checks=checks, score=score, grade=grade)
```

#### 2D — Board-Ready Summarizer

```python
# services/openai_service.py
async def generate_board_summary(
    clinic_id: str,
    period: str,
    enps_data: list[dict],
    review_data: list[dict]
) -> str:
    """Claude 3.5/4.6 Sonnet ile structured output."""
    prompt = build_board_prompt(enps_data, review_data)
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    summary = response.choices[0].message.content
    # operational_sentiment tablosuna kaydet
    await save_executive_summary(clinic_id, period, summary)
    return summary
```

**Sprint 2 Çıktısı:** 8 endpoint, MCP protokol desteği, teknik audit servisi, AI özet motoru.

---

### Sprint 3 — Next.js Dashboard (Frontend)

**Hedef:** Klinik yöneticilerinin veriyi izleyeceği, aksiyonları onaylayacağı SaaS panosu.

**Proje yapısı (`app/` router):**

```
nefalix-dashboard/
├── app/
│   ├── (auth)/
│   │   ├── login/page.tsx          # Magic link / JWT login
│   │   └── setup/[token]/page.tsx  # dashboard_users.setup_token akışı
│   ├── (dashboard)/
│   │   ├── layout.tsx              # Sidebar + top nav
│   │   ├── page.tsx                # Ana KPI özeti
│   │   ├── reviews/page.tsx        # Google yorum onay akışı
│   │   ├── inbox/page.tsx          # WhatsApp + Web chat birleşik gelen kutusu
│   │   ├── nps/page.tsx            # NPS dağılımı + detractor alarmları
│   │   ├── ai-score/page.tsx       # AI Readiness skoru + grade kartı
│   │   ├── executive/page.tsx      # Board-ready özet + korelasyon grafikleri
│   │   └── settings/page.tsx       # Klinik profil, kullanıcı yönetimi
│   └── api/
│       ├── auth/[...nextauth]/route.ts
│       ├── reviews/approve/route.ts   # → n8n webhook tetikler
│       ├── upload/enps/route.ts       # CSV upload → FastAPI /ai/summary
│       └── stripe/webhook/route.ts    # Stripe event işleme
├── components/
│   ├── ui/                         # shadcn/ui bileşenleri
│   ├── charts/
│   │   ├── CorrelationChart.tsx    # eNPS ↔ Yıldız korelasyon grafiği
│   │   ├── NpsTrendChart.tsx
│   │   └── AiScoreGauge.tsx
│   ├── cards/
│   │   ├── KpiCard.tsx
│   │   ├── AlertCard.tsx           # Grade D uyarısı
│   │   └── ExecutiveSummaryCard.tsx
│   └── reviews/
│       ├── ReviewApprovalRow.tsx
│       └── DraftEditor.tsx         # AI draft düzenleme + onay
└── lib/
    ├── supabase/
    │   ├── client.ts               # Browser client (anon key)
    │   └── server.ts               # Server client (service key)
    ├── mcp-client.ts               # FastAPI MCP calls
    └── n8n-client.ts               # Webhook trigger'ları
```

#### 3A — İlk Açılacak Sayfalar (MVP Slice)

**1. Ana Dashboard (`/`):**

```typescript
// app/(dashboard)/page.tsx
// Server Component — veri sunucu tarafında çekilir

const kpis = await Promise.all([
  supabase.from('nps_responses').select('score').eq('clinic_id', clinicId)
    .gte('created_at', last30days),
  supabase.from('google_reviews').select('rating, status').eq('clinic_id', clinicId),
  supabase.from('inbox_messages').select('id, status').eq('clinic_id', clinicId)
    .eq('status', 'open'),
  fetch(`${MCP_URL}/mcp/context/${clinicId}`).then(r => r.json())
])
```

Gösterilen metrikler:
- Ortalama NPS (son 30 gün) + trend oku
- Google yorum ortalaması + onay bekleyenler
- Açık inbox mesajları
- AI Readiness Grade kartı (A/B/C/D)
- Kritik uyarı listesi

**2. AI Score Sayfası (`/ai-score`):**

```typescript
// Otomatik audit tetikleme + skor gösterimi
// Her sayfaya girişte son audit tarihi kontrol edilir
// 7 günden eskiyse → FastAPI /ai/audit çağrılır
```

Gösterilenler:
- Genel skor gauge (0-100)
- Alt skorlar: Discoverability · Answer Readiness · Trust Signals
- Checklist: llms.txt ✅/❌ · Schema.org ✅/❌ · NAP tutarlılığı ✅/❌
- Öneri listesi (AI-generated, önceliklendirilmiş)

**3. Executive Summary (`/executive`):**

```typescript
// Korelasyon grafiği: X=enps_score, Y=patient_star_rating
// Her çeyrek için bir nokta, trend çizgisi
// CSV upload → /api/upload/enps → FastAPI /ai/summary
```

#### 3B — Bileşen Kütüphanesi

```bash
# Kurulum
npx shadcn@latest init
npx shadcn@latest add card badge button table alert dialog
npm install recharts @tanstack/react-table date-fns
npm install @supabase/ssr @supabase/supabase-js
npm install next-auth@beta
```

**Sprint 3 Çıktısı:** 6 dashboard sayfası, KPI kartları, korelasyon grafiği, yorum onay akışı, CSV upload.

---

### Sprint 4 — n8n Otomasyon Genişletme

**Hedef:** Yeni iş kurallarını ve GEO/AEO akışlarını n8n workflow'larına entegre et.

#### 4A — Yeni Workflow'lar

| Workflow | Tetikleyici | Akış | Çıktı |
|----------|-------------|------|-------|
| `wf-audit-cron` | Her Pazartesi 09:00 | Tüm `locations` → FastAPI `/ai/audit` → DB'ye yaz → Grade D ise alert | AI skor güncellendi |
| `wf-alert-engine` | DB trigger (Realtime) | `ai_readiness_scores.grade = 'D'` → Yönetici WhatsApp + webhook | Alarm gönderildi |
| `wf-board-summary` | Ayda 1 cron | `operational_sentiment` → FastAPI `/ai/summary` → DB kaydet | Yönetici PDF/özet |
| `wf-llms-txt-patch` | Manuel / webhook | Grade D lokasyon → `llms.txt` şablon üret → repo'ya PR | Teknik düzeltme |
| `wf-nap-checker` | Haftada 1 | `locations.nap_address` → Google Places karşılaştır → uyumsuzluk alarmı | NAP raporu |

#### 4B — Alert Öncelik Motoru (wf-alert-engine)

```javascript
// n8n Function node
const grade = $input.item.json.grade;
const overall = $input.item.json.overall_score;

let priority, channel;
if (grade === 'D' || overall < 30) {
  priority = 'CRITICAL';
  channel = ['whatsapp', 'email', 'slack'];
} else if (grade === 'C' || overall < 60) {
  priority = 'TOP_PRIORITY';
  channel = ['whatsapp'];
} else {
  priority = 'MONITOR';
  channel = ['email'];
}

return [{ priority, channel, location_id: $input.item.json.location_id }];
```

#### 4C — `wf-board-summary` Akışı

```
Cron (ay başı)
  → Supabase: operational_sentiment son 3 ay çek
  → Supabase: nps_responses + enps_responses ortalamaları çek
  → FastAPI POST /ai/correlate → correlation_score al
  → FastAPI POST /ai/summary → board özeti üret
  → Supabase: operational_sentiment.executive_summary güncelle
  → Yönetici WhatsApp: "Aylık yönetici raporunuz hazır 📊"
  → Dashboard bildirim (Supabase Realtime)
```

**Sprint 4 Çıktısı:** 5 yeni workflow, otomatik audit cron, Grade D alarm motoru, aylık board özeti.

---

### Sprint 5 — GEO/AEO Teknik Katman

**Hedef:** AI arama motorlarında görünürlük (ChatGPT, Gemini, Perplexity).

#### 5A — `llms.txt` Generator

```python
# services/llms_txt_service.py
async def generate_llms_txt(clinic_id: str) -> str:
    clinic = await get_clinic(clinic_id)
    reviews = await get_top_reviews(clinic_id, limit=10)  # En yüksek puanlı
    faqs = await get_faqs(clinic_id)

    return f"""# {clinic['name']}

## About
{clinic['description']}

## Services
{format_services(clinic['services'])}

## Patient Reviews (Summary)
{format_review_quotes(reviews)}

## Frequently Asked Questions
{format_faqs(faqs)}

## Contact
Address: {clinic['nap_address']}
Phone: {clinic['nap_phone']}
Website: {clinic['website_url']}
"""
```

#### 5B — Schema.org JSON-LD Injector

```typescript
// Lokasyon sayfaları için otomatik schema üretimi
export function generateLocalBusinessSchema(location: Location) {
  return {
    "@context": "https://schema.org",
    "@type": location.schema_org_type || "LocalBusiness",
    "name": location.business_name,
    "address": {
      "@type": "PostalAddress",
      "streetAddress": location.nap_address,
      "telephone": location.nap_phone
    },
    "url": location.website_url,
    "aggregateRating": {
      "@type": "AggregateRating",
      "ratingValue": location.avg_rating,
      "reviewCount": location.review_count
    },
    "hasMap": location.google_maps_url
  }
}
```

#### 5C — Quote-Ready Content Pipeline

```
n8n wf-quote-ready:
  Google Reviews → En iyi 3 alıntı seç (sentiment pozitif + özgün)
  → GPT-4o ile yeniden yaz (answer-optimized, 2-3 cümle)
  → google_reviews.quote_ready_passage güncelle
  → llms.txt'ye ekle
  → FastAPI /ai/score → answer_readiness_score güncelle
```

**Sprint 5 Çıktısı:** `llms.txt` otomasyonu, Schema.org injector, quote-ready içerik pipeline.

---

### Sprint 6 — Billing & Multi-Tenant SaaS

**Hedef:** Stripe entegrasyonu, çok-kiracılı yapı, self-serve onboarding.

#### 6A — Plan Katmanları

| Plan | Lokasyon | AI Score | Board Summary | MCP Erişimi | Fiyat |
|------|----------|----------|---------------|-------------|-------|
| Standard | 1 | Aylık | ❌ | ❌ | ₺X/ay |
| Professional | 5 | Haftalık | ✅ | Okuma | ₺Y/ay |
| Enterprise | Sınırsız | Günlük | ✅ | Tam | ₺Z/ay |

#### 6B — Stripe Webhook Handler

```typescript
// app/api/stripe/webhook/route.ts
export async function POST(req: Request) {
  const event = stripe.webhooks.constructEvent(body, sig, WEBHOOK_SECRET);

  switch (event.type) {
    case 'customer.subscription.created':
    case 'customer.subscription.updated':
      await supabase.from('clinics').update({
        stripe_subscription_id: event.data.object.id,
        plan_tier: mapPriceToTier(event.data.object.items.data[0].price.id),
        subscription_status: event.data.object.status,
        subscription_current_period_end: new Date(event.data.object.current_period_end * 1000)
      }).eq('stripe_customer_id', event.data.object.customer);
      break;
  }
}
```

**Sprint 6 Çıktısı:** Stripe entegrasyonu, plan kısıtlamaları, self-serve kayıt akışı.

---

## Deployment Mimarisi

```
┌─────────────────────────────────────────────────────────┐
│                    PRODUCTION                            │
│                                                         │
│  Vercel (Next.js)          Railway / Fly.io (FastAPI)   │
│  nefalixai.com             api.nefalixai.com            │
│       │                          │                      │
│       └──────────┬───────────────┘                      │
│                  │                                      │
│         Supabase Cloud (PostgreSQL)                     │
│         supabase.co — proje: nefalix-prod               │
│                  │                                      │
│       n8n Cloud (enkahealthisterr.app.n8n.cloud)        │
│                  │                                      │
│       Evolution API (VPS Docker)                        │
│       WhatsApp Business — Medident pilot                │
└─────────────────────────────────────────────────────────┘
```

### CI/CD Akışı

```yaml
# .github/workflows/deploy.yml
on:
  push:
    branches: [main]

jobs:
  migrate:
    runs-on: ubuntu-latest
    steps:
      - uses: supabase/setup-cli@v1
      - run: supabase db push --project-ref ${{ secrets.SUPABASE_PROJECT_REF }}

  deploy-api:
    needs: migrate
    runs-on: ubuntu-latest
    steps:
      - run: flyctl deploy --app nefalix-api

  # Vercel otomatik deploy — GitHub entegrasyonu ile
```

---

## Öncelikli API Uçları (İlk 2 Sprint'te Açılacaklar)

### FastAPI — P0 (Sprint 2 başında)

```
GET  /health                          → Servis durumu
GET  /mcp/context/{clinic_id}         → LLM bağlam paketi
POST /ai/audit                        → Teknik denetim başlat
POST /ai/score                        → AI skor hesapla + DB'ye yaz
POST /webhooks/n8n                    → n8n event alıcısı
```

### FastAPI — P1 (Sprint 2 ortası)

```
POST /ai/summary                      → Board-ready özet üret
GET  /ai/executive/{clinic_id}        → Kaydedilmiş özeti getir
POST /ai/correlate                    → eNPS ↔ yıldız korelasyonu
POST /upload/enps                     → CSV parse + analiz
```

### Next.js API Routes — P0 (Sprint 3 başında)

```
POST /api/auth/login                  → JWT / magic link
GET  /api/dashboard/kpis              → Ana sayfa KPI'ları
GET  /api/reviews                     → Onay bekleyen yorumlar
POST /api/reviews/[id]/approve        → Yorumu onayla + n8n tetikle
GET  /api/inbox                       → Birleşik gelen kutusu
POST /api/upload/enps                 → FastAPI'ye yönlendir
POST /api/stripe/webhook              → Stripe event işle
```

---

## İlk Sprint'lerde Hangi Tablolardan Başlamalı?

### Okuma (Sprint 1–2 başında, hemen bağlan):

1. **`clinics`** — Temel klinik profili, tüm sorgularda ana referans
2. **`nps_responses`** — NPS trend ve dağılım (dashboard P0)
3. **`google_reviews`** — Yorum onay akışı (dashboard P0)
4. **`inbox_messages`** — Birleşik gelen kutusu (dashboard P0)
5. **`dashboard_users`** — Auth ve session yönetimi

### Yazma (Sprint 2'de FastAPI ile):

6. **`ai_readiness_scores`** — Her audit sonrası yaz (yeni tablo)
7. **`locations`** — GEO/AEO takibi için klinik lokasyonları (yeni tablo)
8. **`operational_sentiment`** — Board summary + korelasyon (yeni tablo)
9. **`automation_events`** — Tüm workflow event logu (mevcut, genişlet)

### Geç Aşama (Sprint 4+):

10. **`enps_responses`** — Çalışan anketi (CSV import ile dolar)
11. **`reputation_mentions`** — Şikayetvar + sosyal medya
12. **`recall_campaigns`** — Geri çağrı otomasyonu

---

## Teknik Riskler & Azaltma Stratejileri

| Risk | Seviye | Azaltma |
|------|--------|---------|
| Google Places API rate limit | Orta | Cache + `google_places_sync` migration mevcut |
| FastAPI ↔ Supabase auth senkronizasyonu | Yüksek | `service_role` key → JWT bypass; RLS server-side |
| n8n Cloud outage | Düşük | Kritik workflow'lar için fallback webhook endpoint |
| OpenAI API maliyet | Orta | GPT-4o-mini audit için, 4o board summary için |
| Schema.org checker false positive | Düşük | `cheerio` + `jsonld` parse; hatalı markup için graceful degradation |
| Multi-tenant veri sızıntısı | Yüksek | RLS her tabloda zorunlu; `service_role` sadece FastAPI/n8n |

---

## Referans Komutlar

```bash
# Sprint 0: Projeleri oluştur
npx create-next-app@latest nefalix-dashboard --typescript --tailwind --app
pip install fastapi uvicorn supabase openai httpx pytest

# Sprint 1: Migration uygula
cd /workspace
supabase db push

# Sprint 2: FastAPI çalıştır
cd fastapi-mcp && uvicorn main:app --reload --port 8000

# Sprint 3: Next.js çalıştır
cd nefalix-dashboard && npm run dev

# Mevcut execution script'leri
python3 execution/import-workflows.py   # n8n workflow import
python3 execution/sync-google-reviews.py  # Google review sync
bash execution/test-all-workflows.sh    # Tüm workflow'ları test et
```

---

## Öncelik Özeti (TL;DR)

```
Sprint 0  →  Next.js + FastAPI projesi kur, Vercel + Fly.io bağla
Sprint 1  →  3 yeni Supabase tablosu (locations, ai_readiness_scores, operational_sentiment)
Sprint 2  →  FastAPI: /mcp/context + /ai/audit + /ai/score + /ai/summary
Sprint 3  →  Next.js: Dashboard ana sayfa + Reviews + Inbox + AI Score sayfaları
Sprint 4  →  n8n: wf-audit-cron + wf-alert-engine + wf-board-summary
Sprint 5  →  GEO/AEO: llms.txt generator + Schema.org injector + quote-ready pipeline
Sprint 6  →  Stripe billing + multi-tenant self-serve
```

**İlk 2 sprintte mutlaka açılması gereken tablolar:** `clinics` · `nps_responses` · `google_reviews` · `inbox_messages` (okuma) + `ai_readiness_scores` · `locations` · `operational_sentiment` (yazma)

**İlk 2 sprintte mutlaka açılması gereken endpoint'ler:** `/mcp/context` · `/ai/audit` · `/ai/score` · `/webhooks/n8n` (FastAPI) + `/api/dashboard/kpis` · `/api/reviews` · `/api/inbox` (Next.js)
