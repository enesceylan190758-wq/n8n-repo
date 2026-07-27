# Nefalix Ürün Mimarisi

**Sürüm:** 3.6 (sade)  
**Tarih:** 23 Temmuz 2026  
**Kim için:** Arif (Next.js) + iç ekip  
**Pilot:** MediDent Kartal — `51738ea8-c12e-40ce-a0e2-42869496d76b`

---

## Nasıl okunur? (karışıklığı kes)

Üç yol var — hepsini okumak zorunda değilsin:

| Sen | Oku | Atla |
|-----|-----|------|
| **Enes / ürün** | Bölüm A (kilitler) + B (modül kartları) | Ekler |
| **Arif / Next** | A + B + C (CRM) + **Ek 1** (wf start→end) | Ek 3–4’ü ihtiyaç olunca |
| **Araştırma / hukuk** | **Ek 2–3** (Stella, İYS, belli değil) | Modül tekrarları |

**Bu dosya ne?** Ürün ne yapar, hangi kural, bugün nerede. Kod nasıl yazılır demez.  
**Supabase** = operasyon DB. **SSS / protokol içeriği** henüz yok — karar kilitli, tablo yok.

---

## A — Kilit kararlar (tek bakış)

Değişmez ürün kuralları. Detay gerekirse ilgili modül kartına bak.

| # | Konu | Karar |
|---|------|--------|
| 1 | SSS / AI | Ortak Nefalix katalog, **branş bazlı** (diş→estetik→saç). AI kendi kafasına cevap uydurmaz; eşleşmezse insan. |
| 2 | Protokol | Sohbet değil. “2. gün, şu şampuan…” — **önceden onaylı senaryo**, otomatik gider. Eşleme: Stella `serviceId`. |
| 3 | İYS | Dosya yükletme yok. HBYS bayrağı varsa kullan; yoksa Nefalix opt-in linki. |
| 4 | NPS skor | **8–10** → Google (varsayılan). **≤7** → Google yok; kriz + yönetici. |
| 5 | NPS gönderim (pilot) | Taslak → Inbox **onay** → WA. |
| 6 | Yorum yanıt | **5★ otomatik; ≤4 insan.** |
| 7 | NPS kalıp | Biz yazarız, A/B ölçeriz, yönetim seçer. |
| 8 | Hasta verisi | Minimal (ad, tel, İYS, randevu, NPS, mesaj). TC/foto/belge yok. **Maskeleme zorunlu.** |
| 9 | Recall | **6 ayda bir** sağlık hatırlatma. Panelde **kasıtlı sahte satır** (boş görünmesin). |
| 10 | Sentinel | Şikayetvar + hedefte IG/FB/LinkedIn. |
| 11 | CRM | Klinik CRM ileride **Dashboard içine**. Kurum CRM (`/nefalix-crm`) iç satış — müşteriye açılmaz. |
| 12 | Arif | Her otomasyon **nerede başlar → nerede biter** (Ek 1). Otel/oto yok. |
| 13 | Çift anket | HBYS kendi anketi + Nefalix birlikte yasak. |

### Ortak platform (her yerde)

- Her kayıtta `clinic_id` (multi-tenant).
- WA: `WHATSAPP_SEND_ENABLED` + hız limiti (wf-00).
- Bugün: Vercel HTML + n8n + Supabase. Hedef: **Next.js**; veri Supabase kalır.

### Ürün yüzeyleri

| Yüzey | URL | Kim | Giriş |
|-------|-----|-----|-------|
| Dashboard | `/dashboard` | Klinik yönetici | e-posta + şifre |
| Klinik CRM | `/klinik-crm` | Klinik satış | kod |
| Kurum CRM | `/nefalix-crm` | Nefalix saha | kod |

---

## B — Modül kartları (kısa)

Her kart: **ne → akış → kritik kural → veri → durum**.

### B1 — Feedback (NPS)

**Ne:** Randevu bitince 1–10 sor; memnun → yorum linki; değil → içeride tut.

**Akış:** HBYS Tamamlandı → taslak Inbox → onay → WA → skor → promoter / detractor.

**Kritik:** 8–10 / ≤7. Detractor’a Google yok. Aynı `appointmentId` iki kez tetiklenmez.

**Veri:** `nps_responses` (`flow`, `resolution_status`).

