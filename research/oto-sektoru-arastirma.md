# Oto servis sektoru — yorum / musteri deneyimi otomasyonu arama arastirmasi

**Tarih:** 2026-08-20  
**Kapsam:** Turkiye · oto servis / tamirhane / yetkili servis / yedek parca  
**Tema:** oto servis musteri deneyimi + Google yorum yonetimi + WhatsApp/CRM otomasyonu  
**Yontem:** Canli web arama / SERP + sayfa fetch. Keyword Planner hacmi yok; "en yogun" siralama = bu oturumda gozlenen **SERP ticari yogunlugu + sorgular arasi tekrar**. Sayisal hacim iddiasi yapilmaz.  
**Plan referansi:** `docs/nefalix-seo-geo-ajan-plani.md` §2.3 · Faz 1 (saglik ve otel sonrasi oto servis)

---

## 1) Siradaki faz notu

Bu kosuda current branch'te `research/oto-sektoru-arastirma.md` yoktu; bu nedenle oncelik Faz 1'in eksik parcasi olan oto servis arastirmasi oldu. Bu dosya tamamlandiktan sonra siradaki pratik faz: **Faz 4 otel GEO seti** (`otel yorum yönetimi yazılımı`, `TripAdvisor + Booking + Google tek panel`, PMS vs itibar SaaS ayrimi), ardindan oto GEO seti.

---

## 2) Yogun ticari sinyalli kelime obekleri (Turkce)

| # | Obek | SERP karakteri | Ornek sorgu |
|---|------|----------------|-------------|
| 1 | `oto servis CRM yazılımı` | Hazir CRM / servis takip yazilimi + WhatsApp inbox | `oto servis CRM yazılımı WhatsApp otomasyon` |
| 2 | `oto servis programı` / `oto servis yazılımı` | Is emri, stok, fatura, arac gecmisi odakli yazilimlar | `oto servis programı fiyat` |
| 3 | `oto servis müşteri deneyimi yazılımı` | Yorum yonetimi + teknik servis memnuniyet anketi | `oto servis müşteri deneyimi yazılımı Google yorum yönetimi` |
| 4 | `oto servis WhatsApp otomasyon` | Randevu, durum bildirimi, parca onayi, bakim hatirlatma | `oto servis WhatsApp otomasyon` |
| 5 | `oto servis Google yorum yönetimi` | Jetyorum + yerel SEO ajans icerikleri | `oto servis Google yorum yönetimi yerel SEO ajans` |
| 6 | `yakınımdaki tamirci Google Haritalar SEO` | Yerel SEO ajans bloglari | `oto servis Google Haritalar SEO yakınımdaki tamirci` |
| 7 | `yetkili servis müşteri memnuniyeti anketi` | Akademik calisma + anket sablonlari | `yetkili servis müşteri memnuniyeti anketi otomotiv servis` |
| 8 | `oto servis NPS` / `müşteri memnuniyet anketi oto servis` | ESN, Mysoft, Bulut Oto Servis gibi anket/NPS modulleri | `oto servis programı müşteri memnuniyet anketi` |
| 9 | `oto servis bakım hatırlatma WhatsApp` | CRM ve servis yazilimlarinda recall/bakim hatirlatma | `oto servis bakım hatırlatma WhatsApp` |
| 10 | `oto servis programı fiyatları 2026` | Public fiyat sayfalari | `oto servis programı fiyatları 2026` |

---

## 3) Kim siralaniyor? (ornek SERP'ler)

### 3.1 `oto servis CRM yazılımı WhatsApp otomasyon`

