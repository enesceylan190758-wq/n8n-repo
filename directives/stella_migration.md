# Stella → Nefalix Hasta CRM Geçişi (P0)

## Hedef

Medident günlük Stella akışını `/hasta-crm` üzerinden sürdürmek; 2–4 hafta paralel koşu sonrası Stella kesimi.

**Canlı:** https://nefalix.com/hasta-crm  
**Motor:** `nefalix-landing/api/_lib/clinic-crm.js` → Supabase `crm_*` (cloud: `SUPABASE_URL_PROD`)  
**Spec:** `docs/Stella_Phase1_Spec.md`

## Mimari

| Katman | Dosya |
|--------|-------|
| Stella UI | `nefalix-hasta-crm.html` + `nefalix-hasta-crm-app/` |
| Store (API) | `nefalix-hasta-crm-app/store.js` |
| Pack | `execution/pack-nefalix-hasta-crm.py` |
| API | `api/_lib/clinic-crm.js` |
| Şema | `supabase/migrations/20260727120000_crm_stella_phase1.sql` |
| Segment CSV | `docs/stella_segments.csv` |
| Referans CSV | `docs/stella_reference_sources.csv` |

## Kurulum (tek sefer)

### 1. Migration (VPS Supabase — Klinik CRM burada)

```bash
# CRM tabloları cloud PROD'da değil; VPS `supabase_db_n8n-repo` içinde.
scp supabase/migrations/20260727120100_crm_stella_phase1_alter.sql root@VPS:/tmp/
ssh root@VPS 'docker cp /tmp/20260727120100_crm_stella_phase1_alter.sql supabase_db_n8n-repo:/tmp/ && docker exec supabase_db_n8n-repo psql -U postgres -d postgres -f /tmp/20260727120100_crm_stella_phase1_alter.sql'
```

### 2. Segment + referans seed

VPS'te SQL seed veya:

```bash
# Laptop → VPS proxy (NEFALIX_INTERNAL_KEY + FORCE_PROXY)
python3 execution/import-stella-definitions.py --prod
```

### 3. Stella veri import (VPS üzerinde)

```bash
ssh root@VPS 'cd /opt/nefalix && set -a && . ./.env && set +a && export SUPABASE_URL=http://127.0.0.1:54321 && python3 execution/import-stella-crm.py'
```

Not: Stella `CustomerApi/List` sayfalama parametresi `offset` (skip değil).

### 4. Hasta UI pack + deploy

```bash
python3 execution/pack-nefalix-hasta-crm.py
cd /Users/enesceylan/nefalix-landing && vercel --prod --yes
```

Vercel env: `SUPABASE_URL_PROD`, `SUPABASE_SERVICE_ROLE_KEY_PROD`, `DASHBOARD_SESSION_SECRET`

## Giriş

- URL: `/hasta-crm`
- Kod: `enes`, `abdulkadir`, `kader` (şifre yok)
- Cookie: `nefalix_clinic`, 90 gün HttpOnly
- Yenilemede oturum: `clinic-me` + `restoreServerSession()`

**Lead listesi:** yalnızca segment `YENİ DATA` / `Yeni Lead` / `Yeni Gelen` veya segmentsiz. Diğer potansiyel/takip → Danışan + Dinamik.

## Paralel koşu checklist (2 hafta)

| Gün | Enes / Abdülkadir | Kontrol |
|-----|-------------------|---------|
| 1–3 | Lead kayıt + atama `/hasta-crm` | Stella ile aynı segment isimleri |
| 4–7 | Dinamik arama + not/segment | `next_call_date` doğru mu |
| 8–10 | Randevu takvim | Açık randevular import edildi mi |
| 11–14 | Teklif + basit ödeme | EUR teklif, kasa hareketi |
| 15 | Go/no-go toplantı | Stella kesim tarihi |

### Go kriterleri

1. Günlük akış tamamen `/hasta-crm` (lead → atama → dinamik → randevu)
2. Yenilemede oturum düşmüyor
3. Segment listesi Stella ile uyumlu (39 tanım)
4. Aktif lead + açık randevu import tamam
5. Ekip eğitimi yapıldı

### Stella kesim

1. FB lead → manuel `/hasta-crm` veya `clinic-lead-intake` (P1: Meta webhook)
2. Stella salt-okunur 1 hafta (yedek)
3. Stella lisans iptal

## Edge cases

| Sorun | Çözüm |
|-------|--------|
| API 404 `crm_*` | Migration uygulanmamış — §Kurulum 1 |
| Giriş düşüyor | `clinic-me` route + cookie `DASHBOARD_SESSION_SECRET` Vercel'de |
| Dinamik boş | `import-stella-definitions.py --prod`; `next_call_date` bugün veya geçmiş |
| 5× ulaşılamadı | `dynamic_attempt_count` + segment `5_kez_ulasilamadi` otomatik |

## P1 (kesim sonrası)

- Meta FB lead otomatik → `clinic-lead-intake`
- WhatsApp panel (Evolution) hasta kartı
- Tam finans / fatura
- Stella not/teklif geçmiş import
