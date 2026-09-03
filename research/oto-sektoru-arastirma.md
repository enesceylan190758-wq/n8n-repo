# Oto servis sektörü — yorum / müşteri deneyimi otomasyonu arama araştırması

**Tarih:** 2026-09-03
**Kapsam:** Türkiye · bağımsız oto servisler, tamirhaneler, yetkili servis / bayi servis ağları
**Tema:** oto servis müşteri deneyimi + WhatsApp/inbox + Google yorum / itibar yönetimi
**Yöntem:** Canlı web arama / SERP + kaynak sayfa fetch. Keyword Planner, Ahrefs veya hacim API'si yok; "en yoğun" sıralama **sayısal hacim iddiası değil**, bu oturumda gözlenen **SERP ticari yoğunluğu + sorgular arası tekrar** ölçüsüdür. Rakip fiyatı veya özellik iddiası yalnızca kaynak sayfada görüldüyse yazıldı.
**Plan referansı:** `docs/nefalix-seo-geo-ajan-plani.md` §2.3 · `docs/nefalix-seo-geo-gap-notes.md` Faz 1 eksik halka

---

## 1) Bu koşuda sıradaki faz

Gap notes'a göre Faz 0 teknik indeks görünürlüğü tamamlanmış, Faz 1'de sağlık ve otel araştırmaları yazılmıştı. Bu checkout'ta eksik ana teslimat **oto servis sektörü araştırması** olduğu için bu koşuda Faz 1'in üçüncü sektör araştırması tamamlandı.

Bu dosyadan sonra sıradaki pratik faz: **Faz 4 — otel GEO seti** (`otel yorum yönetimi yazılımı`, `TripAdvisor + Booking + Google tek panel`, `PMS vs itibar SaaS`, `misafir NPS + WhatsApp`), ardından oto GEO seti.

---

## 2) Yoğun ticari sinyalli kelime öbekleri (Türkçe)

Sıra = bu araştırmada gözlenen SERP yoğunluğu / çapraz tekrar (yüksek -> düşük).

| # | Öbek | SERP karakteri | Örnek kaynak / gözlem |
|---|------|----------------|------------------------|
| 1 | `oto servis yazılımı` / `oto servis yönetim yazılımı` | Garaj/servis yönetimi yazılımları baskın: iş emri, stok, kasa, randevu | OtoCore, Mekaniq, ServisDefteri, Bulut Oto Servis |
| 2 | `oto servis CRM yazılımı` | CRM/inbox oyuncuları ve servis programları karışık | Rapitek, Rocketly, ÖzgürKod, Planports |
| 3 | `oto servis WhatsApp otomasyon` | WhatsApp bildirim, randevu, bakım hatırlatma ve "aracım hazır mı?" trafiği | OtoCore, Rocketly, ÖzgürKod, Mekaniq |
| 4 | `oto servis müşteri takip programı` | Müşteri + araç kartı, bakım geçmişi, teklif/onay akışı | ServisDefteri, ÖzgürKod, OtoCore |
| 5 | `oto servis Google yorum yönetimi` | Otoya özel sayfa az; genel yorum/itibar SaaS ve Jetyorum otomotiv sayfası öne çıkıyor | Jetyorum, Esinix, Restarun, ADWEBX |
| 6 | `yetkili servis müşteri memnuniyet anketi` | Teknik servis / saha servis platformları ve NPS araçları | UISAP ui.ServiceGrid, SerPro, ESN/ServisProgrami, Palmate AI |
| 7 | `oto servis randevu programı` | Randevu + iş emri + hatırlatma odaklı servis programları | Piyzi, OtoCore, Mekaniq |
| 8 | `araç bakım hatırlatma yazılımı` | Periyodik bakım geri çağırma / recall benzeri niyet | Planports, Rocketly, OtoCore, ServisDefteri |
| 9 | `oto bayi müşteri yorumları` | Bayi/servis gelirini yorumla büyütme iddiası; widget ve yönlendirme riski var | Jetyorum otomobil servisleri/bayileri |
| 10 | `Google yorum satın alma oto servis` / `sahte yorum` | Politika ve itibar riski araması; satın alma içerikleri de SERP'te görünüyor | Google destek, ADWEBX etik yöntemler, forum şikayetleri |

