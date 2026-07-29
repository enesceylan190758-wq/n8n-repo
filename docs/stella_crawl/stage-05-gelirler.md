# Stage 05 — Gelirler / Kasa

**Status:** done  
**PNG total:** 30  
**Sample read:** 25/25 (script sample)  
**Tarih:** 2026-07-28

## GELİRLER menü (dropdown)

1. Yeni Satış · 2. Kasa · 3. Satış Listesi · 4. Bakiye Listesi · 5. Banka Özet · 6. Faturalar · 7. Gelirler

## Dosya → URL haritası

| Dosya (kısa) | URL | Ekran |
|--------------|-----|--------|
| 12.24.07–.16 | `/bill-new` | **Yeni Satış** (danışan ara → ödeme satırları + kur) |
| 12.24.22–.37 | `/accounting/summary` | **Kasa** özet kartlar + hareket tablosu |
| 12.24.45–.25.00 | `/bill` | **Satışlar** liste + KPI |
| 12.25.06–.17 | `/accounting/customerDebtList` | **Bakiye Listesi** |
| 12.25.24–.25 | `/reporting/bankStatementList` | **Banka Özet** |
| 12.25.31–.40 | `/invoice` | **Faturalar** (örnek aralıkta boş) |
| 12.25.43–.48 | `/accounting/incomings` | **Gelirler** şube/kur özet kartları |

## Bulgular

### Yeni Satış (`/bill-new`)
Danışan Ara → sekmeler (Danışan Bilgileri / Randevular / Ödemeler / Teklifler / Etiketler).  
Randevu seçimi Evet/Hayır. Tarih+saat, Takip Numarası, Personel.  
Ödeme ekle: **+ Nakit · Kredi Kartı · Banka Hesabı · SGK · Özel Sigorta · Diğer · Puan**; + Yeni Satır.  
Satır: Kapora checkbox, tutar, kur (TRY/EUR…), kredi kartında **TEK ÇEKİM** (taksit). Açık hesap satırı.  
Sağ: Toplam / Dağıtılan + **Kaynak/Hedef Kur / Parite** (TRY→EUR/USD/GBP). Notlar.

### Kasa (`/accounting/summary`)
Özet (2026 yıl örneği): Gelir 378.281 TRY / 125.750 EUR · Gider −1.045.696 TRY / −24.355 EUR · Net.  
Gelir detay ödeme yöntemi (Nakit). Gider kategorileri: Hayır, Klinik, Maaş/personel, Otel/Transfer, Rutin şirket.  
Tablo: Ödeme tarihi, Danışan/Firma, İşlem tipi (**Para girişi** yeşil / **Para çıkışı** kırmızı), Bilgi, Referans, Ödeme yöntemi/aracı, Not, Tutar (EUR+TRY), düzenle/sil. ~115 kayıt.  
İşlemler: Gider Kaydet · Transfer Yap · Döviz al/sat · Excel/Pdf.

### Satışlar (`/bill`)
Kolonlar: Tarih, Referans, Danışan, Detaylar (hizmet/otel), Satış toplamı, Para iadesi, Nakit / KK / Banka, Bakiye (turuncu), Toplam tahsilat (yeşil).  
Filtre: Danışan, Segment, Temsilci, Ülke, Takip no, Referans, İndirim grubu… + Aramayı kaydet.  
KPI: Toplam Tahsilat · Toplam Satış · Toplam Bakiye · Vadesi Geçmiş Bakiye (ör. 14.600 EUR).

### Bakiye Listesi (`/accounting/customerDebtList`)
Satış/vade tarihi, Referans, Danışan, Telefon, Segment (inline), Detaylar, **Geçen süre (gün)** (renk eşiği), Tutar.  
Filtre: Personel, Segment, Tutar aralığı, Vade aralığı, ileri tarihli kayıtlar. Sms/E-Posta · Excel/Pdf.  
Alt toplam: EUR / TRY / USD bakiyeler (ör. 41.008 EUR · 167.825 TRY · 800 USD).

### Banka Özet (`/reporting/bankStatementList`)
Ödeme aracı (Yapı Kredi) × yöntem × kur: Gelir / Gider / Net (TRY/EUR/USD/GBP satırları).

### Faturalar (`/invoice`)
Liste + Excel/Pdf; örnek tarih aralıklarında kayıt yok (klinik fatura kullanımı düşük/boş).

### Gelirler (`/accounting/incomings`)
Yetkili şube toplamı + Medident İstanbul kartları: kur bazında Nakit gelir (EUR/TRY özet).

## Canlı doğrulama (Stella UI)

| URL | Sonuç |
|-----|--------|
| `/bill-new` | **OK** — `Stella - Yeni Satış` |
| `/bill` | **OK** — `Stella - Satışlar` |
| `/accounting/summary` | **OK** — `Stella - Kasa` |
| `/invoice` | **OK** — `Stella - Faturalar` |
| Bakiye / Banka / Gelirler | PNG URL doğrulandı; ayrı tık atlandı (aynı oturum) |
| Kayıt oluşturma | **Yapılmadı** |

## Gap delta → Nefalix

| Stella | Nefalix | Öncelik |
|--------|---------|---------|
| `/bill-new` çok yöntem + kapora + kur parite + takip no | `YeniSatis` — yöntem/kur KISMİ; SGK/sigorta/puan **YOK** | **P0** |
| Kasa gelir/gider/net + para girişi/çıkışı tek ekran | `Kasa` — özet KISMİ; gider kategorileri ayrı | **P0** |
| Kasa: Transfer / Döviz al-sat | **YOK** | P1 |
| Satış liste KPI (tahsilat/satış/bakiye/vadesi geçmiş) | `SatisListesi` — KPI KISMİ | **P0** |
| Bakiye listesi + geçen gün + vade + çoklu kur toplam | `BakiyeListesi` — geçen gün/vade KISMİ | **P0** |
| Banka özet (araç×kur net) | `BankaOzet` stub / **YOK** | P1 |
| Faturalar | **YOK** | P1 |
| Gelirler şube/kur kartları | Dashboard/rapor KISMİ | P1 |
