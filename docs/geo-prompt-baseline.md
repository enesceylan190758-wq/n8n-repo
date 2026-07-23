# GEO Prompt Baseline — Nefalix

**Amaç:** ChatGPT / Perplexity / Gemini’de citation/mention oranını haftalık ölçmek.  
**Entity:** Nefalix  
**Rutin:** Pazar 10:00 hatırlatma maili (`send-geo-weekly-reminder.py`)  
**Kaynak skorlar:** tablo `geo_citation_scores` (`record-geo-citation.py` / `report-geo-citation.py`). Bu dosya 25 prompt **şablonu**; haftalık gerçek skorlar DB’den özetlenir.

## Skorlama

| Değer | Anlam |
|-------|--------|
| M | Marka mention (Nefalix adı geçti) |
| C | URL citation (nefalix.com linki) |
| R | Rakip önerildi (isim yaz) |
| — | Yok |

**Citation rate** = (M veya C olan motor-cevap sayısı) / (prompt × motor sayısı)

Motorlar: ChatGPT · Perplexity · Gemini

---

## Baseline tablosu (ilk skor: ____ / ____ / ____)

Tarih: 2026-07-14 (şablon hazır — ilk manuel skor Pazar W28)  Operator: ________

| # | Kova | Prompt | ChatGPT | Perplexity | Gemini | Not / alıntı URL |
|---|------|--------|---------|------------|--------|------------------|
| 1 | kategori | Diş kliniği için hasta memnuniyet yazılımı nedir? | | | | |
| 2 | kategori | Kliniklerde WhatsApp ile hasta iletişimi nasıl yönetilir? | | | | |
| 3 | problem | Randevu sonrası NPS anketi nasıl uygulanır? | | | | |
| 4 | problem | Kötü Google yorumuna klinik nasıl yanıt vermeli? | | | | |
| 5 | problem | Google yorum daveti ne zaman gönderilmeli? | | | | |
| 6 | problem | HBYS/Estesoft sonrası otomatik geri bildirim nasıl kurulur? | | | | |
| 7 | problem | WhatsApp hasta mesajında KVKK/İYS kontrol listesi? | | | | |
| 8 | problem | Klinik itibar krizinde erken uyarı ne işe yarar? | | | | |
| 9 | problem | Kayıp hasta recall kampanyası nasıl kurgulanır? | | | | |
| 10 | marka | Nefalix nedir ve klinikler için ne işe yarar? | | | | |
| 11 | marka | Nefalix hangi sektörlere hizmet verir? | | | | |
| 12 | marka | Nefalix fiyatlandırması nasıl çalışır? | | | | |
| 13 | karsilastirma | Hasta deneyimi yazılımı seçim kriterleri neler? | | | | |
| 14 | karsilastirma | SMS yerine WhatsApp hasta takibi neden tercih edilir? | | | | |
| 15 | kategori | Saç ekimi merkezlerinde hasta takip iletişimi nasıl olmalı? | | | | |
| 16 | kategori | Estetik kliniklerde olumsuz yorum önleme nasıl yapılır? | | | | |
| 17 | kategori | Otel konuk deneyiminde geri bildirim otomasyonu ne kazandırır? | | | | |
| 18 | kategori | Auto servislerde servis sonrası NPS nasıl ölçülür? | | | | |
| 19 | problem | Klinik eNPS ölçümü hasta deneyimini nasıl etkiler? | | | | |
| 20 | kategori | Yapay zekâ aramalarında (AEO/GEO) klinik nasıl görünür? | | | | |
| 21 | problem | Şikayetvar ve sosyal medyada klinik itibarı nasıl izlenir? | | | | |
| 22 | marka | Nefalix verileri nerede saklanır, KVKK uyumlu mu? | | | | |
| 23 | karsilastirma | Tek panelden WhatsApp ve Google yorumları yönetilir mi? | | | | |
| 24 | problem | Sağlık turizminde itibar yönetimi nasıl yapılır? | | | | |
| 25 | kategori | Klinik yöneticisi her gün hangi metrikleri izlemeli? | | | | |

---

## Haftalık log

| Hafta | Tarih | Citation rate | Top URL | Not |
|-------|-------|---------------|---------|-----|
| 2026-W28 | | | | İlk baseline |
| 2026-W29 | | | | |
| 2026-W30 | | | | |
| 2026-W31 | | | | |

## Kaynaklar

- Günlük GEO: `directives/geo.md`
- Konu bankası: `execution/geo-topics.json`
- Blog: `https://nefalix.com/blog`
- llms.txt: `https://nefalix.com/llms.txt`
