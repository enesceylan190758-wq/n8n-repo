# Nefalix Agent Instructions

Bu dosya `CLAUDE.md` ve `GEMINI.md` ile aynı içeriği taşır — farklı AI ortamlarında tutarlı çalışmak için.

## 3 Katmanlı Mimari

LLM'ler olasılıksaldır; Nefalix iş mantığı (KVKK, İYS, HBYS, Supabase) deterministik olmalıdır.

| Katman | Konum | Rol |
|--------|-------|-----|
| **1 — Directive** | `directives/` | Ne yapılacağı (SOP). Hedef, girdi, araç, çıktı, edge case. |
| **2 — Orchestration** | AI (sen) | Directive oku → doğru script'i sırayla çağır → hata yönet → öğrenilenleri directive'e yaz. |
| **3 — Execution** | `execution/` | Deterministik Python/shell script'leri. API, DB, dosya işleri. |

**Kural:** Scraping, import, test, migration gibi işleri kendin uydurma — önce `execution/` ve `directives/` bak, varsa onu çalıştır.

## Çalışma İlkeleri

1. **Önce aracı kontrol et** — Yeni script yazmadan `execution/` listele.
2. **Self-anneal** — Hata olunca: oku → script'i düzelt → test et → `directives/` güncelle.
3. **Directive'leri yaşat** — Tek seferlik not değil; her öğrenilen kısıt (API limiti, UUID, Docker host) directive'e eklenir.
4. **Directive silme/üzerine yazma** — Kullanıcı istemedikçe mevcut SOP'u koru, geliştir.

## Dosya Organizasyonu

| Yol | Amaç |
|-----|------|
| `directives/` | SOP'lar (instruction set) |
| `execution/` | Deterministik script'ler |
| `workflows/` | n8n workflow JSON (import kaynağı) |
| `supabase/migrations/` | DB şema (tek veri katmanı) |
| `docs/` | Mimari referans (ARCHITECTURE, SETUP, SUPABASE) |
| `.tmp/` | Ara dosyalar — commit etme, silinebilir |
| `.env` | Secret'lar — commit etme |

**Deliverable:** Supabase tabloları, n8n workflow'ları, GitHub commit'leri, Vercel deploy.  
**Intermediate:** `.tmp/` altındaki cookie, test çıktıları, geçici export.

## Nefalix Bağlamı

- **Pilot klinik:** MediDent Kartal — sabit `clinic_id`: `51738ea8-c12e-40ce-a0e2-42869496d76b`
- **n8n Docker:** `host.docker.internal:54321` (Supabase için `127.0.0.1` değil)
- **Workflow'lar ayrı** — tek dev workflow yok; veri Supabase'te birleşir
- **WhatsApp:** MVP'de log stub; gerçek API credential gelince directive güncellenir

## Yeni oturum devri

Yeni Cursor hesabı veya sohbet taşıması yoksa: önce **`.tmp/handoff.md`** oku (git’te tutulur; güncel durum, yarım işler, sonraki adımlar).

## Directive Index

| Görev | SOP |
|-------|-----|
| Stack başlat (Docker + Supabase) | `directives/start_stack.md` |
| Workflow import | `directives/import_workflows.md` |
| Vertex AI / Gemini (GCP kredi) | `directives/vertex_ai_setup.md` |
| Tüm workflow'ları test et | `directives/test_workflows.md` |
| Supabase migration | `directives/supabase_migrate.md` |
| Site chat tunnel | `directives/chat_tunnel.md` |
| Estesoft CRM (Medident) | `directives/estesoft_integration.md` |
| Evolution API (WhatsApp pilot) | `directives/evolution_setup.md` |
| Randevu tetikleme (HBYS/CRM) | `directives/appointment_trigger.md` |
| Ürün yol haritası | `directives/product_roadmap.md` |
| Google yorum senkronu (Places API) | `directives/google_reviews_sync.md` |
| Şikayetvar itibar tarama | `directives/sikayetvar_sync.md` |
| Medident dashboard otomasyonları | `directives/activate_medident_pilot.md` |
| Güvenlik / secret rotasyon | `directives/security.md` |
| Sosyal medya otomasyonu (IG/LinkedIn) | `directives/social_media_automation.md` |

## Self-Annealing Döngüsü

```
Hata → execution/ düzelt → test et → directives/ güncelle → sistem güçlenir
```

Örnek: `clinic_id` her `db reset`'te değişiyordu → migration'da sabit UUID → `directives/supabase_migrate.md` güncellendi.