**Nefalix görünürlüğü:** Bu oturumda oto servis temalı ticari SERP'lerde nefalix.com görünürlüğü doğrulanmadı; Nefalix'in `/fiyatlar` sayfasında sektör seçimi içinde "Auto Servis" var, ancak dedicated oto GEO/pillar dosyası bu repoda yoktu.

---

## 3) Rakip haritası: yazılım / ajans / DMS-servis yönetimi ayrımı

### 3.1 Oto servis / garaj yönetim yazılımları

Bu katman iş emri, stok, kasa, fatura, randevu ve araç geçmişini yönetir. Nefalix ile doğrudan aynı kategori değildir; Nefalix bu yazılımların yerine geçmekten çok, yorum + geri bildirim + inbox + kriz alarmı katmanı olarak konumlanmalıdır.

| Marka / site | Model | Kaynaklı gözlem |
|---------------|-------|-----------------|
| **OtoCore** — `otocore.tr` | Oto servis yönetim yazılımı | Randevu, iş emri, stok, cari, WhatsApp, plaka/ruhsat okuma ve müşteri portalını tek pakette anlatıyor; aylık **1.500 TL**, yıllık **15.000 TL**, 2 yıllık **20.000 TL** (KDV hariç) yazıyor. |
| **Mekaniq** — `mekaniq.com.tr` | Oto servis / garaj programı | İş emri, müşteri/araç, stok, fatura ve WhatsApp bildirimleri; ücretsiz plan, Başlangıç **999 TL/ay**, Kurumsal **3.999 TL/ay**; WhatsApp eklentisi **99 TL/ay** veya Kurumsal pakette dahil. |
| **ServisDefteri** — `servisdefteri.tr` | Oto servis takip yazılımı | İş emri, fatura, stok, kasa, randevu, WhatsApp bildirimi ve AI arıza analizi; 30 gün deneme; aylık plan indirimli **413 TL**, yıllık **4.500 TL/yıl + KDV** olarak görünüyor. |
| **Bulut Oto Servis** — `bulutotoservis.com` | Oto servis programı | İş emri, stok, e-fatura/e-arşiv, WhatsApp belge paylaşımı ve otomatik mesaj anlatıyor; fiyat sayfasında paket verisi JS ile "yükleniyor" kaldığı için rakam doğrulanmadı. |
| **Canbus** — `canbus.net.tr/yetkili-servis-yazilimi` | Yetkili servis / bayi servis otomasyonu | Çok şubeli yetkili servis süreçleri, araç kabulden teslime SMS/e-posta bildirimleri ve periyodik bakım hatırlatma anlatıyor; public fiyat doğrulanmadı. |

### 3.2 CRM / birleşik inbox / WhatsApp katmanı

Bu katman servis talebi, teklif onayı, WhatsApp yazışması, satış sonrası takip ve bakım hatırlatma süreçlerini müşteri iletişimi tarafında toplar.

| Marka / site | Model | Kaynaklı gözlem |
|---------------|-------|-----------------|
| **Rocketly** — `gorocketly.com/sektorler/oto-servis` | CRM + birleşik inbox | WhatsApp, Instagram, web formu, telefon notu ve servis süreci pipeline'ı; AI'nin arıza teşhisi/fiyat taahhüdü vermediğini açıkça belirtiyor. Fiyat sayfası kesitinde Free, Starter **$25/ay**, Professional **$66/ay**, Business **$166/ay** yıllık faturalandırma rakamları göründü. |
| **Rapitek** — `rapitek.com/oto-servis-crm` | CRM / müşteri yönetim sistemi | WhatsApp Business API, SMS/e-posta, satış pipeline ve ERP entegrasyonlarını anlatıyor; SERP kesitinde **$25/kullanıcı/ay** başlangıç ve 2-4 hafta canlıya alma iddiası göründü. Fetch zaman aşımına uğradı; rakam SERP kesitiyle sınırlı not edilmelidir. |
| **ÖzgürKod** — `ozgurkod.com/cozumler/oto-servis` | Oto servis CRM / WhatsApp'lı yönetim | WhatsApp, Instagram ve web'den gelen mesajları tek panel, teklif/sipariş/tahsilat ve pipeline ile anlatıyor; 7 gün ücretsiz deneme var, public fiyat bu oturumda doğrulanmadı. |
| **Planports** — `planports.com/tr/otomotiv-firmalari-icin-crm-programi.html` | Otomotiv CRM / bayi ve servis takibi | Bayi, satış hunisi, servis hatırlatma, WhatsApp & Instagram DM; DMS'nin stok/servis operasyonu, CRM'in lead/pipeline/pazarlama katmanı olduğunu açıkça ayırıyor. Public fiyat bu sayfada doğrulanmadı. |

