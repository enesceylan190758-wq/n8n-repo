# Stage 07 — Giderler

**Status:** done  
**PNG total:** 20  
**Sample read:** 20/20  
**Tarih:** 2026-07-28

## GİDERLER menü (dropdown)

1. Gider Kaydet · 2. Yeni Firma · 3. Firma Listesi · 4. Yeni Ödeme/Ürün Alımı · 5. Firma Ödemeleri · 6. Ödenecekler · 7. Onaylar · 8. Giderler

(Kaynak: stage-06 dropdown map + bu aşama PNG URL’leri.)

## Dosya → URL haritası

| Dosya (kısa) | URL | Ekran |
|--------------|-----|--------|
| 12.26.33 | (local Nefalix Dashboard HTML) | Pakette home mock — Stella Giderler değil |
| 12.30.40–.46 | `/menu/expense/new` | **Gider Kaydet** form + kategori/ödeme dropdown |
| 12.30.52 | `/company-new` | **Yeni Firma** |
| 12.30.59–.02 | `/company` | **Firmalar** liste (2 kayıt) |
| 12.31.09 | `/companyBill-new` | **Yeni Firma Ödemesi** (firma ara) |
| 12.31.14–.16 | `/companyBill` | **Firma Ödemeleri** (örnek boş) |
| 12.31.19–.25 | `/accounting/companyDebtList` | **Ödenecekler** (örnek boş) |
| 12.31.27–.29 | `/confirmation` | **Onaylar** (örnek boş) |
| 12.31.35–.41 | `/accounting/expenses` | **Giderler** özet kartlar (yıllık) |

## Bulgular

### Gider Kaydet (`/menu/expense/new`)
Alanlar: **Kategori** · **Gider Kalemi** · **Fatura no/Ek Bilgi** · **Gider tarihi** · **Tutar** + kur (TRY) · **Ödeme Yöntemi** · **Notlar**.  
Butonlar: Vazgeç · Kaydet.

**Kategori örnekleri:** Hayır · Klinik Giderleri · Maaş ve personel Giderleri · Otel Konaklama ve Transfer Giderleri · Reklam Giderleri · Rutin Şirket Giderleri.  
**Gider Kalemi:** kategori seçilmeden “Sorry, no matching options.” (bağımlı select).  
**Ödeme Yöntemi:** Banka Hesabı · Devir Kasa · Diğer · Kliniğe Ait Kredi Kartı · Nakit (varsayılan).

### Yeni Firma (`/company-new`)
Firma Adı · Firma Kodu · Fatura adı · Vergi Dairesi · Vergi no · Ülke (Türkiye) · Şehir · Adres · Telefon / Telefon 2 · E-Posta / E-Posta 2 · İnternet sitesi · Vazgeç/Kaydet.

### Firmalar (`/company`)
Kolonlar: Ad · Fatura adı · Telefon · E-Posta · İşlemler.  
Örnek: DENTALZONE · Şirket giderleri (fatura adı MediDent). 2 kayıt.  
İşlemler + **Yeni Firma**.

### Yeni Firma Ödemesi (`/companyBill-new`)
Önce firma arama (`Ara (Medident Istanbul)`); alanlar arama sonrası açılır (PNG’de boş arama durumu).

### Firma Ödemeleri (`/companyBill`)
Filtre: Değişiklik tarihi · Firma · Tarih aralığı. İşlemler. Örnek aralıkta kayıt yok.

### Ödenecekler (`/accounting/companyDebtList`)
Liste + İşlemler: **Excel İndir** · **Pdf İndir**. Örnek boş.

### Onaylar (`/confirmation`)
Filtre: Tarih aralığı · Onay durumu · Bilgi. Örnek 01.07–17.07.2026 boş.

### Giderler (`/accounting/expenses`)
Tarih aralığı + **Kur** filtresi.  
Özet kartlar (2026 yıl örneği, Kasa ile uyumlu):  
Yetkili şube toplamı / Medident İstanbul — **−24.355 EUR** · **−1.045.696,25 TRY** (Nakit kırılımı).  
Tek gün (16.07.2026) filtresinde kayıt yok → kartlar yıllık aralıkta doluyor.

## Canlı doğrulama (Stella UI)

| URL | Sonuç |
|-----|--------|
| `/menu/expense/new` | **OK** — `Stella - Gider Kaydet` |
| `/accounting/expenses` | **OK** — `Stella - Giderler` |
| `/company-new` | **OK** — `Stella - Yeni Firma` |
| `/company` | **OK** — `Stella - Firmalar` |
| `/companyBill-new`, `/companyBill`, `/companyDebtList`, `/confirmation` | PNG URL doğrulandı; oturum sonunda Chrome pencere hatası (−1719) — yeniden tık atılmadı |
| Kayıt oluşturma | **Yapılmadı** |

## Gap delta → Nefalix

| Stella | Nefalix | Öncelik |
|--------|---------|---------|
| Gider Kaydet: kategori→kalem bağımlı + 5 ödeme yöntemi + kur | `GiderKaydet` / gider form — kategori/kalem/yöntem **KISMİ** | **P0** |
| Firmalar (tedarikçi) CRUD + vergi/iletişim | `FirmaListesi` / `YeniFirma` — alan seti **KISMİ** | **P0** |
| Yeni Firma Ödemesi + Firma Ödemeleri listesi | Ürün alımı / firma ödeme akışı **YOK/KISMİ** | **P0** |
| Ödenecekler (firma borç) + Excel/Pdf | **YOK** | P1 |
| Onaylar (gider onay workflow) | **YOK** | P1 |
| Giderler şube/kur özet kartları (negatif Nakit) | `Giderler` / Kasa gider kırılımı **KISMİ** | **P0** |
| Kasa ↔ Giderler tutar tutarlılığı (aynı EUR/TRY) | Tek kaynak özet modeli | P1 |
