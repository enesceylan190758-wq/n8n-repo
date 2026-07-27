# Stella → Nefalix Hasta CRM — Phase 1 Spec

**Tarih:** 2026-07-27  
**Pilot:** MediDent İstanbul (`clinic_id`: `51738ea8-c12e-40ce-a0e2-42869496d76b`)  
**Canlı UI:** https://nefalix.com/hasta-crm  
**Motor:** `nefalix-landing/api/_lib/clinic-crm.js` + Supabase `crm_*`

## Mimari

```
/hasta-crm (Stella UI DC)  ──►  clinic-* API  ──►  Supabase crm_*
/klinik-crm (basit HTML)   ──►  clinic-* API  ──►  Supabase crm_*
Stella REST API            ──►  import-stella-*.py  ──►  Supabase crm_*
```

Üçüncü backend yok. Hasta CRM `store.js` kurum CRM oturum desenini (`clinic-login` cookie, 90 gün) kullanır.

## Stella API (doğrulanmış)

| Endpoint | Durum | Not |
|----------|-------|-----|
| `POST /api/AuthApi/GetToken` | ✅ | `.env` `ESTESOFT_*` |
| `GET /api/CustomerApi/List?resultCount=&skip=` | ✅ | ~7500 kayıt; `segmentName`, `referenceSource`, `represent` |
| `GET /api/AppointmentApi/List` | ✅ | `directives/estesoft_integration.md` |
| `GET /api/AppointmentApi/Get?id=` | ✅ | Randevu detay |
| Segment / referans tanım API | ❌ | HTML 404; CSV seed kullanılır |

## P0 modül eşlemesi

| Stella | Nefalix | Tablo / endpoint |
|--------|---------|------------------|
| Kayıt listesi | Lead listesi | `crm_contacts` stage=lead · `clinic-leads` |
| Atama | Temsilci ata | `clinic-assign` |
| Not + segment | Not kaydı | `clinic-note-save` → `next_call_date` |
| Dinamik arama | Bugün aranacaklar | `clinic-dynamic` |
| 5× ulaşılamadı | `dynamic_attempt_count` | `noteSave` kuralı |
| Takvim | Randevu | `crm_appointments` · `clinic-appointments` |
| Teklif (EUR, otel) | Teklif | `crm_offers` · `clinic-offers` |
| Basit kasa | Ödeme | `crm_payments` · `clinic-payments` |
| Ay sonu rapor | Rapor | `clinic-reports` |
| Referans kaynağı | Tanım | `crm_reference_sources` |

## Segment modeli

Kaynak: Stella `customerSegment` ekranı + `CustomerApi/List` unique değerler.  
Tam liste: `docs/stella_segments.csv` (39 satır — Stella 38 + kapanış kodları).

Alanlar (`crm_segments`):

- `label` — UI etiketi (Stella ile birebir)
- `gun_offset` — Dinamik aramada tekrar çıkma günü (min 1; 0 = hemen)
- `show_in_dynamic` — false ise dinamikten düşer
- `hide_in_report` — raporda gizle
- `max_dynamic_attempts` — ulaşılamadı sayacı eşiği (varsayılan segment: 5)

## Referans kaynakları

`docs/stella_reference_sources.csv` — Stella panel + API’den görülen 5 kaynak + web/FB ekleri.

## Veri import kapsamı (P0)

| Veri | Script | Filtre |
|------|--------|--------|
| Segment + referans | `import-stella-definitions.py` | CSV upsert |
| Aktif lead/danışan | `import-stella-crm.py` | `status=aktif`, kapanış segmenti hariç |
| Açık randevu | `import-stella-crm.py` | Son 60 gün + gelecek 90 gün |

P1: tam not/teklif/bakiye geçmişi, FB lead otomatik.

## Oturum (Hasta CRM)

- `loginAsync(kod)` → `POST /api/clinic/login` (şifre yok)
- Cookie: `nefalix_clinic`, HttpOnly, 90 gün
- `restoreServerSession()` → `clinic-me` (yenilemede localStorage boşsa cookie’den devam)
- `resumeRoute()` → `nfx_last_route` + hash routing

## Paralel koşu (kesim öncesi)

1. Enes + Abdülkadir 2 hafta `/hasta-crm` günlük akış
2. Segment isimleri Stella ile aynı (`label` eşleşmesi)
3. Go/no-go: Stella kesim tarihi `directives/stella_migration.md`

## Riskler

| Risk | Azaltma |
|------|---------|
| Segment API yok | CSV seed + müşteri verisinden doğrulama |
| Çift sistem | Paralel dönem; import dry-run |
| KVKK | Import önce staging / `--dry-run` |