### 3.3 Yorum / itibar yönetimi SaaS katmanı

Bu katman Nefalix'e en yakın "Google yorum + AI yanıt + olumsuz yorum uyarısı" dilini kullanır; fakat bazı rakip anlatımlarında review-gating ve widget riski açıkça vardır.

| Marka / site | Model | Kaynaklı gözlem |
|---------------|-------|-----------------|
| **Jetyorum** — `jetyorum.com/otomobil-servisleri-bayileri` | Yorum toplama / itibar SaaS | Oto bayileri/servisleri için yorum, geri bildirim, sosyal paylaşım, widget (iFrame/API), NLP içgörü ve CRM/ERP entegrasyonu anlatıyor. Sayfada "sadece mutlu müşterileri yorum bırakma sürecine yönlendirin" ifadesi var; bu Nefalix içeriklerinde **uyum riski** olarak ele alınmalı, örnek alınmamalı. |
| **Esinix** — `esinix.com/itibar-yonetimi` | Genel Google/Facebook itibar SaaS | Otomatik yorum talebi, AI yanıt, olumsuz yorum uyarısı ve "memnun -> Google, memnun değil -> özel form" yönlendirmesi anlatıyor; bu da review-gating riski taşır. Ayrıca `%93`, `%57`, `%5-9` gibi istatistikler kaynaklandırılmadan sayfada yer alıyor; Nefalix içeriklerinde kullanılmamalı. |
| **Restarun** — `restarun.com` | Google yorum yönetimi / AI yanıt | Google yorumlarını takip, AI yanıt önerisi, rapor ve rakip karşılaştırması anlatıyor; otoya özel değil. Public fiyat bu oturumda doğrulanmadı. |
| **ADWEBX AI Google Yorum Yönetimi** — `adwebx.com.tr/tr/ai-google-yorum-yonetimi` | Ajans / otomasyon hizmeti | GBP API + AI + n8n ile yanıt taslağı ve onay adımı anlatıyor; insan onayı vurgusu Nefalix'in güvenli içerik diliyle uyumlu. |

### 3.4 Teknik servis / NPS / saha servis katmanı

Bu katman oto servise komşu bir arama niyeti üretir: servis kapanışı sonrası anket, NPS, düşük puan alarmı ve saha servis performansı.

| Marka / site | Model | Kaynaklı gözlem |
|---------------|-------|-----------------|
| **UISAP ui.ServiceGrid** — `uisap.com.tr` | SAP entegre servis yönetimi | SAP CS/BTP/ECC/S4HANA entegrasyonu, servis işlemi sonrası NPS, bölge/il bazlı NPS analizi anlatıyor. |
| **SerPro** — `serpro.com.tr` | Teknik servis yönetim SaaS | SMS/WhatsApp/e-posta otomasyon, takip linki, memnuniyet anketi ve yıldız puanlama anlatıyor; otoya değil genel teknik servise konumlu. |
| **ESN / ServisProgrami** — `servisprogrami.com/blog/musteri-memnuniyet-anketi` | Servis programı + anket içerik | Servis kapanışı sonrası SMS/e-posta anket, olumsuz değerlendirmede otomatik uyarı, çalışan/servis türü analizi anlatıyor. |
| **Palmate AI** — `palmate.ai/tr/cozumler/nps-geri-bildirim-ai` | NPS / geri bildirim chatbot'u | WhatsApp veya web üzerinden NPS ve geri bildirim toplama; dikey oto değil, yatay CX/NPS aracı. |

### 3.5 Ajans / danışmanlık katmanı

Oto servis SERP'inde sağlık sektöründeki kadar güçlü "itibar ajansı" yoğunluğu görülmedi. Ajans tarafı daha çok genel GBP/yerel SEO, Google yorum artırma rehberi veya AI yorum yanıt otomasyonu şeklinde çıkıyor. Bu nedenle oto içeriklerinde rakipleri "ajans kötü, yazılım iyi" diye değil, **iş modeli ayrımı** ile anlatmak gerekir.

