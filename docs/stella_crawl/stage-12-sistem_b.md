# Stage 12 — Sistem (2/3)

**Status:** done  
**PNG total:** 40  
**Sample read:** 6/25 (hizmet/paket/ürün/yetki/tanimlamalar temsil)  
**Tarih:** 2026-07-28

## Dosya → URL haritası

| URL | Ekran |
|-----|--------|
| `/authGroup` | **Yetki Grupları** |
| `/service` | **Hizmetler** katalog |
| `/package` | **Paketler** |
| `/product` | **Ürünler** |
| `/definitions/bankAccounts` | Tanımlamalar → Banka Hesapları (+ `/new` form) |
| `/definitions/*` | Finansal + Diğer tanımlamalar ağacı |

### Yetki grupları (örnek)
Banko · Estetisyen · Satış Temsilcisi · Yönetici · Personel · Tam Yetkili — önem derecesi · kendi danışan görme · iletişim bilgisi görme toggles.

### Hizmetler (`/service`)
Ad · Hizmet grubu · uygulama sıklığı · satış/randevu/teklif sayıları · fiyat/vadeli fiyat · kayıt/fiyat değişim tarihi · silinenleri göster filtresi.

### Tanımlamalar sol menü
**Finansal:** Ödeme Araçları · Banka Hesapları · Gider kategori/kalem · POS taksit · Döviz kurları  
**Diğer:** Şubeler · İşlem kartı · Formlar · Onam · Dinamik alanlar · İndirim grupları · …

## Canlı doğrulama (Cursor browser MCP)

| URL | Sonuç |
|-----|--------|
| `/service` | **OK** |
| `/authGroup` | **OK** |
| `/authorizationGroup` | Yönlendirme/boş — PNG `/authGroup` kullan |
| Kayıt oluşturma | **Yapılmadı** |

## Gap delta → Nefalix

| Stella | Nefalix | Öncelik |
|--------|---------|---------|
| Yetki grupları (6 rol + iletişim gizleme) | `Yetki` stub | **P0** |
| Hizmet/ürün/paket fiyat katalog | `Hizmet`/`Urun`/`Paket` **KISMİ** | **P0** |
| Tanımlamalar (banka, gider kalemi, POS) | SistemTanim **KISMİ** | P1 |
