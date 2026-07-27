# Nefalix Hasta / Klinik CRM — Next.js Geçiş Planı

**Sürüm:** 1.0  
**Tarih:** 27 Temmuz 2026  
**Kim için:** Enes (ürün) · Arif (Next.js) · Abdülkadir / operasyon  
**Pilot:** MediDent Kartal — `clinic_id` `51738ea8-c12e-40ce-a0e2-42869496d76b`  
**Bağlam kaynakları:** Arif güvenlik raporu (11 Tem 2026) · Entrfy teklif (14 Tem 2026) · `Nefalix_Urun_Mimarisi.md` · `Stella_Phase1_Spec.md`

---

## Kısa verdict

Hasta CRM’in **kalıcı üretim yüzeyi Next.js olmalıdır**. Stella kesimi için mevcut `/hasta-crm` (HTML pack + `clinic-crm.js`) paralel koşuda kalır; Next’e taşıma Stella’yı bloke etmez. Arif’in güvenlik mantığı (auth, kiracı, RLS, yedek, izleme) CRM’de **birebir** uygulanır — “n8n’i sonsuza kadar güçlendir” kısmı otomasyonlar için güncellendi; CRM zaten n8n’de değil.

---

## Bugün nerede?

```
/hasta-crm (DC HTML pack)  ──►  /api/clinic/* (Vercel)  ──►  Supabase crm_*
/klinik-crm (basit HTML)    ──►  aynı API
Stella REST                 ──►  import-stella-*.py      ──►  Supabase crm_*
```

| Katman | Durum | Risk |
|--------|-------|------|
| UI | Drive DC → pack → Vercel HTML | Bakım zor; Dashboard ile ayrı yüzey |
| API | `clinic-crm.js` + cookie oturum | Kod ile giriş; şifre yok; secret fallback riski |
| Veri | `crm_*` + service role | RLS / kiracı izolasyonu üretimde henüz Arif seviyesinde değil |
| Stella | Paralel koşu P0 | Kesim = operasyon + go kriterleri |

