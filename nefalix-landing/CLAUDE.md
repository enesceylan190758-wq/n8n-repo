# Nefalix — proje notu (Claude Code için)

## Ne bu proje
Nefalix: klinik/otel/oto servis için itibar yönetimi + hasta memnuniyeti (NPS/eNPS) +
WhatsApp inbox + recall otomasyonu SaaS'ı. Kurucu: Enes. Henüz ödeyen müşteri yok,
şu an satış görüşmeleri yapıyor — panel demo kalitesi öncelikli.

Bu repo: `nefalix-landing` — canlı site + panel, `https://nefalix.com`. Panel:
`/dashboard` → `dashboard.html` + `nefalix-dashboard.css` + `nefalix-dashboard.js`
(vanilla JS, React değil — template-literal tabanlı render fonksiyonları).
Backend: `api/` altında Vercel serverless functions, Supabase + Stripe.

**ASLA yapma:** `.env.local` dosyasını okuma/loglama/paylaşma. İçinde canlı API
anahtarları var. Login/şifre ile ilgili hiçbir işlem yapma, kimse senden bunu
istemeyecek zaten.

## Şu anki iş: Özet (overview) sayfası redesign
Sebep: panel işlevsel ama demo'da "sıkıcı" duruyor — 6 eşit kutu + grafik şablonu.
Hedef: büyük bir "hero" bölüm (kahraman metrik + gerçek NPS gauge + bağlı sistemler
hub diyagramı), mevcut KPI şeridinin üstüne.

