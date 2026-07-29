# Stage 10 — Rapor (2/2)

**Status:** done  
**PNG total:** 42  
**Sample read:** 15/25 (kalan finansal satırlar stage-09 ile örtüşür; `/reporting/index` tam katalog)  
**Tarih:** 2026-07-28

## Rapor indeks (`/reporting/index`)

Kart grupları: **Sık Kullanılanlar** · Finansal · Danışan · Randevu · Sistem · Form & Anket · CRM (ayrı menü).

### Finansal (tam liste)
Satış · Hizmet/Ürün/Paket Satış Adetleri · Tahsilat · Çapraz Satış · Satış Fiyat Analizi · **Prim** · **Kapora** · **Teklif Raporu**

### Danışan (tam liste — stage-09 ile örtüşenler +)
Referans Kaynağı Performans · Transfer · Danışan Temsilci & Segment

### Randevu / Sistem / Form
Yardımcı Personel Görev · TTB İzlem · Paket Takip · Stok · Kapsamlı Güvenlik · Trend · Form/Anket (doldurulan/gönderilen/analiz)

## Dosya → URL (stage 10 yeni)

| URL | Ekran |
|-----|--------|
| `/reporting/index` | Tüm raporlar ağacı |
| `/reporting/revenue` | **Tahsilat Raporu** |
| `/reporting/salePriceComparison` | **Satış Fiyat Analizi** (liste vs ortalama, kırmızı/yeşil fark) |
| `/reporting/bounty` | **Prim Raporu** (personel + ay sekmeleri) |
| `/reporting/propose` | **Teklif Raporu** — KPI kartları + pasta/grafikler |
| `/reporting/myRevenue` | **Benim Tahsilat Raporum** |
| `/reporting/mySales` | **Benim Satış Raporum** |
| `/reporting/productSaleCounts` | Ürün adet (+ Excel) — stage-09 devam |

## Bulgular

### Tahsilat (`/reporting/revenue`)
Kolonlar: Tahsilat tarihi · Referans · Danışan · Personel · Hizmet/Ürün/Paket · Kategori · Ödeme yöntemi · Parite · Toplam (EUR).

### Satış Fiyat Analizi
Satış adeti · toplam · ortalama vs tanımlı fiyat · fark (implant/zirkonyum örnekleri).

### Prim Raporu
Personel seçimi zorunlu; ay sekmeleri (Temmuz 2025→2026).

### Teklif Raporu (`/reporting/propose`)
KPI: toplam teklif 92 · ort. kapanış 19 gün · satışa dönen / olumsuz / beklemede (EUR+TRY).  
Grafikler: durum pasta · olumsuz neden · personel bazlı süre · segment/ürün/hizmet grubu bar.

### Raporlarım
Kişisel filtreli **Benim Tahsilat/Satış** — aynı kolon seti, kullanıcı kapsamı.

## Canlı doğrulama (Cursor browser MCP)

| URL | Sonuç |
|-----|--------|
| `/reporting/index` | PNG katalog; MCP atlandı (sales stage-09 OK) |
| Kayıt oluşturma | **Yapılmadı** |

## Gap delta → Nefalix

| Stella | Nefalix | Öncelik |
|--------|---------|---------|
| Rapor indeks ağacı (6 kategori) | `Raporlar` stub | **P0** |
| Tahsilat + fiyat analizi + prim | **YOK** | P1 |
| Teklif raporu KPI/grafik | Teklifler liste **KISMİ** | **P0** |
| Benim satış/tahsilat (rol bazlı) | **YOK** | P1 |
| Stok/TTB/güvenlik/form raporları | **YOK** | P2 |
