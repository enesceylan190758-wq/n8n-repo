# Stella → Nefalix Gap / Action Map

**Tarih:** 2026-07-27  
**Kaynak paket:** `discovery/stella-discovery-2026-07-27.zip` (LFS) → `.tmp/stella-discovery/`  
**Canlı hedef:** https://nefalix.com/hasta-crm  
**Spec:** `docs/Stella_Phase1_Spec.md` · SOP: `directives/stella_migration.md`

## Kapsam dürüstlüğü

| Ne | Sayı |
|----|------|
| Pakette PNG | 390 |
| İlk örnekleme (2026-07-27) | **~35** |
| Aşamalı crawl (2026-07-28+) | State: `.tmp/stella-crawl-state.json` · SOP: `directives/stella_screenshot_crawl.md` · çıktı: `docs/stella_crawl/` |
| Stage 01 CRM/Lead | **17/17 done** → `docs/stella_crawl/stage-01-crm_lead.md` |
| Stage 02 Hasta kartı | **done** (15/25 örnek) → `docs/stella_crawl/stage-02-hasta_karti.md` |
| Stage 03 Danışan | **22/22 done** → `docs/stella_crawl/stage-03-danisan.md` — P0: YeniDanışan alanları, liste birleştir/Excel, Notlar&Görevler, Teklif KPI |
| Stage 04 Randevu | **25/25 sample done** → `docs/stella_crawl/stage-04-randevu.md` — P0: takvim görünümleri/oda, durum renkleri, liste KPI |
| Stage 05 Gelirler | **25/25 sample done** → `docs/stella_crawl/stage-05-gelirler.md` — P0: YeniSatış yöntem/kur, Kasa özet, satış/bakiye KPI |
| Stage 06 Ana ekran | **18/18 done** → `docs/stella_crawl/stage-06-ana_ekran.md` — P0/P1: Dashboard KPI + widget grid; Son İşlemler; Transfer Takvimi menü |
| Stage 07 Giderler | **20/20 done** → `docs/stella_crawl/stage-07-giderler.md` — P0: GiderKaydet kategori/yöntem; Firma CRUD; firma ödeme; Giderler kur kartları |
| Stage 08 WhatsApp | **17/17 done** → `docs/stella_crawl/stage-08-whatsapp.md` — P0: WA hesap/template/hatırlatma; autoresponder/atama; inbox/rapor |
| Stage 09 Rapor (1/2) | **25/25 sample done** → `docs/stella_crawl/stage-09-rapor_a.md` — P0: Satış raporu; CRM KPI/FB beta; gelmeyen danışan |
| Stage 10 Rapor (2/2) | **15/25 sample done** → `docs/stella_crawl/stage-10-rapor_b.md` — P0: Rapor indeks; teklif raporu KPI |
| Stage 11 Sistem (1/3) | **8/25 sample done** → `docs/stella_crawl/stage-11-sistem_a.md` — P0: Genel ayarlar; personel; API/entegrasyon |
| Stage 12 Sistem (2/3) | **6/25 sample done** → `docs/stella_crawl/stage-12-sistem_b.md` — P0: Yetki grupları; hizmet/ürün/paket |
| Stage 13 Sistem (3/3)+Destek | **5/30 sample done** → `docs/stella_crawl/stage-13-sistem_c.md` — P0: Tanımlamalar ağacı; P2: Helpdesk |
| Excel | 4/4 başlık+örnek satır |
| Onat ses (`Onat-Sk.m4a`) | **tamam** → `docs/Onat_Sk_Transcript.md` |

Aşamalı crawl **tamamlandı** (13/13); gap satırları `docs/stella_crawl/stage-*.md` dosyalarında.

---

## Stella navigasyon (ekranlardan)

Üst menü (hepsi `medidentistanbul.stellamedi.com`):

| Menü | Alt / örnek URL | PNG klasörü |
|------|-----------------|-------------|
| Ana (ev / özet) | `/home/index` — aktif danışan, gün randevu, kasa, ciro, grafikler | `ana ekran özetler paneller` (16) · `ev işareti sekmesi` (2) |
| CRM | `/lead-new`, lead listesi, `/dynamicSearch` | `crm sekmesi içerikleri` (15) |
| DANIŞAN | `/customer-new`, liste | `danışan sekmesi içerikleri` (22) |
| RANDEVU | `/appointment-new`, takvim | `randevu sekmesi` (26) |
| GELİRLER | `/bill-new` · `/accounting/summary` (Kasa) · `/bill` · `/accounting/customerDebtList` · `/reporting/bankStatementList` · `/invoice` · `/accounting/incomings` | `gelirler sekmesi` (30) |
| GİDERLER | `/menu/expense/new` · `/company-new` · `/company` · `/companyBill-new` · `/companyBill` · `/accounting/companyDebtList` · `/confirmation` · `/accounting/expenses` | `giderler sekmesi` (20) |
| WHATSAPP | `/integrations/whatsappManagementPanel` · `/reporting/whatsappReports` · `/integrations/metaManagementPanel` · `/sirius/messages` | `whatsapp sekmesi` (17) |
| RAPOR | `/reporting/index` · `/reporting/sales` · `/reporting/crm` · `/reporting/propose` · … | `rapor sekmesi` (85) |
| SİSTEM | `/management/generalSettings` · `/staff` · `/authGroup` · `/service` · `/definitions/*` · `/integrations` | `sistem sekmesi` (119) |
| DESTEK | `/helpdesk/index` | `destek sekmesi` (3) |

