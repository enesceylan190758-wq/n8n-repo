# YouTube + GEO (kanal içeriği)

## Hedef

[@Nefalixai](https://www.youtube.com/@Nefalixai) videoları AI ve insanlar için **answer-first** açıklama taşısın; her videoda public Nefalix URL (`/geo`, ürün, blog) olsun. Entity adı: **Nefalix**.

Hazır metinler: [`docs/youtube-geo-pack.md`](../docs/youtube-geo-pack.md)

## Açıklama şablonu (zorunlu alanlar)

1. **Direkt cevap** — ilk 40–60 kelime, başlığa cevap (filler yok)
2. **3 madde** — ne anlatıldığı
3. **SSS** — 3 kısa Q&A (görünür metin)
4. **Linkler** — en az: `https://nefalix.com/geo` + ilgili ürün/blog + demo
5. **Uyarı** — tıbbi tavsiye / sonuç garantisi yok; KVKK notu

Tıbbi iddia, abartılı “%X hasta artışı” uydurma. Orijinal metrik yoksa yazma.

## Yayın ritmi

| Kural | Detay |
|-------|--------|
| Sıklık | **Haftada 1** yeni video (aynı güne 7 video basma) |
| Batch | Yasak — algoritma + güven için serpilmiş yayın |
| Yeni video | Pack şablonunu kopyala; güncel `/geo/YYYY-MM-DD` veya ilgili blog ekle |
| Featured (site) | `I9W_oyS_b1o` — [`nefalix-landing/youtube-channel.js`](../nefalix-landing/youtube-channel.js) |

## Pin / izleme sırası (Studio)

1. Nefalix Nedir? (`kx1A60aNjiw`)
2. Ne kazandırır? (`I9W_oyS_b1o`)
3. Bir hasta üç senaryo (`hkncjql8eSE`)
4. 8 Modül (`zharVhgk-Ec`)

## Kanal Hakkında

One-liner (Organization ile aynı):

> Nefalix: klinikler için WhatsApp, NPS, Google yorumları ve hasta geri bildirimi otomasyonu. KVKK uyumlu, Türkiye'de barınır.

Linkler: nefalix.com · https://nefalix.com/geo · Cal.com demo

## Site ilişkisi

- Kaynaklar `#youtube` grid + `#geo` paketleri
- `llms.txt` kanal satırı
- GEO günlük cron sitede; video açıklaması o yüzeye işaret eder

## Edge case

| Durum | Çözüm |
|-------|--------|
| API ile toplu description | Şimdilik yok — Studio manuel (credential gelince ayrı iş) |
| Thumbnail / montaj | Bu SOP kapsamı dışı |
| Transcript | YouTube auto-caption açık olsun; açıklama yine dolu kalsın |

## Studio checklist

Bkz. pack sonu: [`docs/youtube-geo-pack.md`](../docs/youtube-geo-pack.md#studio-uygulama-checklist-manuel-3040-dk)
