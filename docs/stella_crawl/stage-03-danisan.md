# Stage 03 — Danışan sekmesi

**Status:** done  
**PNG total:** 22  
**Sample read:** 22/22  
**Tarih:** 2026-07-28

## Dosya → URL haritası

| Dosya (kısa) | URL | Ekran |
|--------------|-----|--------|
| 12.14.29–.39 | `/customer-new` | **Yeni Danışan** formu (kişisel → adres → diğer → medikal) |
| 12.14.46–.57 | `/customer` | **Danışanlar** listesi (+ İşlemler, kolon filtre, arama) |
| 12.15.01 | `/customer` | Arama kriterleri paneli (geniş filtre seti) |
| 12.15.05–.08 | `/propose-new` | **Yeni Teklif** — danışan ara (typeahead) |
| 12.15.27–.43 | `/propose` | **Teklifler** listesi + KPI özet (Beklemede/Satış/Olumsuz) |
| 12.15.48–.57 | `/customerNote` | **Notlar & Görevler** (~46k kayıt) |
| 12.16.01–.03 | `/complaint` | **Şikayetler** (filtre + boş sonuç) |

## Bulgular (tıkla → ne olur — ekrandan)

### Yeni Danışan (`/customer-new`)
Bölümler:
1. **Kişisel Bilgi:** Ad Soyad, Vatandaşlık no (+ doğrula ikonu), Cinsiyet, Uyruk (TR), Telefon (**kırmızı/zorunlu**), E-Posta, Satış temsilcisi (default Abdülkadir), Segment, Referans kaynağı, Doğum tarihi, Meslek.
2. **Adres:** Ülke (TR), Şehir, İlçe, Zaman dilimi, Adres textarea.
3. **Diğer Bilgiler:** Sms izin (Evet), E-Posta izin (Evet), İletişim Kaynağı/Tercihi, Referans olan danışan (ara), İndirim grubu, Dil (Türkçe), İlgili Personel (checkbox: Abdülkadir / Enes / Kuays), Etiketler, Kayıt notu.
4. **Medikal Bilgiler:** Boy, Kilo, BMI (readonly), Alerji, İlaçlar, Teşhis, Ameliyat, Alkol/Sigara, Otoimmün, Uygulamalar, Medikal cihaz tedavileri.
Butonlar: Vazgeç (kırmızı) · Kaydet (yeşil).

### Danışanlar (`/customer`)
- ~**7500** kayıt; sayfa başına 30.
- Varsayılan kolonlar: checkbox, ID, durum ikonu (turuncu/yeşil check), Ad, Ülke (bayrak), Satış Temsilcisi, Kayıt tarihi, İşlemler (chat + ok + menü).
- **İşlemler** dropdown: Yeni Danışan · Hasta Birleştir · Excel İndir · Pdf İndir · Dinamik Alanları Excel İndir · Excel'den Aktar.
- Toplu: **Sms gönder**, **E-Posta gönder**, Ara.
- **Kolonları filtrele:** ID/Ad/Temsilci/Kayıt tarihi açık; gizli örnekler: E-Posta, Telefon, Yaş, Cinsiyet, Şehir, Referans, Facebook/TikTok Formu.
- Arama kriterleri (geniş): Arama metni, Danışan tipi, Dil, Etiket, FB/Google reklam, Hizmet grubu, İlgili Personel, KVKK Onay, Bakiyesi olan, Doğduğu ay, İletişim izin, İndirim grubu, Lead Kayıt Tarihi, Referans, Cinsiyet, Meslek, …

### Yeni Teklif (`/propose-new`) — DANIŞAN menü altı
Önce **Danışan Ara** typeahead zorunlu; örnek arama `sda` → test kayıtları (+49 telefonlar).

### Teklifler (`/propose`)
Kolonlar: Tarih, Referans kodu, Danışan, Telefon, Detaylar (temsilci + hizmet satırı), Toplam (EUR rozet), Segment (inline dropdown), Ana Durum (Beklemede/Satış/…), Durum, İşlemler.  
Filtre: Ana Durum, Danışan, Hizmet/Paket/Ürün, Personel, Referans, Segment, Olumsuz neden…  
Alt KPI kartlar (ör. yıl filtresi): Beklemede **518.150 EUR** · Satış **43.000 EUR** · Olumsuz **28.250 EUR**.  
Sms / E-Posta toplu + Excel/Pdf (İşlemler).

### Notlar & Görevler (`/customerNote`)
~**46.055** kayıt. Kolonlar: Danışan, Not, Not tipi, Hatırlatma tarihi, Personel, Oluşturan, Kayıt tarihi, Segment, Durum (toggle), Sesli Not mu (X), Sil.  
İşlemler: Excel İndir · Pdf İndir. Filtre: not tipi, hatırlatma, segment, oluşturan, personel…

### Şikayetler (`/complaint`)
Filtre: Aksiyon, Aksiyon sonucu, Danışan, Personel, Şikayet durumu/kanalları/tipi. Örnek tarih aralığında kayıt yok (sarı banner).

## Canlı doğrulama (Stella UI)

| Adım | Sonuç |
|------|--------|
| Chrome oturumu `/home/index` → `URL` set `/customer` | **OK** — title `Stella - Danışanlar`, URL `…/customer` |
| `/customer-new` | **OK** — title `Stella - Yeni Danışan` |
| Kayıt oluşturma / silme | **Yapılmadı** (destructive test data yok) |

Oturum: panel kullanıcı (AB); şifre dokümana yazılmadı.

## Gap delta → Nefalix

| Stella | Nefalix | Öncelik |
|--------|---------|---------|
| `/customer-new` tam form (vatandaşlık, adres, SMS/e-posta izin, medikal, ilgili personel) | `YeniDanisan` — alanlar KISMİ (izin/medikal/vatandaşlık eksik) | **P0** |
| `/customer` liste + ülke bayrak + İşlemler (birleştir/Excel import) | `DanisanListesi` — birleştir/Excel aktar **YOK** | **P0** |
| Danışan arama kriterleri (KVKK, bakiye, doğduğu ay, reklam alanları) | KISMİ filtre seti | P0/P1 |
| `/propose` liste + EUR KPI + inline segment/ana durum | Teklifler var; KPI özet + inline durum KISMİ | **P0** |
| `/propose-new` danışan-öncelikli typeahead | `YeniTeklif` — danışan ara akışı KISMİ | P0 |
| `/customerNote` global not/görev listesi + hatırlatma + sesli not | `NotlarGorevler` — hatırlatma/sesli **YOK**; ölçek (46k) yok | **P0** |
| `/complaint` şikayet listesi | Hasta kartı şikayet P2; global liste **YOK** | P2 |
| Toplu SMS/E-posta (liste + teklif) | **YOK** | P2 |