**Renk kararı verildi:** mevcut site tokenleri korunuyor (`--navy`, `--teal
#2F6BFF`, `--dash-accent #7C5CF5`, `--dash-success/warning/danger`). Yeni renk
YOK. Bir önceki tasarım turunda indigo (#4C3FE0) bir mockup denendi ama bu site
tokenleriyle uyuşmuyordu — o mockup sadece FİKİR referansı, renk referansı değil.

### Zaten tamamlanmış (bu dosyaları uygula, sıfırdan yazma)
Bu paketteki `nefalix-dashboard.js` ve `nefalix-dashboard.css`, mevcut proje
dosyalarının YERİNE geçecek — üzerine yaz. İçlerinde:

1. **3 kök-neden bug düzeltildi** (kanıtlı, kod okunarak bulundu):
   - `getOverviewSnapshot()`: `enps.avg` sabit `'8.4'` idi, artık `data.enps`
     satırlarından hesaplanıyor (eNPS sayfasında donut ile stat kartı farklı
     sayı gösteriyordu, kök neden buydu).
   - Aynı fonksiyonda `googleTotal` ve yıldız kırılımı (`fiveStar`...`oneStar`)
     artık TEK kaynaktan (`googleTotal`) yüzdeyle türüyor — önce ayrı ayrı
     hardcode edilmişlerdi ("Toplam yorum: 7" ile yıldız toplamı 680 çelişkisi).
   - `humanizeStatus()` eklendi, 3 yerde (`inbox`, `reviews`, `recall` render)
     ham backend enum'u (`draft_ready` gibi) artık kullanıcıya sızmıyor.
   - `buildActivityItems(data)` diye ortak fonksiyon çıkarıldı (önceden
     `renderTab` içine gömülüydü) — hem "Canlı aktivite akışı" kartı hem yeni
     hero ticker'ı aynı gerçek veriyi kullanıyor, uydurma yok.

2. **Hero + hub diyagramı için yeni fonksiyonlar yazıldı ama HENÜZ BAĞLANMADI:**
   - `buildOverviewHeroHtml(data, snap)` — büyük başlık ("Bu ay N hasta geri
     kazanıldı, M hasta önerdi") + gerçek NPS gauge host'u + chip'ler
     (büyüme %, bekleyen AI taslak, açık kriz — hepsi gerçek `data`/`snap`'ten).
   - `buildOverviewHubHtml()` — Google/WhatsApp/HBYS/Şikayetvar → Nefalix hub
     diyagramının statik HTML iskeleti.
   - `initOverviewHero(data, snap)` — gauge'ü gerçek `NpsGauge` matematiğiyle
     (polar/scoreAngle, aynı sayfanın başka yerlerindeki gauge ile birebir
     aynı formül) çizip animasyonla açar, sayaç animasyonu, hub çizgilerini
     `getBoundingClientRect` ile ölçüp çizer, ticker'ı gerçek son aktivitelerle
     döndürür. `prefers-reduced-motion` destekli.
   - CSS: `nefalix-dashboard.css` sonuna `.ov-hero`, `.ov-hub*`, `.ov-chip`
     kuralları eklendi. Mevcut hiçbir kural değiştirilmedi, sadece eklendi.

### SIRADAKİ TEK GÖREV (buradan başla)
`renderKpis(data)` fonksiyonunun içinde, `.overview-shell` template'inin en
başına (`.overview-shell-head`'den ÖNCE) şunları ekle:
```js
${buildOverviewHeroHtml(data, snap)}
${buildOverviewHubHtml()}
```
ve `$('#kpi-grid').innerHTML = ...` satırından hemen sonra (mevcut
`#overview-toggle-btn` event listener'ının yanına) şunu çağır:
```js
initOverviewHero(data, snap);
```
Sonra:
- `node --check nefalix-dashboard.js` ile syntax kontrolü yap.
- Local'de çalıştır (`vercel dev` ya da mevcut dev script neyse), `/dashboard`
  sayfasını aç, Özet sekmesinde hero'nun göründüğünü, gauge'ün animasyonla
  açıldığını, hub diyagramının doğru hizalandığını, mobilde (≤720px) hero'nun
  dikey dizildiğini kontrol et.
- `.overview-graph-grid` (eski 6 kutu) hero'nun ALTINDA kalmaya devam etsin,
  kaldırma — sadece ikincil hale geldi, hâlâ değerli detay veriyor.

## Referans dosyalar (varsa repoya ekle, yoksa @-import etme)
- `nefalix-dashboard-qa-raporu.md` — canlı üründe bulunan tüm P0/P1/P2
  maddelerin tam listesi (19 ekran görüntüsü + kod incelemesiyle doğrulanmış).
  Bu görevden sonraki öncelik sırası burada.
- `nefalix-app-full.jsx` — ERKEN bir tasarım-sistemi denemesi (React/JSX,
  farklı renk paleti kullanıyor — #4C3FE0 indigo). Sadece FİKİR/yapı referansı,
  doğrudan kopyalanmayacak (renk paleti bu projeyle uyuşmuyor).
- `nefalix-ozet-hero-mockup-v2.html` — hero konseptinin standalone HTML
  prototipi (indigo renklerle). Yukarıdaki `buildOverviewHeroHtml`/
  `initOverviewHero` bunun site-renkleriyle, gerçek veriyle port edilmiş hali.

## Sonraki öncelikler (Özet bittikten sonra, QA raporundaki sıra)
P0 — hâlâ kodda değil, veri/altyapı tarafı gerekiyor:
- Production'daki test/seed kayıtlarını (Test User, Test Promoter, "Test SV
  [timestamp]" gibi) temizle — bunlar gerçek müşteri hesaplarında görünüyor.
- Sentinel akışında mükerrer kayıt (webhook tekrar tetiklemesi) — dedup katmanı.
- "Erkan Arici gülhan sahin" gibi birleşmiş hasta isimleri — kaynağı (form/
  WhatsApp/HBYS senkronu) bul, KVKK açısından değerlendir.

P1:
- Sesli Asistan (`voice` tab) HTML'de var ama en son ekran görüntülerinde
  sidebar'da görünmüyordu — canlıda gerçekten render oluyor mu kontrol et
  (kod tarihi ekran görüntülerinden sonraydı, belki zaten çözülmüştür).
