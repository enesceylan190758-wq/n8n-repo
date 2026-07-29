# Stage 02 — Hasta kartı sekmeleri

**Status:** done  
**PNG total:** 33  
**Sample read:** 15/25 (eşit aralıklı örnek + kritik sekmeler)  
**Tarih:** 2026-07-28  
**Örnek hasta:** Kadriye Bak · `#10686` · UUID `e48fd336-75fc-f011-9042-d9f82e27061e`

## Giriş akışı

Dinamik Arama (`/dynamicSearch`) → satırda **isim tık** → `/customer/{uuid}/…`

CRM dropdown (doğrulandı): Yeni Lead, Lead Listesi, Salesline, Dinamik Arama, Dinamik Arama-Havuz, Lead Dönüşüm Geçmişi, Lead Takibi, CRM Ayarları.

## Sol menü (tam IA)

| Sekme | URL suffix | P0 kesim? |
|-------|------------|-----------|
| Detaylar | `/` (summary) | **Evet** |
| Düzenle | `/summary/edit` | **Evet** |
| Formlar | `/formList` | Hayır (P2) |
| Teklif | `/proposeList` | **Evet** |
| Randevu | `/appointmentList` | **Evet** |
| Notlar | (notes) | **Evet** |
| İşlem Kartları | | P1 |
| Dosya & Fotoğraf | `/multimedia` | P2 |
| Satış & Tahsilat | `/accountingList` | **Evet** (basit) |
| Faturalar | | P1 |
| Puan | `/customerPoint` | Hayır |
| Paket Takibi | | P1 |
| İletişim | | P2 |
| Tanılar | `/customerDiagnose` | Hayır |
| Transfer & Konaklama | | P1 (otel/transfer teklifte) |
| Diyetisyen / Obezite / Reçete / Tıbbi Rapor / Diş / Göz / Tahlil / Diyet / Şikayet | çeşitli | Hayır (klinik form) |

## Sekme bulguları

### Detaylar
3 kolon: İşlemler (WA, geçmiş, medikal indir, dosya no, Sil) · kişisel/adres/diğer (segment, temsilci, FB reklam alanları) · Notlar timeline + Hızlı Not.  
Üst KPI: Randevu/Satış/Teklif sayaç + **+ Yeni**. Etiketler. Kayıt notu (`MJA FORM en_US`).  
FB bloğu: Sayfa, Kampanya, Ad Set, Reklam, Form, LeadgenID.

### Düzenle (`/summary/edit`)
Adres (ülke/şehir/ilçe/TZ/adres); SMS/E-posta izni; Tip=Potansiyel Hasta; dil; ilgili personel checkbox; etiket; kayıt notu; medikal (boy/kilo/BMI + anket alanları).

### Formlar (`/formList`)
Alt tab: Formlar & Anketler · Onam · Satış Sözleşmesi · Yolculuk ve Tedavi Planı.  
Örnek form adları: Memnuniyet Anketi; Onam (geçici diş, görsel izin, sedasyon).

### Teklif (`/proposeList`)
Kolon: Tarih, Ref kodu, Detaylar (temsilci × kalem + EUR rozet), Toplam EUR, **Segment**, **Ana Durum** (Beklemede…), Durum, İşlemler.  
Örnek: `7VC70` · 5.000 EUR · İMPLANT NEODENT STRAUMAN.

### Randevu (`/appointmentList`)
İşlemler: Yeni Randevu · Excel · PDF. (örnek hasta boş)

### Satış & Tahsilat (`/accountingList`)
Üç blok: Satışlar · Bakiye Listesi · Tahsilat — her birinde İşlemler + Ara.

### Dosya & Fotoğraf (`/multimedia`)
Yeni Dosya/Fotoğraf; alt: Dökümanlar, Hassas, Instagram, İşlem Çizimleri, Şablonlar, Öncesi/Sonrası.

### Puan / Tanılar / Diyet vb.
Boş liste + İşlemler — kesim için şart değil.

## Canlı doğrulama

Browser MCP yok. Stella **API** token OK (CustomerApi). Panel tıkla: sonraki tur (Playwright / Cursor browser + panel kullanıcı).

## Gap delta

| Stella kart | Nefalix | Öncelik |
|-------------|---------|---------|
| Detay + hızlı not + segment timeline | HastaKarti KISMİ | P0 |
| Düzenle (izin, dil, ülke, personel) | form alanları eksik | P0 |
| Teklif EUR + segment + ana durum | otel/transfer patch var; ana durum/ref kod kontrol | P0 |
| Randevu listesi + Yeni | KISMİ | P0 |
| Satış/Bakiye/Tahsilat üçlü | Kasa/ödeme KISMİ | P0 |
| FB Leadgen alanları | YOK | P1 |
| Formlar/onam/diş/diyet… | YOK (bilinçli) | P2 |
| Multimedia | YOK | P2 |