### Hasta kartı (dinamik arama → isim tık)

Örnek: `/customer/{id}/treatmentCard`, `.../complaintList`  
Sol menü (örneklenen): Detaylar, Düzenle, Formlar, Teklif, Randevu, Notlar, Dosya & Fotoğraf, Satış & Tahsilat, Faturalar, İşlem Kartları, Diyetisyen İzlem, Diş Tedavisi, Şikayet.  
Klasör: `crm içindeki … hasta kartı içerikleri` (33 PNG).

---

## Excel → alan eşlemesi

| Dosya | Kullanım | Nefalix hedef |
|-------|----------|---------------|
| `Danisan Listesi (8).xlsx` (50 kolon) | Tam danışan export | `crm_contacts` + ileride FB/TikTok/Google attribution kolonları |
| `Dinamik Arama.xlsx` | Bugün aranacaklar | `clinic-dynamic` / `next_call_date` + segment |
| `Danisan Bakiyeleri Raporu.xlsx` | Vade, tutar EUR/TRY | `crm_payments` / bakiye görünümü (P1) |
| `Kasa Raporu.xlsx` | Para girişi/çıkış, yöntem, kur | `crm_payments` + kasa raporu |

**Danışan Listesi kritik kolonlar (P0):** Ad, Telefon, Segment, Satış temsilcisi, Referans kaynağı, Sms/E-Posta izni, Lead Kayıt Tarihi, Son müşteri notu, Ülke.  
**P1 attribution:** Facebook/TikTok/Google/WhatsApp reklam alanları (20+ kolon) — Meta webhook sonrası.

---

## Gap matrisi (Stella → Nefalix)

Durum: **VAR** (P0 canlıda / importta), **KISMİ**, **YOK**.

| # | Stella alanı | Durum | Nerede değişecek | Öncelik |
|---|--------------|-------|------------------|---------|
| 1 | Yeni Lead formu | KISMİ | `nefalix-landing/nefalix-hasta-crm-app/` + `api/_lib/clinic-crm.js` `clinic-lead-*` — ülke/dil/konu/mesaj alanları eksik olabilir | P0 |
| 2 | Lead listesi (segment filtresi) | KISMİ | `store.js` `getLeads` — sadece YENİ*; Stella’da tüm lead tipleri ayrı listede | P0 |
| 3 | Dinamik Arama tablo + SMS/E-posta | KISMİ | `store.js` + `clinic-dynamic` / `clinic-note-save`; SMS/e-posta toplu **YOK** | P0 (arama) / P2 (SMS) |
| 4 | 5× ulaşılamadı kuralı | VAR | `clinic-crm.js` noteSave + `crm_segments.max_dynamic_attempts` | — |
| 5 | Danışan oluştur / düzenle | KISMİ | Hasta kartı formları; vatandaşlık, adres, meslek alanları | P0 |
| 6 | Hasta kartı: Not + Segment + Temsilci | KISMİ | `HastaKarti` UI + `clinic-note-save` / assign | P0 |
| 7 | Hasta kartı: Teklif (EUR, otel) | VAR (UI patch) | `crm_offers` · YeniTeklif otel/transfer · Teklifler otel satırı — Mac deploy bekliyor | P0 |
| 8 | Hasta kartı: Randevu | KISMİ | `crm_appointments` · `clinic-appointments` — takvim görünümü | P0 |
| 9 | Hasta kartı: İşlem / tedavi kartı | YOK | Yeni tablo veya stub; HBYS/Estesoft bridge (`directives/estesoft_integration.md`) | P1 |
| 10 | Hasta kartı: Dosya & Fotoğraf | YOK | Storage + UI | P2 |
| 11 | Hasta kartı: Satış & Tahsilat / Fatura | KISMİ/YOK | Ödeme KISMİ; fatura YOK | P0 ödeme / P1 fatura |
| 12 | Hasta kartı: Formlar / şikayet / diyet | YOK | Stella-özel klinik formlar — kesim için şart değil | P2 |
| 13 | Randevu takvim / yeni randevu | KISMİ | UI + import açık randevular | P0 |
| 14 | Gelirler: Kasa / satış / bakiye | KISMİ→P0 kasa VAR | `crm_payments` · YeniSatış Kur/yöntem/işlem tipi; banka özet / fatura YOK | P0 kasa ✓ / P1 fatura |
| 15 | Giderler | YOK | Ayrı gider modeli veya `crm_payments` tip=gider | P1 |
| 16 | Ana ekran özet panelleri | YOK/KISMİ | Dashboard kartları (aktif, gün randevu, kasa) — `clinic-reports` genişlet | P1 |
| 17 | Raporlar (finansal/CRM/danışan) | KISMİ | Basit ay sonu VAR; Stella rapor ağacı YOK | P1 |
| 18 | WhatsApp (Stella içi) | YOK* | Nefalix: Evolution/Chatwoot (`directives/evolution_setup.md`) — Stella paneli kopyalanmaz | P1 (inbox bağla) |
| 19 | Sistem: yetki grupları | YOK | Şu an kod-login (`enes`/`abdulkadir`/`kader`); RBAC sonra | P2 |
| 20 | Sistem: tanımlamalar (segment, hizmet, ürün) | KISMİ | Segment/referans CSV seed VAR; hizmet/ürün/paket YOK | P0 segment / P1 hizmet |
| 21 | Destek | YOK | İhtiyaç yok (Estesoft destek) | — |
| 22 | FB/TikTok lead attribution | YOK | Excel kolonları hazır; `clinic-lead-intake` + Meta webhook | P1 |
| 23 | Onat ses notları | VAR | `docs/Onat_Sk_Transcript.md` — lead atama, dinamik gun_offset, teklif, randevu renk, gelir/gider, CRM rapor, ay sonu kesim | P0 bilgi ✓ |

