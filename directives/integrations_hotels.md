# Otel Entegrasyonları — TheClico & Cloudbeds

## TheClico (TR — rakip / referans)

**Ne yapıyor:** Türkiye merkezli itibar yönetimi — yüzlerce platformdan yorum/şikayet toplama, NLP ile duygu analizi, kriz uyarısı, NPS/CSAT benchmark.

**Nefalix farkı:**
| TheClico | Nefalix |
|----------|---------|
| Dinleme + analiz ağırlıklı | Dinleme + **aksiyon** (WhatsApp NPS, Google davet, yönetici alarmı) |
| Genel marka ORM | Sektör paketleri: klinik, otel, oto servis |
| Dashboard rapor | Operasyon paneli + onaylı yanıt |

**Bizim yapabileceklerimiz:** TheClico müşterisine “üstüne otomasyon katmanı” — checkout sonrası misafir anketi, promoter → Booking/Google, detractor → ön büro müdürü WhatsApp.

## Cloudbeds (global PMS)

**Ne yapıyor:** Otel PMS — rezervasyon, check-in/out, misafir profili, 450+ entegrasyon, **açık REST API + webhook**.

**API tetikleyiciler (Nefalix için):**
- `checked_out` webhook veya `getReservations` + `status=checked_out`
- Misafir telefon/e-posta → NPS WhatsApp
- `postReservationNote` — Nefalix analiz özetini rezervasyona not olarak yazma (opsiyonel)

**Nefalix otel paketi:**
1. Cloudbeds checkout → `nefalix/hotel/guest-checkout` webhook
2. AI misafir memnuniyet anketi (1–10)
3. 8+ → Google/Tripadvisor yorum linki
4. 7− → ön büro müdürü alarmı (Google’a gitmeden çözüm)

**Pilot:** Demo oteller panelde; gerçek Cloudbeds property `propertyID` + OAuth ile bağlanır.

## Satış cümlesi
> Cloudbeds operasyonunuzu yönetir; Nefalix checkout sonrası itibarınızı büyütür — tek panelde otel, klinik ve servis.