Ürün sırası (`Nefalix_Urun_Mimarisi` E): Dashboard → Inbox/NPS → … → **Klinik CRM (#5)** → Kurum CRM (#6).

---

## Arif planından ne alınır?

### Güvenlik raporundan (kök mantık — al)

| İlke | CRM’e yansıması |
|------|-----------------|
| Uçlar auth’suz olmasın | Tüm `clinic-*` oturum zorunlu; public lead-intake ayrı imza |
| `clinic_id` istekten değil oturumdan | Cookie/JWT claim; body’deki clinic_id yok sayılır |
| RLS / anon kapalı | `crm_*` anon SELECT yok; service role yalnız sunucu |
| Yedek + tek sunucu riski | Prod Supabase yedek + restore prova |
| İzleme | Import/API hata → yönetici uyarısı |
| n8n → Next (otomasyon) | CRM iş mantığı zaten Vercel API’de; hedef App Router’da birleşsin |

### Entrfy tekliften (kapsam dili — al; teknoloji dondurması — alma)

| Al | Alma / güncelle |
|----|-----------------|
| A→E sırası: güvenlik → stabilizasyon → multi-tenant → UI → test | “n8n 19 wf korunur” — otomasyonlar için Next kararı üstün |
| Saat/kalem netliği, aşama onayı | “Sıfırdan yazım yok” = mevcut `crm_*` + iş kurallarını taşı; UI framework’ü Next’e geçebilir |
| Firma yalıtımı, şifreleme, KVKK saklama | — |

---

## CRM Next.js olmalı mı?

| Soru | Cevap |
|------|--------|
| Kalıcı mimari | **Evet** — Dashboard ile aynı App Router, aynı auth, aynı kiracı modeli |
| Stella kesimi öncesi zorunlu mu? | **Hayır** — P0 cutover mevcut `/hasta-crm` ile yapılabilir |
| Ne zaman başlar? | Dashboard + auth Next’e oturunca (ürün sırası #1–2 sonrası veya paralel iskelet) |
| Kurum CRM (`/nefalix-crm`) | Ayrı ürün; Hasta CRM’den sonra; aynı güvenlik ilkeleri |

---

## Fazlı plan (Arif tarzı)

### FAZ 0 — Canlı CRM risklerini kapat · 0–72 saat

Stella gerçek hasta/lead ile büyürken ertelenemez:

1. `DASHBOARD_SESSION_SECRET` / clinic cookie secret production’da sabit fallback olmasın; rotate.
2. Tüm `clinic-*` uçlarında `requireSession`; `clinic_id` yalnız oturum/claim.
3. `crm_*` tablolarında anon RLS kapat; yalnız service role (sunucu) + ileride authenticated policy.
4. Kod-only giriş → en azından PIN/şifre veya dashboard kullanıcısına bağlama kararı (geçici: rate limit + audit log).
5. Elle/otomasyon yedek: prod `crm_*` snapshot; import öncesi dry-run disiplini korunur.

### FAZ 1 — Stella P0 üretim kalitesi · 1–2 hafta (paralel koşu)

Mevcut yüzeyde; Next şart değil:

| Kalem | Go sinyali |
|-------|------------|
| Segment 39 + dinamik arama | Stella ile aynı etiket / `next_call_date` |
| Lead → atama → not → randevu | Günlük akış `/hasta-crm` |
| Teklif + basit ödeme | EUR / kasa hareketi |
| Oturum yenilemede düşmesin | `clinic-me` + 90g cookie |
| Import tamam | Aktif lead + açık randevu |
| Go/no-go | Stella salt-okunur → kesim |

SOP: `directives/stella_migration.md` · Spec: `docs/Stella_Phase1_Spec.md`

### FAZ 2 — Next.js Klinik CRM (kalıcı) · 2–6 hafta (Dashboard sonrası)

```
app/(clinic)/crm/...     UI (Stella ekran eşlemesi)
lib/crm/*                iş kuralları (dinamik, segment, 5×)
API Route Handlers       eski clinic-crm.js’in taşınmış hali
auth                     Dashboard ile ortak oturum (tercih)
Supabase crm_*           şema korunur; migration ile yetki sıkılaşır
```

**Taşıma sırası (ekran):** Login → Lead listesi → Dinamik → Hasta kartı / not → Randevu → Teklif/ödeme → Rapor.  
**Kesme:** Feature flag; HTML `/hasta-crm` salt-okunur 1 hafta → kaldır.

**Kurum CRM:** Faz 2b — JSON blob (`nefalix_state`) → normalize tablolar veya ayrı tenant; müşteriye açılmaz.

### FAZ 3 — Ölçek · 1–2 ay

- Self-servis klinik onboarding (CRM kullanıcı + segment seed)
- PII alanlarında encryption-at-rest / maskeleme UI
- KVKK saklama + silme (lead arşiv TTL)
- FB/Meta lead webhook → `clinic-lead-intake` (imzalı)
- E2E + güvenlik testi (çapraz klinik okuma denemesi fail etmeli)

---

## Mimari hedef (tek bakış)

```
                    ┌─ Dashboard (CX) ─┐
Klinik kullanıcı ──┤                   ├── Next.js (Vercel) ── Supabase
                    └─ Klinik CRM ─────┘         │
                                                 ├─ auth / clinic_id claim
Stella (geçici) ── import scripts ───────────────┘
n8n ── yalnızca prototip; üretim CRM yolu değil
```

---

## Güvenlik kontrol listesi (CRM özel)

| Kontrol | Zorunlu ne zaman |
|---------|------------------|
| Auth her clinic uçta | Faz 0 |
| `clinic_id` oturumdan | Faz 0 |
| Anon RLS kapalı | Faz 0 |
| Çapraz klinik test | Faz 1 go |
| Yedek + restore prova | Faz 1 |
| Şifre/PIN veya SSO | Faz 1–2 |
| PII encryption / retention | Faz 3 (canlı hasta yoğunluğuna göre öne çek) |
| Audit log (kim ne değiştirdi) | Faz 2 |

---

## Rol ayrımı

| Rol | Ne yapar |
|-----|----------|
| Cursor / PM | Spec, iş kuralı, `crm_*` migration, import script, SOP |
| Arif / Next | App Router CRM, ortak auth, kiracı, test edilebilir API |
| Abdülkadir | Paralel koşu, segment doğrulama, go/no-go |
| Operasyon (Kadir) | Günlük hacim, kesim tarihi, FB lead kaynağı, eğitim |

---

## Bilinçli olarak bu planda olmayanlar

- Stella plan dosyasını (`.cursor/plans/`) değiştirmek
- Kurum CRM’i Hasta CRM ile birleştirmek
- n8n içinde CRM iş mantığı yazmak
- Stella kesimini Next bitene ertelemek

---

## Referanslar

- `docs/Nefalix_Urun_Mimarisi.md` — kilit #11, Next sırası E
- `docs/Stella_Phase1_Spec.md` — P0 eşleme
- `directives/stella_migration.md` — cutover SOP
- `directives/security.md` — rotasyon / harden
- Arif PDF: Güvenlik ve Sistem Değerlendirmesi (11 Tem 2026)
- Entrfy PDF: Demo ve Sistem Güçlendirme teklifi (14 Tem 2026)