**Durum:** Canlı pilot (şalterli).

### B2 — Inbox

**Ne:** Gelen WA + NPS taslak onayı + kriz alarmları.

**Akış:** Evolution → wf-06 → SSS eşleşirse otomatik; yoksa insan. Skor görünürse → NPS.

**Kritik:** Pilot NPS onaysız gitmez. 403 gönderim kapalı / 429 rate limit.

**Veri:** `inbox_messages` (`message_kind`: inbound / estesoft_nps / nps_alert).

**Durum:** Canlı; SSS havuzu yok → serbest AI riski.

### B3 — Review AI

**Ne:** Yorum çek → taslak → yanıt.

**Akış:** Places 6s sync → taslak → 5★ auto (hedef) / ≤4 insan → Sentinel.

**Kritik:** Bugün yalnız Google (son 5). DT/Doktorsitesi/Trustpilot mimaride; Google gibi kolay pull her yerde yok (Ek 2).

**Veri:** `google_reviews`.

**Durum:** Google canlı; yayın çoğu manuel.

### B4 — eNPS

**Ne:** Çalışan 1–10 anonim nabız.

**Kritik:** Kanal = WA ve/veya panel linki (e-posta yok). Hangisi kazanır ölçülünce kilitlenir.

**Veri:** `enps_responses`.

**Durum:** Pilot / zayıf.

### B5 — Sentinel

**Ne:** İtibar sinyali → risk → gerekirse yönetici WA.

**Kritik:** Canlı Şikayetvar. Hedef + sosyal. “Tüm web” iddiası yok.

**Veri:** `reputation_mentions`.

**Durum:** Kısmi.

### B6 — Recall

**Ne:** ~6 ay gelmeyen hastaya sağlık hatırlatma.

**Kritik:** İYS yoksa gitmez. Demo/sahte satırlar kasıtlı.

**Veri:** `recall_campaigns`.

**Durum:** İskelet.

### B7 — Dashboard

**Ne:** Tüm CX’in ortak paneli (NPS, Inbox, Reviews, …).

**Kritik:** İlk Next taşıma adayı. VPS yoksa 503. Cookie 7 gün.

**Durum:** Canlı.

### B8 — Protokol (akıllı mesaj) — henüz üründe yok

**Ne:** Tedavi sonrası gün gün senaryo (D0, D1, D7…).

**Kritik:** Önceden onaylı şablon, otomatik gönderim. Stella `serviceId` ile eşle (adapter’da henüz taşınmıyor). İskelet: Ek 4.

---

## C — CRM (ayrı ürünler)

### C1 — Klinik CRM (hasta lead)

**Ne:** Lead → atama → not+segment → **Dinamik Arama** → randevu.

**Kalp kuralı:** Cron yok. `next_call_date <= bugün` + `status=aktif`. Segment `gun_offset` ile ileri atar. Kapanış (`satildi` / `sureci_biten` / `tedaviye_uygun_degil`) → arşiv.

**Atama:** `stage=danisan`, `next_call_date=bugün`.

**Teknik:** `api/_lib/clinic-crm.js`. SOP: `directives/clinic_crm.md`.

### C2 — Kurum CRM (Nefalix satışı)

**Ne:** Klinik müşteri pipeline: Yeni Lead → … → Aktif Müşteri.

**URL:** `nefalix.com/nefalix-crm`. Veri: `nefalix_state` id=2 (JSON blob).

**Durum:** Canlı, teknik borçlu.

---

## D — Dış bağlantılar (tek satır)

| Sistem | Bugün | Not |
|--------|-------|-----|
| Evolution WA | Canlı | Resmi Meta API tarih/BSP belli değil |
| Estesoft | Canlı NPS | Get’te `serviceId` var; wf-12 taşımıyor (Ek 2) |
| Google Places | Canlı | Son 5 yorum |
| Şikayetvar | Canlı scrape | Kırılgan |
| İYS resmi API | Yok | Model A’da kilitli; bildirim yok |

---

## E — Next sırası (kısa)

1. Dashboard + auth  
2. Inbox + NPS  
3. Bilgi havuzu + protokol şeması  
4. Reviews  
5. Klinik CRM  
6. Kurum CRM  
7. Meta WA adapter  
8. Sentinel + Recall  
9. Blog/GEO  

