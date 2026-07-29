# Stage 01 — CRM / Lead / Dinamik arama

**Status:** done  
**PNG total:** 17  
**Sample read:** 17/17  
**Tarih:** 2026-07-28

## Dosya → URL haritası

| Dosya (kısa) | URL | Ekran |
|--------------|-----|--------|
| 16.23.37 / .40 | `/staff/profile` | Personel profil / kişisel dashboard (hedef, not, randevu, teklif, tahsilat) |
| 12.10.44 | `/lead-new` | **Yeni Lead** formu |
| 12.10.47 | `/lead` | **Leadler** listesi |
| 12.10.52 | `/salesline` | **Salesline** kanban (segment kolonları) |
| 12.10.56 | `/dynamicSearch` | **Dinamik Arama** tablo |
| 12.11.02–.09 | `/dynamicSearchPool` | **Dinamik Arama – Havuz** (+ filtre UI) |
| 12.11.13–.19 | `/LeadConversionLog` | **Lead Dönüşüm Geçmişi** |
| 12.11.29 | `/LeadConsultationList` | **Lead Takibi** |
| 12.11.42 / .52 | `/CRMSettings/autoAssignRules` | Otomatik atama kuralları (boş) |
| 12.11.45 | `/CRMSettings/crmGeneralSettings` | CRM genel ayarlar (toggle’lar) |

## Bulgular (tıkla → ne olur — ekrandan)

### Yeni Lead (`/lead-new`)
Alanlar: Ad Soyad, E-Posta, Ülke (TR default), Telefon (zorunlu/kırmızı), Referans kaynağı, Dil, Konu, Mesaj.  
Butonlar: Vazgeç (kırmızı) · Kaydet (yeşil).

### Leadler (`/lead`)
Kolonlar: Kayıt tarihi, Ülke, Lead (ad), İşlemler (ok + menü).  
Arama kriterleri + Kolonları filtrele + İşlemler.

### Salesline (`/salesline`)
Sol filtre: Segment / Segment Grubu, Tarih, Ülke, Referans, Dil, Aramayı Kaydet.  
Kanban kolon örnekleri: *Ulaşılamadı Tekrar Aranacak*, *Sıcak Alacak*, *Bilet Bekleniyor*, *Analiz Verilecek* — sayaç + % + TRY.

### Dinamik Arama (`/dynamicSearch`)
Kolonlar: Dosya no, Ülke, Danışan, Telefon, **Segment** (renkli rozet), Satış temsilcisi, Referans kaynağı, Kayıt/Değişiklik tarihi, İşlemler (3 ikon).  
Toplu: **Sms gönder**, **E-Posta gönder**, Ara.

### Dinamik Havuz (`/dynamicSearchPool`)
Ayrı liste; filtre: Havuza alınma tarihi, Referans, Temsilci, Segment. Kayıt yok örneği sarı banner.

### Lead Dönüşüm Geçmişi
Filtre: İşlem tarihi, Dönüştüren (Enes / Abdülkadir / Kuays…), Danışan, Kaynak, Segment, Temsilci, İşlem kodu.

### Lead Takibi (`/LeadConsultationList`)
Filtre: Arama metni, Durum, Kayıt tarihi, Oluşturan, Segment.

### CRM Genel Ayarlar (önemli iş kuralları)
| Ayar | Değer (ekran) |
|------|----------------|
| Dinamik aramada referans kaynağı + filtre | AÇIK |
| Gün sayısı geçen lead → havuza otomatik | KAPALI |
| Danışan kayıt/düzenle’de temsilci seçimi temsilciye göster | AÇIK |
| Manuel lead kaydında numara kontrolü | Danışan |
| Numara zaten varsa | Eski danışanı kullanmayı dene |
| İşlemde temsilciyi güncelle | false |
| Segmenti “Tekrar Gelen Lead” yap | false |

Otomatik atama kuralları: boş (henüz kural yok).

### Staff profil (`/staff/profile`) — CRM dışı ama navigasyon bağlamı
Kişisel KPI: hedef, ilgilendiğim danışan, satış, kaydettiğim, randevu, teklif, tahsilat; Son 10 Notum; Gelecek 10 Randevu; Son 10 Teklif.

## Canlı doğrulama (Stella UI)

- Bu ortamda **browser MCP yok**; panel tıkla-doğrulama ertelendi.
- API token (`.env` `ESTESOFT_*`) ayrı kanal — UI cookie oturumu değil.
- Sonraki: panel kullanıcı (örn. Abdülkadir e-posta) + şifre ile Playwright/Cursor browser; CRM menü → Lead / Dinamik yollarını doğrula.

## Gap delta → Nefalix

| Stella | Nefalix | Öncelik |
|--------|---------|---------|
| `/lead-new` alanları (ülke, dil, konu, mesaj) | `YeniLead` / `clinic-lead-*` — eksik alanlar | P0 |
| `/lead` liste + ülke + işlem ok | `LeadListesi` — temsilci/referans eklendi; ülke/işlem menü KISMİ | P0 |
| `/salesline` kanban | **YOK** (`Salesline.dc.html` stub olabilir) | P1 |
| `/dynamicSearch` SMS/E-posta toplu | **YOK** | P2 |
| `/dynamicSearchPool` | Saha CRM’de havuz var; Hasta CRM’de KISMİ | P0/P1 |
| Lead dönüşüm log / Lead takibi | **YOK** | P2 |
| CRM genel ayarlar (numara dedup, havuz auto) | Kodda kısmi; ayar UI **YOK** | P1 |
| Otomatik atama kuralları | **YOK** (manuel assign VAR) | P1 |
| Staff profil KPI | Dashboard P1 | P1 |