\*WhatsApp: Stella hesabı boş görünüyor; Nefalix zaten ayrı kanal planlıyor.

---

## P0 uygulama sırası (kesim öncesi)

Günlük akış: **Lead → atama → dinamik arama → not/segment → randevu → teklif/ödeme**.

1. **Lead + Dinamik parity** — Stella kolonları (segment, temsilci, referans, tarih); `store.js` + `clinic-crm.js`.
2. **Hasta kartı çekirdek** — detay, not, segment, temsilci, teklif, randevu, basit tahsilat; tedavi/şikayet/form **atlanır**.
3. **Randevu takvim** — oluştur/liste; import doğrula.
4. **Kasa / EUR ödeme** — Stella `Kasa Raporu` alanları (yöntem, kur, referans kodu).
5. **Segment/referans tanımları** — `docs/stella_segments.csv` + `stella_reference_sources.csv` VPS seed teyit.
6. **Onat ses** — `docs/Onat_Sk_Transcript.md` (2026-07-27); kurallar gap’e işlendi.
7. Paralel koşu checklist → `directives/stella_migration.md`.

### Dokunulacak dosyalar (özet)

| Katman | Path |
|--------|------|
| UI | `nefalix-landing/nefalix-hasta-crm-app/` (`store.js`, ekranlar), pack: `execution/pack-nefalix-hasta-crm.py` |
| API | `nefalix-landing/api/_lib/clinic-crm.js` |
| Şema | `supabase/migrations/20260727120*_crm_stella_phase1*.sql` (+ gerekirse yeni alter) |
| Import | `execution/import-stella-crm.py`, `import-stella-definitions.py`, `stella_api.py` |
| SOP | `directives/stella_migration.md`, bu dosya |

> Landing ayrı workspace (`nefalix-landing`); bu repo orchestration + şema + pack script.

---

## P1 / P2 (kesim sonrası)

- **P1:** Giderler, fatura, bakiye listesi, ana özet paneller, rapor ağacı, tedavi kartı stub veya HBYS, Meta lead, WhatsApp inbox ↔ hasta kartı, hizmet/ürün tanımları.
- **P2:** Dosya/foto, şikayet/formlar, yetki grupları (Banko/Satış/Yönetici…), Stella WhatsApp kopyası, diyetisyen formları.

---

## Örnek ekran indeksi (cloud)

ASCII kopyalar (hızlı okuma): `.tmp/stella-samples/{ana,crm,hasta_karti,danisan,randevu,gelir,gider,whatsapp,rapor,sistem}_*.png`  
Asıl paket: `.tmp/stella-discovery/nefalix-crm/`.

---

## Sonraki agent adımı

1. ~~Screenshot crawl~~ **DONE** (13/13, lock off).
2. **Stella UI tıkla-doğrula:** Cursor browser MCP (Chrome/AppleScript kullanılmıyor).  
3. **Mac deploy:** `apply-crm-offers-payments-vps.sh` + `deploy-hasta-crm-from-extract.sh`.  
4. Paralel koşu → Stella kesim (`directives/stella_migration.md`).