---

## Ek 1 — Workflow start → end (Arif)

| WF | Başlar | Biter |
|----|--------|-------|
| 00 | `…/whatsapp/send` | Gönderim veya skip; `whatsapp_send_log` |
| 01 | HBYS completed + NPS response | `nps_responses` + link/alarm |
| 02 | Cron 6s / new-review | Analiz/taslak |
| 03 | Aylık + enps response | `enps_responses` |
| 04 | Cron / sentinel mention | `reputation_mentions` ± WA |
| 05 | Günlük / recall check | `recall_campaigns` |
| 06 | inbox incoming | `inbox_messages` ± NPS fan-out |
| 07 | dashboard data | Panel JSON |
| 08 | inbox send/clear | Outbound / clear |
| 09 | Cron / google sync | `google_reviews` |
| 10 | Cron / draft | `draft_reply` |
| 11 | review-approve | `published` |
| 12 | estesoft webhook | Inbox NPS taslak |
| 13 | Cron poll | → wf-12 |
| 14 | Cron / sikayetvar | → wf-04 |
| 15 | whatsapp connect | QR/status |
| 16 | supabase-proxy | Vercel→VPS DB |
| 17 | Sosyal (eski) | Drive paketi; asıl Python |

---

## Ek 2 — Stella / HBYS (araştırma özeti)

**Canlı denendi (2026-07-23):** `AppointmentApi/List` + `Get`.

**Adapter’ın kullandığı:** id, customerName, phone, status, staffName, serviceName.

**Get’te ekstra (önemli):** `appointmentService[].serviceId` + `serviceName`, `customerId`.

**Yok:** ilaç listesi, İYS bayrağı.

**Borç:** wf-12’ye `serviceId` map. SOP: `directives/estesoft_integration.md`.

---

## Ek 3 — Belli değil (tek liste)

| Konu | Sonraki adım |
|------|--------------|
| İlaç / aftercare HBYS’de | Klinik şablon |
| Stella İYS alanı | Customer Swagger + opt-in |
| Adapter `serviceId` | wf-12 / Next |
| İYS’de kim hizmet sağlayıcı | Hukuk |
| WA ticari vs bilgilendirme | Uyum notu |
| Meta WA tarih / BSP / numara sahibi | İş kararı |
| DoktorTakvimi review pull | Public API’de yok; partner |
| IG/FB/LinkedIn API erişimi | P1 araştırma |
| eNPS kazanan kanal | Ölç |
| Faturalama prod (PayTR/Stripe) | Doğrula |

---

## Ek 4 — Diş SSS + implant protokol iskeleti

İçerik taslağı; hekim onayı sonrası DB. Migration yok.

**SSS (özet):** İmplant süre/ağrı, çekim sonrası yeme, kanal seans, dolgu, beyazlatma, hamilelik (**insan**), florür, plak, röntgen, **fiyat/sigorta insan**, acil şişlik (**insan**), marka, kontrol.

**İmplant günleri:** D0 dinlen/reçete → D1 yumuşak gıda → D2 şişlik → D3 ağrı artarsa ara → D7/D14 kontrol → M1/M3/M6 kontrol.

---

## Ek 5 — Olgunluk

| Modül | Durum |
|-------|-------|
| Dashboard | Canlı |
| NPS | Canlı pilot |
| Inbox | Canlı; SSS yok |
| Reviews | Google canlı |
| eNPS | Pilot |
| Sentinel | Şikayetvar |
| Recall | İskelet + demo satır |
| Klinik CRM | P0 |
| Kurum CRM | Canlı, borçlu |
| SSS / protokol | Karar var, içerik/tablo yok |
| İYS modeli | Kilitli; resmi API yok |

---

## Sözlük (mini)

n8n/wf · Supabase · Evolution · HBYS/Estesoft · NPS 8–10/≤7 · İYS · Dinamik Arama (`next_call_date`) · Bilgi havuzu · Protokol senaryosu

---

## Bakım

Tek kaynak bu MD. PDF: `/usr/bin/python3 execution/generate-urun-aktarim-pdf.py`  
Secret yazılmaz.

**Son güncelleme:** 2026-07-23 — **3.6 sade**: önde kilit + kısa kartlar; araştırma/iskelet ekte.