---

## 4) Alt sorular (PAA benzeri + forum / şikayet temaları)

People Also Ask kutusu araç çıktısında ayrı parse edilmedi. Aşağıdaki sorular SERP'te sıralanan sayfa H2/SSS'leri ve Ekşi Sözlük gibi forum/şikayet başlıklarından derlendi.

1. Oto servis yazılımı yalnızca iş emri mi tutar, yoksa WhatsApp ve randevu akışını da yönetir mi? — OtoCore, Mekaniq, ServisDefteri SSS/özellik blokları.
2. DMS/servis programı ile CRM/inbox aynı şey midir? — Planports, DMS'nin stok/servis operasyonu; CRM'in lead, satış pipeline ve pazarlama katmanı olduğunu ayırıyor.
3. Servis sonrası memnuniyet anketi ne zaman gönderilmeli ve düşük puan gelirse kim uyarılmalı? — UISAP, ESN/ServisProgrami, SerPro.
4. Periyodik bakım zamanı gelen müşteriye WhatsApp hatırlatması nasıl kurulur? — OtoCore, Rocketly, Planports, ServisDefteri.
5. Google yorum talebi herkese mi gönderilmeli, yoksa yalnızca memnun müşteriye mi? — Google destek sayfası yorum linki/QR paylaşımına izin verir; yorum karşılığı teşvik yasaktır. Jetyorum/Esinix gibi sayfalardaki seçici yönlendirme dili Nefalix için riskli örnektir.
6. "Aracım ne durumda?" aramalarını azaltmak için müşteri takip linki veya teslim bildirimi nasıl çalışır? — OtoCore, ServisDefteri, Rocketly.
7. AI oto serviste arıza teşhisi koyabilir mi? — Rocketly güvenli sınır koyuyor: AI taslak/özet üretir, teşhis/fiyat/süre taahhüdü vermez. ServisDefteri ise AI arıza analizi vaadi kullanır; bu iddia kendi ürün sayfasına aittir, Nefalix'e taşınmamalı.
8. Forum/şikayet temaları: yanlış parça, servis sonrası aynı arızanın sürmesi, ikame araç/geri dönüş eksikliği, merkez-yetkili servis iletişim kopukluğu. Örnek Ekşi başlıkları: `dogu-bati-honda--7879391`, `antalya-mercedes-yetkili-servis-rezaleti--8010377`, `citroen-cam-magduriyeti--8111709`, `kasim-2022-borusan-otomotiv-ve-bmw-rezaleti--7468821`.

---

## 5) Fiyat / özellik şeffaflığı (bu oturumda doğrulanan)

| Rakip | Tip | Public fiyat / şeffaflık | Kaynak |
|-------|-----|--------------------------|--------|
| **OtoCore** | Oto servis yönetim yazılımı | **1.500 TL/ay**, **15.000 TL/yıl**, **20.000 TL/2 yıl**, KDV hariç; 30 gün deneme | `https://otocore.tr/` |
| **Mekaniq** | Oto servis / garaj programı | Ücretsiz plan; Başlangıç **999 TL/ay**; Kurumsal **3.999 TL/ay**; WhatsApp eklentisi **99 TL/ay** veya Kurumsal'da dahil | `https://mekaniq.com.tr/` |
| **ServisDefteri** | Oto servis takip yazılımı | 30 gün deneme; aylık plan indirimli **413 TL**; yıllık **4.500 TL/yıl + KDV**; fiyatlara KDV dahil değil | `https://servisdefteri.tr/` |
| **Rocketly** | CRM + inbox | Free; Starter **$25/ay**, Professional **$66/ay**, Business **$166/ay** yıllık faturalandırma kesiti görüldü | `https://gorocketly.com/sektorler/oto-servis` |
| **Rapitek** | CRM / müşteri yönetim sistemi | SERP kesitinde **$25/kullanıcı/ay** başlangıç; kaynak fetch zaman aşımı nedeniyle rakam "SERP snippet" olarak notlanmalı | `https://rapitek.com/oto-servis-crm/` |
| **ÖzgürKod** | Oto servis CRM | 7 gün ücretsiz deneme; public aylık fiyat bu oturumda doğrulanmadı | `https://ozgurkod.com/cozumler/oto-servis` |
| **Planports Otomotiv CRM** | Otomotiv CRM | Ücretsiz kurulum / demo; bu sayfada public aylık fiyat doğrulanmadı | `https://www.planports.com/tr/otomotiv-firmalari-icin-crm-programi.html` |
| **Jetyorum** | Yorum/itibar SaaS | Oto bayi/servis sayfasında public fiyat doğrulanmadı; widget ve seçici yönlendirme dili var | `https://www.jetyorum.com/otomobil-servisleri-bayileri` |
| **Esinix** | Genel itibar SaaS | Public fiyat doğrulanmadı; review-gating olarak okunabilecek akış anlatıyor | `https://esinix.com/itibar-yonetimi` |
| **Nefalix** | Yorum + NPS + inbox + kriz/recall SaaS | Başlangıç **9.500 TL/ay** + **25.000 TL** kurulum; Pro **14.900 TL/ay** + **50.000 TL** kurulum; Kurumsal **45.000 TL+/ay**; Sentinel **+3.500 TL/ay**, Recall **+2.500 TL/ay** | `https://nefalix.com/fiyatlar` |

