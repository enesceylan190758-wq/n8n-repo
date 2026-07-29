# Stage 06 — Ana ekran / ev

**Status:** done  
**PNG total:** 18  
**Sample read:** 18/18  
**Tarih:** 2026-07-28

## Dosya → URL haritası

| Dosya (kısa) | URL | Ekran |
|--------------|-----|--------|
| 11.51.23–.47, 11.52.03–.06 | `/home/index` | **Göstergeler** dashboard (KPI + widget grid) |
| 11.51.52 | `/sirius/messages` | Üst WhatsApp ikonu → **Sirius** mesaj inbox |
| 12.10.02–.12 | `/reporting/lastTransactions` | Ev menü → **Son Yapılan İşlemler** |

## Ev / home menü

- Ev ikonu altı (PNG): **Göstergeler** · **Son Yapılan İşlemler**
- Title canlıda: `Stella - Göstergeler`

## Bulgular — Dashboard (`/home/index`)

### Üst KPI kartları (döner / kişiselleştirilebilir)
Örnek değerler (aynı gün farklı anlar):
- Aktif / Toplam / Potansiyel / Pasif Danışan → DANIŞAN LİSTESİ
- Günün randevuları / Beklemede / Tamamlanan → TAKVİME GİT
- Günün kasa toplamı (TRY) → KASAYA GÖZ AT
- Ciro farkı (30 gün) % → SATIŞ LİSTESİ

### Widget grid (Estesoft Bildirimleri / paneller)
| Widget | Tip |
|--------|-----|
| Yoğunluk haritası | Bubble: danışan/randevu/satış/teklif/lead |
| Yeni Danışan ve Lead sayıları | Line (+ Duyurular / + Yeni) |
| Danışan tipleri dağılımı | Pie (Aktif vs Potansiyel) — panel başlığı “Döviz Kurları” da görülebilir |
| Günün en çok uygulanan işlem grupları | Bar (çoğu boş) |
| Sistem kullanım performansı | Radar (danışan, randevu, satış, teklif, not, işlem kartı) |
| Tarihe göre randevu dağılımı | Area |
| Tahsilat - Satış tutarları (TRY) | Dual line |
| Randevu tarih-saat ısı haritası | Heatmap |
| Günün en çok satılanları | Bar |
| Personele / tipine / odaya göre randevu dağılımı | Bar/pie |

### Header yan ürünleri
- Global Ara · WA ikonu · Bildirimler (boş modal) · Ev · Profil (Profilim / Çıkış) — örnek kullanıcı Abdülkadir (e-posta UI’da; secret değil ama dokümana şifre yok).
- WA ikonu → `/sirius/messages` (kanal: WA/IG/FB; sohbet listesi + MessageStatistics).

### Menü dropdown haritası (ana ekrandan tıklandı — stage 07+ için)
- **RANDEVU:** Yeni Randevu · Takvim · Randevu Listesi · Etkinlikler · **Transfer Takvimi**
- **GİDERLER:** Gider Kaydet · Yeni Firma · Firma Listesi · Yeni Ödeme/Ürün Alımı · Firma Ödemeleri · Ödenecekler · Onaylar · Giderler
- **WHATSAPP:** Yönetim Paneli · Raporları · Meta Yönetim Paneli
- **RAPOR:** Tüm Raporlar
- **SİSTEM:** Yetki · Ayarlar · Güvenlik · Personel · Prim · Entegrasyonlar · Api · Hizmet · Paket · Ürün · Tanımlamalar · Toplu Sms Onayları
- **DESTEK:** Kayıtlarım · Yeni Destek Kaydı

### Son Yapılan İşlemler (`/reporting/lastTransactions`)
Audit log: İşlem tarihi, yapan, tip (Giriş Yap…), Modül (Oturum), Ref, IP. ~549 kayıt; ApiUser yoğunluğu görünür.

## Canlı doğrulama (Stella UI)

| Adım | Sonuç |
|------|--------|
| `/home/index` | **OK** — `Stella - Göstergeler` |
| Widget tıklama / duyuru oluşturma | **Yapılmadı** |

## Gap delta → Nefalix

| Stella | Nefalix | Öncelik |
|--------|---------|---------|
| KPI kartları (aktif danışan, gün randevu, kasa, ciro %) | `Dashboard` — kart seti KISMİ | **P0**/P1 |
| Yoğunluk / lead-danışan trend / tip pie | Dashboard grafikleri **YOK**/KISMİ | P1 |
| Tahsilat-satış TRY + randevu ısı haritası | **YOK** | P1 |
| Personel/oda/tip randevu dağılımı widget | **YOK** | P1 |
| Son Yapılan İşlemler audit | `SonYapilanIslemler` stub / **YOK** | P1 |
| Sirius omnichannel inbox (header WA) | Evolution/Chatwoot ayrı — Stella Sirius kopyası **YOK** | P2 |
| Transfer Takvimi (RANDEVU menü) | **YOK** | P1 |
