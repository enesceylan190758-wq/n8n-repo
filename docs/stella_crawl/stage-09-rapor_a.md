# Stage 09 — Rapor (1/2)

**Status:** done  
**PNG total:** 43  
**Sample read:** 25/25  
**Tarih:** 2026-07-28

## RAPOR menü

Ana: **Tüm Raporlar** (`/reporting` veya rapor ağacı). Alt klasörler: finansal · danışan · crm (+ stage-10: sık kullanılanlar, raporlarım).

## Dosya → URL haritası (stage 09 kapsamı)

### Finansal raporlar
| URL | Ekran |
|-----|--------|
| `/reporting/sales` | **Satış Raporu** — satır detay + hizmet/paket/ürün grup özetleri (TRY/EUR) |
| `/reporting/serviceSaleCounts` | **Hizmet Satış Adetleri** |
| `/reporting/productSaleCounts` | **Ürün Satış Adetleri** |

### Danışan raporları
| URL | Ekran |
|-----|--------|
| `/reporting/customerCommitment` | Danışan Bağlılığı (+ Sms/E-Posta) |
| `/reporting/patientAccountingPerformance` | Danışan Performans Raporu |
| `/reporting/referencedCustomerPerformanceReport` | Referans Getiren Kişi Performans |
| `/reporting/customerLastVisit` | **Gelmeyen Danışanlar** (+ Excel, Sms/E-Posta) |
| `/reporting/customerPointReport` | Puan Raporu |
| `/reporting/customerObesityTrackingsReport` | Obezite İzlem Raporu |
| `/reporting/customerStaysReport` | Konaklama raporu |

### CRM raporları
| URL | Ekran |
|-----|--------|
| `/reporting/crm` | **Crm Raporu** — 5 sekme (aşağı) |
| `/reporting/representAction` | Temsilci - Segment/Zaman Analizi |

**Crm Raporu sekmeleri:** Crm-Trend · Güncel Temsilci-Segment dağılımı · Temsilci-Segment değerlendirmesi · Temsilci-Referans Kaynağı · **Facebook Reklam Analizi (Beta)**

## Bulgular

### Satış Raporu (`/reporting/sales`)
Kolonlar: Danışan · Ödeme tarihi · Personel · Randevu · Yardımcı personel · Tip (Hizmet) · Hizmet/Ürün/Paket · Ana kategori · İndirim · Tutar (TRY/EUR).  
109 kayıt örneği; sayfalama. Alt özet: Hizmet/Paket/Ürün grupları — DIŞ TEDAVİLERİ · Otel & Konaklama · Transfer.

### Hizmet/Ürün adet
Filtre: tarih · hizmet/ürün · personel · temsilci · grup/marka. Tablo + **Toplam Satış Adetleri** accordion.

### Danışan raporları
Ortak: Arama kriterleri · Aramayı kaydet · **Sms gönder** · **E-Posta gönder** · Excel (Gelmeyen).  
Gelmeyen: geçen gün renk eşiği · son randevu/ödeme içeriği. Referans performans: tahsilat/bakiye toplamları.

### CRM Raporu (`/reporting/crm`)
**KPI (2026 örnek):** Toplam Lead 755 · Danışan 547 · Randevu alan 11 · Satış 8 · Tahsilat 2.1M TRY · Ort. atama 11 saat.  
Grafikler: ülke top-15 · referans kaynağı (WhatsApp ağırlıklı) · segment dağılımı · aylık lead trend · temsilci-segment matris · Facebook kampanya/set lead+satış.

### Temsilci Segment/Zaman (`/reporting/representAction`)
Personel renk başlığı; segment değişim sayısı + ortalama değişim süresi (dk/gün).

## Canlı doğrulama (Cursor browser MCP)

| URL | Sonuç |
|-----|--------|
| `/reporting/sales` | **OK** — yüklendi (Enes Ceylan oturumu) |
| `/reporting/crm` | PNG doğrulandı; ayrı MCP tık atlandı |
| Kayıt oluşturma | **Yapılmadı** |

## Gap delta → Nefalix

| Stella | Nefalix | Öncelik |
|--------|---------|---------|
| Satış raporu satır + grup özet (TRY/EUR) | `Raporlar` **KISMİ/YOK** | **P0** |
| CRM funnel KPI + FB reklam beta | CRM dashboard **YOK** | **P0** |
| Gelmeyen danışan + Sms/E-Posta/Excel | recall workflow **YOK** | P1 |
| Referans performans / bağlılık / puan | **YOK** | P1 |
| Obezite izlem / konaklama raporları | **YOK** | P2 |