**Fiyat yorumu:** Oto servis operasyon yazılımları Nefalix'ten belirgin biçimde daha düşük aylık fiyatla listeleniyor; bu doğrudan "daha ucuz/pahalı" karşılaştırması değildir çünkü kategori farklıdır. Nefalix oto içeriklerinde iş emri/stok/fatura programı olmadığını, yorum + NPS + WhatsApp/inbox + kriz alarmı katmanı olduğunu net söylemelidir.

---

## 6) Google yorum politikası / uyum notları

- Google'ın işletmelere yorum bağlantısı veya QR kodu paylaşma dokümanı, müşterilerin yorum bırakmasını kolaylaştırmaya izin verir; aynı dokümanda yorum karşılığında ücretsiz/indirimli ürün veya hizmet gibi teşviklerin sahte etkileşim sayıldığı ve yasak olduğu belirtilir: `https://support.google.com/business/answer/16816815?hl=tr`
- Jetyorum otomobil sayfasında "sadece mutlu müşterileri yorum bırakma sürecine yönlendirin" ve Esinix sayfasında "memnun -> Google, memnun değil -> özel form" benzeri ifadeler yer alıyor. Bu dil Nefalix içeriklerinde **öneri** gibi kullanılmamalı; yalnızca sektör riski olarak anlatılmalı.
- Google yorum widget'ı veya yorumların müşteri sitesinde yeniden yayınlanması anlatılacaksa doğrulama, güncellik ve kaynak uyarısı şarttır. Jetyorum iFrame/API widget anlatıyor; Nefalix oto GEO içerikleri bu özelliği anlatırsa Reklam Kurulu/yanıltıcı yorum vitrini riskini açıkça sınırlamalıdır.
- KVKK rol ayrımı: oto servis / bayi veri sorumlusudur; Nefalix veya benzeri SaaS sağlayıcısı veri işleyen rolünde konumlanır. Araç plakası, telefon, servis geçmişi ve yazışmalar kişisel veri içerebilir; "tam uyum garanti" gibi kesin pazarlama cümlesi kullanılmamalıdır.

---

## 7) nefalix.com'da oto yüzeyi: var / eksik

| Yüzey | Durum |
|-------|-------|
| `/fiyatlar` | Sektör seçimi içinde **Auto Servis** var; fiyat hesaplayıcı sağlık/otel/auto ayrımını destekliyor. |
| `/sektorler#oto` | Plan ve sitemap bağlamında oto sektör sayfası bekleniyor; bu koşuda landing repo yok, canlı sayfa editlenmedi. |
| `/geo` | Bu repodaki `geo/*.md` sağlık odaklı; oto servis GEO pillar yok. |
| `/blog` | Bu koşuda landing API taraması yapılmadı; oto özel blog stokunu iddia etmiyorum. |
| `research/` | Sağlık ve otel dosyaları vardı; oto dosyası bu koşuda eklendi. |

**Eksik / backlog (oto GEO seti):**

1. `oto servis müşteri deneyimi yazılımı nedir?`
2. `oto servis Google yorum yönetimi nasıl yapılır?`
3. `oto servis WhatsApp otomasyonu ve bakım hatırlatma`
4. `DMS / servis programı ile itibar yönetimi yazılımı farkı`
5. `yetkili servis müşteri memnuniyet anketi ve NPS`
6. `Nefalix vs oto servis programı: hangi katman hangi işi yapar?` (adil, kategori farkını vurgulayan karşılaştırma)