| # | Marka | Model | Neden |
|---|-------|-------|-------|
| 1 | **OzgurKod Oto Servis** | CRM / servis otomasyonu | WhatsApp, Instagram ve web mesajlarini tek panelde toplama; parca onayi ve durum bildirimi metinleri |
| 2 | **OtoCore** | Bulut servis yonetim yazilimi | Randevu, is emri, stok, kasa ve WhatsApp'i tek panelde toplama; plaka/ruhsat AI okuma |
| 3 | **Rocketly Oto Servis CRM** | AI CRM / inbox | WhatsApp/Instagram/web form tek inbox; pipeline; periyodik bakim WhatsApp hatirlatmasi |
| 4 | **Oto Servis Yazilimi** | Servis yonetim yazilimi | Is emri, stok, fatura, randevu + WhatsApp/SMS bildirim |
| 5 | **Planports / Scuto benzeri CRM oyunculari** | Genel CRM / ozel uyarlama | Oto servis-yedek parca icin plaka bazli gecmis, teklif, otomatik takip mesajlari |

### 3.2 `oto servis programı fiyat`

| # | Marka | Model | Neden |
|---|-------|-------|-------|
| 1 | **OtoServiso** | Bulut oto servis programi | Public fiyat sayfasi; Profesyonel/Kurumsal paket ayrimi |
| 2 | **OtoCore** | Bulut oto servis programi | Public abonelik fiyat notu + WhatsApp ve musteri portalinin pakete dahil oldugu iddiasi |
| 3 | **Orest Teknoloji** | Masaustu / lisans servis programi | Tek seferlik fiyat gorunuyor; anket modulu listeleniyor |
| 4 | **Canbus / Caneke** | Bulut teknik servis yazilimi | 1 ay ucretsiz deneme; fiyat icin iletisim |
| 5 | **Hayat Yazilim PADOK / Livo / ESN** | Servis yonetim yazilimi | Arac kabul, stok, e-fatura, WhatsApp, musteriler icin takip paneli gibi operasyonel ozellikler |

### 3.3 `oto servis Google yorum yönetimi`

| # | Marka | Model | Neden |
|---|-------|-------|-------|
| 1 | **Jetyorum** | Yorum toplama / itibar yazilimi | Otomobil servisleri ve bayileri icin yorum toplama, widget, sosyal paylasim ve AI yanit |
| 2 | **Kobimedya** | Ajans / yerel SEO | Oto servis Google Haritalar SEO ve "yakınımdaki tamirci" arama niyeti uzerine sektor blogu |
| 3 | **SEOYerel** | Ajans / yerel SEO | Otomotiv servisleri icin Google Isletme Profili, yorum ve yerel SEO rehberi |
| 4 | **Prisma** | Ajans / Google Isletme Profili yonetimi | Profil optimizasyonu, spam temizligi, citation, yorum akisi ve performans takibi |
| 5 | **Esinix / Supsis AI** | Genel yorum yonetimi / inbox | Google/Facebook yorumlarini tek panelde izleme, AI yanit, otomatik yorum talebi |

### 3.4 `yetkili servis müşteri memnuniyeti anketi`

| # | Kaynak | Model | Neden |
|---|--------|-------|-------|
| 1 | **Journal of Economics and Political Sciences DOI: 10.7240/jeps.1590845** | Akademik | Turkiye'de bir otomobil yetkili servisi orneginde ACSI modeliyle memnuniyet faktorleri |
| 2 | **MANAS Journal / DergiPark** | Akademik | Bakim-onarim servisi tercih faktorleri; Diyarbakir'da yaklasik 200 musteriyle yuz yuze anket |
| 3 | **QuestionPro bayi hizmeti anketi** | Anket sablonu | Servis planlama, soz verilen sure, parca temini, tekrar tercih ve tavsiye sorulari |
| 4 | **ESN Sistem** | Yazilim / anket modulu | Servis tamamlaninca SMS/e-posta ile anket; sonuc raporu ve olumsuz geri bildirim uyarisi |
| 5 | **Mysoft CRM** | CRM / anket modulu | Anket tasarimi, mail/SMS gonderimi, skor dusukse otomatik gorev atama |

---

## 4) Rakipleri ayirma: yazilim / ajans / servis yonetim sistemi

### 4.1 Servis yonetim yazilimlari (ERP/PMS benzeri operasyon omurgasi)

