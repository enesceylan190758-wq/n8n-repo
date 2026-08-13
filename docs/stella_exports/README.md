# Stella Medident dışa aktarımlar (2026-08-13)

Kaynak: `medidentistanbul.stellamedi.com` Excel export + Downloads.

Hasta adı / not / telefon içerir — public paylaşma.

| Dosya | Stella ekranı | Not |
|-------|----------------|-----|
| `Danisan_Listesi.xlsx` | Danışan listesi (27 Tem) | Daha önce verilmişti |
| `Notlar_Gorevler_Listesi.xlsx` | Not & Görev listesi | ~3.3 MB |
| `Randevu_Listesi.xlsx` | Randevu listesi | |
| `Satis_Listesi_2026-08-13.xlsx` | Satış listesi | 13.08.2026 |
| `Kasa_Raporu.xlsx` | Kasa raporu | |
| `hizmetler_fiyat.csv` | Sistem → Hizmetler (ürün/fiyat listesi) | 35 kalem, EUR |

## Ekranlar (`screenshots/`)

| Dosya | Stella |
|-------|--------|
| `stella-segmentler-*.png` | `/definitions/customerSegment` — 38 segment |
| `stella-referans-kaynaklari-*.png` | `/definitions/referenceSource` — 43 kaynak (FB form, WA, Google…) |
| `stella-gider-kalemleri-*.png` | `/definitions/expenseType` — 32 gider kalemi |
| `stella-hizmetler-*.png` | `/service` — 35 ürün (diş + otel + transfer), fiyat EUR |

Segment seed: `docs/stella_segments.csv` (feature branch). Referans seed: `docs/stella_reference_sources.csv`.