---

## 8) Nefalix konumlandırma çıkarımı (oto)

Oto servis SERP'i "boş" değil; fakat rakiplerin çoğu iş emri/stok/fatura/randevu veya genel CRM-inbox alanında yoğunlaşıyor. Nefalix'in savunulabilir içerik açısı **servis yönetim yazılımı yerine geçmek** değil, mevcut servis programı veya CRM'in yanına **yorum + NPS + WhatsApp geri bildirim + düşük puan/şikayet alarmı** katmanını koymaktır.

En güvenli GEO mesajı:

> Oto servis müşteri deneyimi yazılımı, araç teslimi sonrası geri bildirimi, Google yorum yanıt disiplinini, WhatsApp takiplerini ve düşük puan alarmını aynı operasyon ritmine bağlar; iş emri, stok ve fatura programının yerine geçmez.

Bu cevap, Rocketly/Planports'un kategori ayrımı diliyle uyumlu, Jetyorum/Esinix'teki review-gating riskinden uzak ve Nefalix'in fiyat/ürün katmanını yanlış konumlandırmayan bir çerçevedir.

---

## 9) Director denetimi

**Onay — araştırma dosyası.** Gerekçe: Dosya answer-first faz seçimiyle açılıyor; rakip iddiaları kaynak URL'lerle sınırlı; fiyatlar yalnızca doğrulandığı yerde yazıldı; review-gating ve widget ifadeleri pazarlama vaadi olarak değil risk olarak işaretlendi; KVKK rol ayrımı "oto servis/bayi = veri sorumlusu, Nefalix/SaaS = veri işleyen" şeklinde net.

**Red gerektirmeyen ama dikkat isteyen alanlar:**

- Rapitek fiyatı doğrudan WebFetch ile doğrulanamadı; SERP snippet kaydı olarak işaretlendi. Oto GEO karşılaştırmasına taşınacaksa yeniden fetch veya alternatif kaynak gerekir.
- Mekaniq/ServisDefteri/OtoCore fiyatları hızlı değişebilir; yayınlanacak karşılaştırma sayfasında tarih ve "public fiyat" notu kalmalı.
- Jetyorum/Esinix review-gating ifadeleri rakip eleştirisi tonunda değil, politika riski olarak kullanılmalı.

---

## 10) Kaynak logu

Kullanılan aramalar:

- `oto servis müşteri deneyimi yazılımı Türkiye oto servis CRM Google yorum yönetimi`
- `oto servis CRM yazılımı fiyat iş emri stok randevu WhatsApp`
- `oto servis Google yorum yönetimi yazılımı`
- `yetkili servis müşteri memnuniyet anketi otomasyon yazılımı NPS`
- `oto servis WhatsApp otomasyon müşteri takip yazılımı`
- `site:eksisozluk.com oto servis Google yorum müşteri memnuniyeti servis şikayet`
- `Google yorum politikası işletmeler yorum karşılığı ödül teşvik review gating`

Fetch / kaynak sayfalar:

- `https://otocore.tr/`
- `https://mekaniq.com.tr/`
- `https://servisdefteri.tr/`
- `https://gorocketly.com/sektorler/oto-servis`
- `https://ozgurkod.com/cozumler/oto-servis`
- `https://www.planports.com/tr/otomotiv-firmalari-icin-crm-programi.html`
- `https://www.jetyorum.com/otomobil-servisleri-bayileri`
- `https://esinix.com/itibar-yonetimi`
- `https://nefalix.com/fiyatlar`
- `https://support.google.com/business/answer/16816815?hl=tr`
- `https://eksisozluk.com/dogu-bati-honda--7879391`
- `https://eksisozluk.com/antalya-mercedes-yetkili-servis-rezaleti--8010377`
- `https://eksisozluk.com/citroen-cam-magduriyeti--8111709`
- `https://eksisozluk.com/kasim-2022-borusan-otomotiv-ve-bmw-rezaleti--7468821`

---

*Dosya yolu: `research/oto-sektoru-arastirma.md`. Landing repo bu checkout'ta yok; canlı deploy veya smoke iddiası yoktur.*