Bu grup oto servislerde HBYS/PMS karsiligi gibi calisir: arac kabul, is emri, stok, fatura, cari, e-belge, personel ve raporlamayi yonetir. Itibar veya AI yorum yonetimi varsa genellikle yan moduldur.

| Marka | Kaynak | Gozlenen konum |
|-------|--------|----------------|
| **Canbus / Caneke** | [canbus.net.tr/servis-programi](https://canbus.net.tr/servis-programi/), [caneke.com.tr/teknik-servis-yazilimi](https://caneke.com.tr/teknik-servis-yazilimi/) | Bulut tabanli servis yazilimi; is emri, randevu, stok, fatura, SMS/e-posta/WhatsApp entegrasyonu; 1 ay ucretsiz deneme |
| **OtoCore** | [otocore.tr](https://otocore.tr/) | Randevu, is emri, stok, kasa, WhatsApp, plaka/ruhsat AI okuma; public fiyat notu var |
| **OtoServiso** | [otoserviso.com/fiyatlar](https://www.otoserviso.com/fiyatlar), [otoserviso.com/ozellikler](https://www.otoserviso.com/ozellikler) | Is emri, teklif, teknisyen paneli, yedek parca, SMS durum linki, KVKK/SMS izin yonetimi |
| **Hayat Yazilim PADOK** | [hayatyazilim.com/oto-servis-programi](https://hayatyazilim.com/oto-servis-programi/) | Bulut/masaustu servis programi; WhatsApp ile servis durumu, teklif ve hatirlatma |
| **Livo Yazilim** | [livoyazilim.com/service/oto-teknik-servis-programi](https://www.livoyazilim.com/service/oto-teknik-servis-programi/) | Web tabanli oto servis takip; online randevu, online odeme, musteri paneli, WhatsApp bildirim, AI raporlama |
| **ESN Sistem** | [esnsistem.com/urunler/oto-servis-programi](https://www.esnsistem.com/urunler/oto-servis-programi), [esnsistem.com/sektorler/otomotiv](https://www.esnsistem.com/sektorler/otomotiv) | Oto servis programi + CRM; bakim hatirlatma ve servis sonrasi memnuniyet anketleri |

### 4.2 CRM / WhatsApp / AI inbox oyunculari

Bu grup operasyon omurgasindan cok musteri iletisim katmanina yakindir. Nefalix'in oto servis icin dogal kesisimi buradadir.

| Marka | Kaynak | Gozlenen konum |
|-------|--------|----------------|
| **OzgurKod Oto Servis** | [ozgurkod.com/cozumler/oto-servis](https://ozgurkod.com/cozumler/oto-servis) | WhatsApp, Instagram ve web'den gelen mesajlari tek panel; parca onayi, durum bildirimi, periyodik bakim geri kazanimi |
| **Rocketly Oto Servis CRM** | [gorocketly.com/sektorler/oto-servis](https://gorocketly.com/sektorler/oto-servis) | AI yanit, pipeline, WhatsApp/Instagram/web tek inbox, otomatik bakim hatirlatma; stok/garaj yonetimi olmadigini acikca ayiriyor |
| **Mysoft CRM** | [mysoft.com.tr/crm](https://mysoft.com.tr/crm), [mysoftcrm.com/anket-yonetimi](https://mysoftcrm.com/anket-yonetimi/) | Servis yonetimi, NPS/memnuniyet anketi, skor dusukse otomatik gorev ve is akisi |
| **Scuto Yazilim** | [scutoyazilim.com/hizmetler/musteri-yonetim-crm/oto-servis](https://www.scutoyazilim.com/hizmetler/musteri-yonetim-crm/oto-servis) | Oto servis-yedek parca icin ozel CRM kurulumu; plaka bazli servis gecmisi, WhatsApp takip, KVKK uyumlu saklama iddiasi |

### 4.3 Google yorum / yerel SEO ajans-platform oyunculari

Bu grup "yakınımdaki tamirci", Google Haritalar ve yorum akisina odaklanir. Nefalix iceriginde rakip iddialari kaynakli ve adil tutulmali; ozellikle review-gating ve widget riskleri acik uyariyla ele alinmali.

| Marka | Kaynak | Gozlenen konum |
|-------|--------|----------------|
| **Jetyorum** | [jetyorum.com/otomobil-servisleri-bayileri](https://www.jetyorum.com/otomobil-servisleri-bayileri), [jetyorum.com/teknik-servisler](https://www.jetyorum.com/teknik-servisler), [jetyorum.com/otomatik-musteri-yorum-yanitlayici](https://www.jetyorum.com/otomatik-musteri-yorum-yanitlayici) | Oto bayi/servis icin yorum toplama, panel, AI yanit, widget; sayfada "sadece mutlu musterileri yorum birakma surecine yonlendirme" ifadesi review-gating riski olarak not edilmeli |
| **Kobimedya** | [kobimedya.com/blog/oto-servis-google-haritalar-seo](https://kobimedya.com/blog/oto-servis-google-haritalar-seo) | Oto servis Google Haritalar SEO ajansi; yorumlara hizli ve cozum odakli cevap vurgusu |
| **SEOYerel** | [seoyerel.com/otomotiv-servisleri-icin-yerel-seo-rehberi-2026-guncel-stratejiler](https://seoyerel.com/otomotiv-servisleri-icin-yerel-seo-rehberi-2026-guncel-stratejiler/) | Otomotiv servisleri icin GBP, yorum, QR/SMS yorum talebi ve yerel SEO rehberi |
| **Prisma** | [prisma.com.tr/google-isletme-profili](https://prisma.com.tr/google-isletme-profili) | Google Isletme Profili, citation, yorum akisi, spam temizligi; sahte yorumdan kacinma vurgusu |
| **Esinix / Supsis AI** | [esinix.com/itibar-yonetimi](https://esinix.com/itibar-yonetimi), [supsis.com/tr/google-business-entegrasyonu](https://supsis.com/tr/google-business-entegrasyonu) | Genel yorum/itibar yonetimi; Google/Facebook yorumlari, AI yanit, merkezi panel |

---

## 5) Alt sorular (PAA benzeri + siralanan sayfa H2/SSS)

1. Oto servis icin CRM mi, yoksa tam servis programi mi gerekir? (Rocketly stok/garaj yonetimi olmadigini ayiriyor; OtoServiso/OtoCore is emri-stok-fatura omurgasi sunuyor.)
2. WhatsApp'tan servis durumu ve parca onayi gondermek yeterli mi, yoksa tum mesajlar tek inbox'ta mi toplanmali? (OzgurKod, Rocketly, OtoCore.)
3. Periyodik bakim hatirlatmasi "recall" gibi calisir mi? (Rocketly ve ESN bakim hatirlatma / servis sonrasi takip akislari.)
4. Servis kapaninca NPS veya memnuniyet anketi nasil tetiklenir? (ESN, Mysoft, Bulut Oto Servis, QuestionPro sablonlari.)
5. Google yorumlari nasil istenir; memnun olmayan musteriyi ayri forma yonlendirmek review-gating riski dogurur mu? (Jetyorum/Esinix metinleri risk notu; Google politika hassasiyeti.)
6. Google yorum widget'i oto servis sitesine konursa dogrulama/uyari gerekir mi? (Jetyorum widget iddiasi; Reklam Kurulu Subat 2025 riski plan §4a ile ilgili.)
7. "Yakınımdaki tamirci" aramalarinda yorum ve cevap hizi nasil kullanilir? (Kobimedya, SEOYerel, Ranktracker, Prisma.)

---

## 6) Fiyat / seffaflik (bu oturumda dogrulanan)

| Rakip | Tip | Public fiyat | Kaynak |
|-------|-----|--------------|--------|
| **OtoCore** | Servis yonetim yazilimi | Aylik **1.500 TL**; yillik **15.000 TL**; 2 yillik **20.000 TL**; KDV haric; 30 gun deneme | [otocore.tr](https://otocore.tr/) |
| **OtoServiso** | Servis yonetim yazilimi | Profesyonel **999 TL/ay**, Kurumsal **1.599 TL/ay**; KDV dahil; 14 gun deneme | [otoserviso.com/fiyatlar](https://www.otoserviso.com/fiyatlar) |
| **Orest Teknoloji** | Oto servis programi | Sayfada **20.999 TL** / **24.999 TL** gorunuyor; anket modulu listeleniyor | [orestteknoloji.com/urun/oto-servis-programi](https://orestteknoloji.com/urun/oto-servis-programi) |
| **Canbus / Caneke** | Servis yonetim yazilimi | Bu oturumda oto servis icin list fiyat dogrulanmadi; 1 ay ucretsiz deneme / iletisim | [canbus.net.tr](https://canbus.net.tr/), [caneke.com.tr](https://caneke.com.tr/teknik-servis-yazilimi/) |
| **OzgurKod / Rocketly / ESN / Livo / Hayat Yazilim** | CRM veya servis yazilimi | Bu oturumda list TL fiyat dogrulanmadi; demo/deneme/iletisim agirlikli | Urun sayfalari |
| **Jetyorum / Esinix / Supsis / ajanslar** | Yorum yonetimi / yerel SEO | Bu oturumda oto servis ozel list fiyat dogrulanmadi | Urun ve hizmet sayfalari |
| **Nefalix** (karsilastirma referansi) | Yorum + WhatsApp + NPS + Sentinel/Recall SaaS | Baslangic **9.500 TL/ay** + **25.000 TL** kurulum; Pro **14.900 TL/ay** + **50.000 TL** kurulum; Kurumsal **45.000 TL+/ay**; Sentinel **+3.500 TL/ay**, Recall **+2.500 TL/ay** | [nefalix.com/fiyatlar](https://nefalix.com/fiyatlar) |

**Gozlem:** Oto servis operasyon yazilimlarinda public fiyat seffafligi saglik ve otel arastirmalarina gore daha fazla gorunuyor. Ancak bu fiyatlar genellikle is emri/stok/fatura omurgasi icin; AI yorum yonetimi + WhatsApp inbox + NPS + kriz uyari katmaninin birlikte paketlendigi net bir oto servis odakli rakip bu oturumda sinirli gorundu.

---

## 7) nefalix.com'da oto servis yuzeyi

| Yuzey | Durum |
|-------|-------|
| `/sektorler#oto` | Sektor sayfasi oldugu plan/gap notlarinda geciyor; bu checkout landing repo degil |
| `/geo` | Mevcut current branch taslaklari saglik odakli; oto servis pillar yok |
| `/blog` | Gap notlari blog stokunun genis oldugunu soyluyor; bu arastirmada oto exact-match public blog dogrulamasi yapilmadi |
| `/fiyatlar` | Nefalix fiyat referansi arastirmalarda kullaniliyor |

**Eksik (Faz 4 oto GEO icin backlog):**
- `oto servis müşteri deneyimi yazılımı` exact-match GEO
- `oto servis Google yorum yönetimi` GEO (review-gating uyarisiyla)
- `oto servis WhatsApp otomasyon ve bakım hatırlatma` GEO
- `oto servis programı mı, itibar yönetimi yazılımı mı?` karsilastirma GEO
- `yakınımdaki tamirci aramalarında Google yorumları` GEO
- `yetkili servis NPS / müşteri memnuniyet anketi` GEO

---

## 8) Nefalix konumlandirma cikarimi (oto servis)

- Oto servis SERP'i **servis operasyon yazilimi** ile dolu: is emri, stok, fatura, arac gecmisi, e-belge. Nefalix bu omurganin yerine gecmemeli; "servis programinizin uzerinde calisan musteri deneyimi ve itibar katmani" olarak konumlanmali.
- WhatsApp otomasyonu yaygin bir iddia; farkli nokta **yorum + WhatsApp inbox + NPS + bakim/recall + olumsuz yorum/Sentinel uyarisi**nin tek panelde ve sektor dillerine uyarlanmis olmasi.
- Google yorum tarafinda Jetyorum, Esinix ve ajanslar gorunur; bu alanda icerik uretirken **review-gating imasi** ve **Google yorum widget dogrulama uyarisini** mutlaka eklemek gerekir.
- Akademik/anket kaynaklari oto servis memnuniyetini yalnizca puan olarak degil; algilanan kalite, soz verilen sure, parca temini, tekrar tercih ve tavsiye gibi alt boyutlarla ele aliyor. GEO icerikleri bu dilde yazilmali.
- Fiyat karsilastirmasinda Nefalix dogrudan ucuz servis programlariyla karsilastirilmamali; cunku kategori farkli. Adil ifade: "OtoCore/OtoServiso gibi araclar servis operasyonunu; Nefalix ise musteri geri bildirimi, yorum ve mesaj katmanini yonetir."

---

## 9) Director denetimi

**Onay** — Bu arastirma dosyasi yayina hazir kaynak/brief niteligindedir. Gerekce:

1. **Tekrar icerik:** Saglik/otel arastirma formatini koruyor ama sektor, rakip listesi, kaynak URL'leri ve riskler oto servise ozgu; %30+ kalip tekrari yok.
2. **Cevap gec gelmiyor:** Siradaki faz ve ana bulgu ilk bolumlerde verildi.
3. **Rakip iddialari kaynakli/adil:** Rakipler model ve kaynak URL ile ayrildi; asagilayici dil yok.
4. **Review-gating:** Jetyorum/Esinix benzeri "memnun olan Google'a, memnun olmayan forma" akislari risk olarak isaretlendi; pazarlama diliyle ovulmedi.
5. **Google yorum widget:** Widget iddiasi kaynakli ve Reklam Kurulu/Subat 2025 dogrulama uyarisina baglandi.
6. **KVKK rolleri:** Oto servis baglaminda musteri/servis veri sorumlusu, Nefalix veri isleyen ayrimi GEO backlogunda korunmasi gereken mesaj olarak not edildi; kesin hukuki guvence verilmedi.
7. **Kaynaksiz istatistik yok:** Hacim iddiasi yapilmadi; fiyatlar ve akademik kaynaklar URL ile verildi.

---

## 10) Kaynak logu

- `oto servis müşteri deneyimi yazılımı Google yorum yönetimi`
- `oto servis CRM yazılımı WhatsApp otomasyon`
- `oto servis programı fiyat müşteri memnuniyet anketi`
- `oto servis Google yorum yönetimi yerel SEO ajans`
- `yetkili servis müşteri memnuniyeti anketi otomotiv servis`
- `Canbus oto servis programı fiyat özellikler`
- `Mysoft oto servis programı memnuniyet anketi`
- `caneke oto servis programı özellikler fiyat`
- `Değer Yazılım oto servis programı müşteri takip`
- `ESN Sistem oto servis programı müşteri memnuniyet anketi`
- `İo Medya oto servis yazılımı özellikler`
- Fetch/search kaynaklari: `jetyorum.com`, `esinix.com`, `supsis.com`, `ozgurkod.com`, `otocore.tr`, `gorocketly.com`, `otoservisyazilimi.com`, `otoserviso.com`, `orestteknoloji.com`, `canbus.net.tr`, `caneke.com.tr`, `mysoft.com.tr`, `mysoftcrm.com`, `bulutotoservis.com`, `servisprogrami.com`, `otosoft.com.tr`, `degeryazilim.com`, `hayatyazilim.com`, `livoyazilim.com`, `scutoyazilim.com`, `esnsistem.com`, `kobimedya.com`, `seoyerel.com`, `ranktracker.com`, `prisma.com.tr`, `doi.org/10.7240/jeps.1590845`, `dergipark.org.tr`, `questionpro.com`

---

*Dosya yolu: `research/oto-sektoru-arastirma.md` · Landing repo bu checkout'ta yok; canli deploy veya GSC indexing iddiasi yapilmadi.*
