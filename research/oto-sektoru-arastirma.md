# Oto servis sektoru — yorum / musteri deneyimi otomasyonu arama arastirmasi

**Tarih:** 2026-08-21
**Kapsam:** Turkiye · ozel oto servis, yetkili servis, tamirhane, lastikci, kaporta / boya, oto elektrik
**Tema:** oto servis yorum yonetimi + musteri deneyimi + servis operasyon otomasyonu
**Yontem:** Canli web arama / SERP sonuclari + sayfa fetch. Keyword Planner / Ahrefs hacim API'si yok; "en yogun" siralama **sayisal hacim degil**, bu oturumda gozlenen **SERP ticari yogunlugu + sorgular arasi tekrar** sinyalidir. Rakip fiyat/ozellik iddialari yalnizca public sayfa veya SERP ciktisi kaynak gosterdiginde yazildi.
**Plan referansi:** `docs/nefalix-seo-geo-ajan-plani.md` §2.3 · Gap notes Faz 1'de siradaki eksik teslimat.

**Kaynak notu:** Web arama arac ciktisi Google TR SERP'inin anlik bir kesitidir; konum, kisisellestirme ve tarih farki olabilir. People Also Ask kutusu arac ciktisinda ayri parse edilmedi; alt sorular SERP'te siralanan sayfa H2/SSS tekrarlarindan ve otomotiv servis memnuniyeti kaynaklarindan derlendi.

---

## 1) Yogun ticari sinyalli kelime obekleri (Turkce)

Sira = bu arastirmada gozlenen ticari sayfa yogunlugu / capraz tekrar (yuksek -> dusuk). Hacim iddiasi degildir.

| # | Obek | SERP karakteri (gozlem) | Ornek sorgu |
|---|------|--------------------------|-------------|
| 1 | `oto servis programi` / `oto servis yonetim yazilimi` | Yerli SaaS / bulut program sayfalari; fiyat ve modul tablolarinin bir kismi public | `oto servis programi fiyat kullanici aylik bulut` |
| 2 | `oto servis CRM yazilimi` | Is emri + musteri/araç gecmisi + randevu; "CRM" genelde operasyon modulu | `oto servis CRM yazilimi randevu WhatsApp musteri memnuniyeti` |
| 3 | `oto servis randevu takip programi` | Web tabanli randevu, is emri, WhatsApp/SMS hatirlatma sayfalari | `oto servis randevu takip programi` |
| 4 | `oto servis WhatsApp otomasyon` | Servis durumu, randevu hatirlatma, teklif/fatura bildirimleri | SERP'te Livo / Mekaniq / OtoCore / PADOK tekrar |
| 5 | `oto servis Google yorum yonetimi` | Jetyorum, Supsis, Restarun, Piyzi gibi yatay yorum platformlari | `oto servis musteri deneyimi yazilimi Turkiye Google yorum yonetimi` |
| 6 | `oto servis Google Haritalar SEO` / `yakınımdaki tamirci` | Ajans bloglari ve yerel SEO rehberleri | `oto servis Google yorum yonetimi yerel SEO ajans` |
| 7 | `yetkili servis musteri memnuniyet anketi` | Akademik / CX / anket kaynaklari; urun sayfasi daha az | `yetkili servis musteri memnuniyet anketi NPS otomotiv servis` |
| 8 | `oto servis NPS` / `otomotiv servis NPS` | Genel NPS araclari + otomotiv CX vaka icerikleri | ayni sorgu ailesi |
| 9 | `oto servis musteri memnuniyeti yazilimi` | Operasyon yazilimi sayfalari "memnuniyet" faydasi yazar; dar exact-match az | `oto servis musteri deneyimi yazilimi` |
| 10 | `oto servis yorum widget` / `yorum arttirma oto servis` | Yorum toplama + widget platformlari; policy riski yuksek | Jetyorum / Piyzi kaynaklari |

**Nefalix gorunurlugu:** `site:nefalix.com oto servis yorum yonetimi WhatsApp NPS` sorgusunda public `/blog` sonucu gorundu; blog indeksinde en az iki oto servis NPS / tekrar ziyaret basligi var. Bu oturumda `/geo` icinde oto servis exact-match pillar veya oto karsilastirma GEO'su dogrulanmadi.

---

## 2) Kim siralaniyor? (marka + model + neden)

### 2.1 `oto servis programi` / `oto servis yonetim yazilimi`

| Marka / site | Model | Neden siralaniyor (SERP sinyali) |
|--------------|-------|----------------------------------|
| **Mekaniq** — [mekaniq.com.tr](https://mekaniq.com.tr/) | Yazilim (bulut oto servis yonetimi) | Is emri, musteri/araç karti, stok, fatura, randevu, WhatsApp bildirim, rapor ve fiyat tablosu tek sayfada. |
| **OtoCore** — [otocore.tr](https://otocore.tr/) | Yazilim (bulut oto servis yonetimi) | Randevu, is emri, stok, kasa, WhatsApp, plaka/ruhsat okuma ve musteri portali; SERP snippet'inde yillik/aylik fiyat gorunuyor. |
| **OtoServiso** — [otoserviso.com/fiyatlar](https://www.otoserviso.com/fiyatlar) | Yazilim (oto servis programi) | Fiyat sayfasi exact-match; Profesyonel/Kurumsal paketleri SERP'te net gorunuyor. |
| **Hayat Yazilim PADOK Bulut** — [hayatyazilim.com/padok-bulut](https://hayatyazilim.com/padok-bulut/) | Yazilim (bulut oto servis programi) | Servis & is emri, ruhsat OCR, cari/stok/fatura ve WhatsApp modulu; fiyat konfiguratoru var. |
| **Canbus / ESN Sistem / Can Eke** — [canbus.net.tr](https://canbus.net.tr/servis-programi/), [esnsistem.com](https://www.esnsistem.com/urunler/oto-servis-programi), [caneke.com.tr](https://caneke.com.tr/teknik-servis-yazilimi/) | Yazilim (servis takip / teknik servis) | Araç kabul, is emri, stok, faturalandirma, CRM ve bulut altyapi anlatimlari; fiyatlar bu oturumda public rakam olarak ayrismadi. |

**Desen:** Bu kume Nefalix'in birebir rakibi degil; esas isleri servis operasyonu, muhasebe, stok ve is emri. Nefalix burada HBYS/PMS benzeri "yerine gecen sistem" degil, servis programindan tetik alan NPS/yorum/WhatsApp/kriz katmani olarak konumlanmali.

### 2.2 `oto servis randevu takip programi` / WhatsApp bildirim

| Marka / site | Model | Neden |
|--------------|-------|-------|
| **Livo Yazilim** — [livoyazilim.com/oto-servis-randevu-takip-programi](https://www.livoyazilim.com/oto-servis-randevu-takip-programi/) | Yazilim (randevu + servis yonetimi) | Online randevu, kapasite kontrolu, is emri, WhatsApp/SMS onay-hatirlatma ve araç hazir bildirimi akisi net anlatiliyor. |
| **Mekaniq** | Yazilim | "Is devam ediyor" durumunda otomatik WhatsApp, randevu hatirlatma ve fatura bildirimi gibi operasyon bildirimleri sayfada. |
| **PADOK Bulut** | Yazilim | WhatsApp bilgilendirme ek modulu; servis durumu, teklif ve hatirlatmalari musteriye iletme vaadi. |
| **OtoCore** | Yazilim | WhatsApp'i randevu/is emri/stok/kasa ile tek panelde anlatir; musteri portali standart oldugunu belirtir. |

**Desen:** WhatsApp bu SERP'te "musteri deneyimi"nden cok operasyonel bildirim araci olarak geciyor. Nefalix icin bosluk, teslim sonrasi NPS/yorum talebi, dusuk skor alarmi ve tekrar ziyaret akisini ayni WhatsApp temasindan kurmak.

### 2.3 `oto servis Google yorum yonetimi` / yorum toplama

| Marka / site | Model | Neden |
|--------------|-------|-------|
| **Jetyorum** — [jetyorum.com/otomobil-servisleri-bayileri](https://www.jetyorum.com/otomobil-servisleri-bayileri) | Yazilim (yorum toplama + widget + NLP) | Oto bayileri/servisleri icin yorum toplama, tek panel, akilli yanitlayici, CRM/ERP entegrasyonu ve web sitesi widget'i anlatiliyor. |
| **Supsis AI** — [supsis.com/tr/google-business-entegrasyonu](https://supsis.com/tr/google-business-entegrasyonu) | Yazilim (omnichannel inbox + Google yorum) | Google yorumlarini WhatsApp/Instagram gibi kanallarla ayni temsilci panelinde toplama ve AI yanit onerisi sunma. |
| **Restarun** — [restarun.com](https://restarun.com/) | Yazilim (Google yorum yonetimi) | Lokasyon bazli Google yorum takibi, AI yanit onerisi, bildirim, analitik ve rakip karsilastirma vaadi. |
| **Piyzi** — [piyzi.com/ozellikler/google-yorum-kazandirma](https://piyzi.com/ozellikler/google-yorum-kazandirma) | Yazilim (yorum talep otomasyonu) | Randevu sonrasi Google yorum linki, segment filtreleri ve raporlar anlatiliyor; review-gating riski tasiyan ifadeler var (bkz. §5). |

**Desen:** Bu kume yorum tarafinda daha yakin rakip. Ancak cogu yatay (restoran, perakende, klinik vb.) veya tek fonksiyonlu; oto servis is emri/randevu sistemleriyle "geri bildirim dongusunu kapatma" iddiasi sinirli.

### 2.4 `oto servis Google Haritalar SEO` / yerel SEO ajanslari

| Marka / site | Model | Neden |
|--------------|-------|-------|
| **Kobimedya** — [kobimedya.com/blog/oto-servis-google-haritalar-seo](https://kobimedya.com/blog/oto-servis-google-haritalar-seo) | Ajans (yerel SEO / dijital pazarlama) | "Yakınımdaki tamirci" niyeti, kategori/hizmet etiketleri, yorum sayisi ve yanit hizi uzerine uzun rehber. |
| **SEOYerel** — [seoyerel.com/...otomotiv-servisleri](https://seoyerel.com/otomotiv-servisleri-icin-yerel-seo-rehberi-2026-guncel-stratejiler/) | Ajans / yerel SEO icerigi | GBP, yorum, QR/SMS ile yorum isteme ve olumsuz yorum yanitlama checklist'i. |
| **Medya Siber / ORCA Software / Ulusoy Digital** | Ajans / rehber | Google Maps optimizasyonu, Local Pack, NAP, yorum stratejisi ve sahte yorum uyarilari. |

**Desen:** "Itibar" sorgusu yazilimdan cok ajans ve rehberlerle dolu. Nefalix'in GEO icerigi bu alanda ajansi asagilamadan "ajans strateji kurar; yazilim gunluk yorum/NPS nobetini olcekler" ayrimini kurmali.

### 2.5 `yetkili servis musteri memnuniyet anketi` / akademik ve CX kaynaklari

| Kaynak | Tip | Neden |
|--------|-----|-------|
| **DergiPark / International Journal of Advances in Engineering and Pure Sciences** — [dergipark.org.tr/en/pub/jeps/article/1590845](https://dergipark.org.tr/en/pub/jeps/article/1590845) | Akademik | Turkiye'de yetkili otomobil servisi baglaminda ACSI modeliyle memnuniyeti etkileyen faktorleri inceliyor; algilanan kaliteyi merkezi faktor olarak ozetliyor. |
| **PressAcademia DOI** — [doi.org/10.17261/pressacademia.2017.645](https://doi.org/10.17261/pressacademia.2017.645) | Akademik | Yetkili servis sonrasi memnuniyetin tavsiye davranisina etkisi; musteri danismani ve baslangicta verilen fiyata sadik kalma bulgulari SERP snippet'inde gorundu. |
| **Staffino** — [staffino.com/tr/otomotiv-endustrisinde-musteri-deneyimi](https://staffino.com/tr/otomotiv-endustrisinde-musteri-deneyimi/) | CX yazilimi / vaka icerigi | Otomotiv servis, lastik servis ve kaporta onarimi temas noktalarinda CSAT/NPS programi anlatimi. |
| **QuestionPro NPS sablonu** — [questionpro.com/tr/survey-templates/net-promoter-score-nps-survey](https://www.questionpro.com/tr/survey-templates/net-promoter-score-nps-survey/) | Anket SaaS / sablon | Genel NPS soru sablonu; oto servis ozel degil ama "tavsiye eder misiniz" formatini destekliyor. |

---

## 3) Alt sorular (PAA benzeri + sayfa SSS tekrarlarindan)

1. Oto servis programi **is emri, stok, fatura, randevu ve WhatsApp'i** tek panelde toplar mi? (Mekaniq, OtoCore, PADOK, Livo)
2. Servis sonrasi musteriye **WhatsApp/SMS ile hangi bildirimler** gitmeli: randevu onayi, 24 saat hatirlatma, is basladi, araç hazir, fatura/teklif? (Livo, Mekaniq, PADOK)
3. Google yorum linki **her musteriden mi** istenmeli, yoksa segment/filtre mi kullanilmali? (Piyzi ve Jetyorum sayfalari; policy riski §4)
4. Olumsuz Google yorumuna oto servis sahibi **ne kadar hizli ve hangi tonla** cevap vermeli? (Kobimedya, SEOYerel, genel Maps SEO rehberleri)
5. Widget ile Google yorumlarini siteye basmak **dogrulama ve guncellik riski** dogurur mu? (Jetyorum widget/API anlatimi; Reklam Kurulu uyarisi plan §4a)
6. Yetkili serviste tavsiye davranisini en cok **hangi temas noktasi** etkiler: musteri danismani, teslim hizi, fiyat tutarliligi, algilanan kalite? (DergiPark / PressAcademia kaynaklari)
7. Oto servis yazilimi ile NPS/itibar yazilimi **ayni sey mi**? (SERP deseninden: hayir; biri is emri/stok, digeri geri bildirim/yorum/kriz dongusu)

---

## 4) Fiyat / ozellik seffafligi (bu oturumda dogrulanan)

| Rakip | Tip | Public fiyat / seffaflik | Kaynak |
|-------|-----|--------------------------|--------|
| **Mekaniq** | Yazilim (oto servis yonetimi) | Ucretsiz paket; Baslangic **799 TL/ay**, Profesyonel **1.499 TL/ay**, Premium **2.099 TL/ay**, Kurumsal **3.499 TL/ay**; WhatsApp eklentisi **99 TL/ay**, E-Fatura **299 TL/ay** | [mekaniq.com.tr](https://mekaniq.com.tr/) |
| **OtoCore** | Yazilim (oto servis yonetimi) | SERP ciktisinda: **1.500 TL/ay + KDV**, **15.000 TL/yil + KDV**, 2 yil **20.000 TL**; 30 gun deneme; sayfa fetch zaman asimi verdi, bu satir SERP snippet'ine dayanir | [otocore.tr](https://otocore.tr/) |
| **OtoServiso** | Yazilim (oto servis programi) | SERP ciktisinda: Profesyonel **999 TL/ay**, Kurumsal **1.599 TL/ay**, KDV dahil; fetch 500 verdi, bu satir SERP snippet'ine dayanir | [otoserviso.com/fiyatlar](https://www.otoserviso.com/fiyatlar) |
| **Hayat Yazilim PADOK Bulut** | Yazilim (bulut oto servis programi) | Baslangic **990 TL/ay + KDV**; WhatsApp mesajlasma **+150 TL**, ek kullanici **+390 TL**; yillik 9.900 TL/yil (~825 TL/ay) | [hayatyazilim.com/padok-bulut](https://hayatyazilim.com/padok-bulut/) |
| **Livo Yazilim** | Yazilim (randevu + servis yonetimi) | Ozellik seffaf; bu oturumda public aylik TL dogrulanmadi (demo CTA) | [livoyazilim.com](https://www.livoyazilim.com/oto-servis-randevu-takip-programi/) |
| **Jetyorum** | Yorum toplama / itibar yazilimi | Ozellik seffaf; public fiyat bu oturumda dogrulanmadi | [jetyorum.com/otomobil-servisleri-bayileri](https://www.jetyorum.com/otomobil-servisleri-bayileri) |
| **Supsis AI / Restarun / Piyzi** | Google yorum / inbox / otomasyon | Deneme sureleri ve ozellikler public; bu oturumda oto servis ozel public fiyat dogrulanmadi | [supsis.com](https://supsis.com/tr/google-business-entegrasyonu), [restarun.com](https://restarun.com/), [piyzi.com](https://piyzi.com/ozellikler/google-yorum-kazandirma) |
| **Canbus / ESN Sistem / Can Eke** | Servis takip / teknik servis yazilimi | Ozellik anlatimi var; fiyat bu oturumda public rakam olarak dogrulanmadi | [canbus.net.tr](https://canbus.net.tr/servis-programi/), [esnsistem.com](https://www.esnsistem.com/urunler/oto-servis-programi), [caneke.com.tr](https://caneke.com.tr/teknik-servis-yazilimi/) |
| **Nefalix** (karsilastirma) | Yazilim (yorum + NPS + WhatsApp + kriz katmani) | Baslangic **9.500 TL/ay** + **25.000 TL** kurulum; Pro **14.900 TL/ay** + **50.000 TL** kurulum; Kurumsal **45.000 TL+/ay**; Sentinel **+3.500 TL/ay**, Recall **+2.500 TL/ay** | [nefalix.com/fiyatlar](https://nefalix.com/fiyatlar) |

**Fiyat yorumu:** Oto servis operasyon yazilimlari aylik 799-3.499 TL bandinda public paketler gosterebiliyor; Nefalix bu kategorinin yerine gecen ucuz is emri yazilimi gibi anlatilmamali. Dogru karsilastirma: "servis programi + Nefalix geri bildirim/itibar katmani" veya "tek fonksiyonlu Google yorum araci vs Nefalix NPS/WhatsApp/kriz akisi".

---

## 5) Uyum ve director risk notlari

### 5.1 Review-gating riski

Jetyorum otomobil sayfasinda "sadece mutlu musterilerinizi yorum birakma surecine yonlendirin; olumsuz durumlarda geri bildirimlerini alarak ... negatif yorumlarin onune gecin" ifadesi var. Piyzi Google yorum sayfasinda "sadece belirli hizmet alan veya memnuniyet puani yuksek musterilere talep gonderin" ve "kotu deneyim yasamis musteriler elenebilir" ifadeleri var. Bu ifadeler Google yorum politikasi ve Nefalix director kuralindaki review-gating kapisi acisindan **RED sinyali** sayilmalidir.

Nefalix oto servis GEO iceriginde "memnun musteriyi Google'a, memnun olmayani iceriye" gibi bir akis ovulmemeli. Guvenli ifade: servis sonrasi geri bildirim daveti tum uygun musterilere adil ve gonullu gonderilir; dusuk puanlar Google'a gitmeden "saklanmaz", operasyon ekibine cozum gorevi olarak dusurulur; platform kurallari ve musteri rizasi korunur.

### 5.2 Google yorum widget riski

Jetyorum sayfasi iFrame/API ile yorumlari web sitesine tasima ve zengin snippet ekleme iddiasi kuruyor. Plan §4a'daki Reklam Kurulu / dogrulanmamis ucuncu taraf yorum uyarisi nedeniyle Nefalix iceriginde widget anlatimi olacaksa kaynak, tarih, dogrulama ve guncel puan tutarliligi uyari mekanizmasi yazilmali. Bu arastirma yeni widget ozelligi iddia etmez.

### 5.3 KVKK rol ayrimi

Oto servis baglaminda veri sorumlusu servis/bayi isletmesidir; Nefalix gibi yazilim saglayici genelde veri isleyen konumunda konumlanir. Arac plakasi, iletisim bilgisi, servis gecmisi, sikayet metni ve WhatsApp kayitlari kisisel veri sayilabilecegi icin pazarlama icerigi "tam garanti KVKK uyumu" gibi kesin cumleler kurmamali; aydinlatma, saklama, riza/mesaj izni ve alt isleyen sozlesmesi servis tarafinda netlesmelidir.

---

## 6) nefalix.com'da oto servis yuzeyi

Dogrulama: `site:nefalix.com oto servis yorum yonetimi WhatsApp NPS` canli arama sonucu (2026-08-21).

| Yuzey | Durum |
|-------|-------|
| `/blog` | Oto servis NPS / tekrar ziyaret temali en az iki blog karti gorundu: 10 Ağu 2026 ve 24 Tem 2026 basliklari. |
| `/geo` | Bu oturumda oto servis exact-match GEO paketi veya karsilastirma sayfasi dogrulanmadi. |
| `/sektorler#oto` | Plan baglaminda sektor yuzeyi bekleniyor; bu oturumda ayrica fetch edilmedi. |
| `/fiyatlar` | Nefalix public fiyatlari saglik arastirmasinda dogrulanmis durumda; bu dosyada karsilastirma icin ayni kaynak kullanildi. |

### Eksik / Faz 4 backlog

| Bosluk | Neden kritik | Onerilen GEO / icerik |
|--------|--------------|-----------------------|
| **`oto servis yorum yonetimi yazilimi` exact-match GEO** | SERP'te Jetyorum/Supsis/Restarun/Piyzi ve ajans rehberleri var; Nefalix blog disinda gorunmuyor | Answer-first: yorum + NPS + WhatsApp + kriz alarmi ayrimi |
| **`oto servis programi vs itibar/NPS yazilimi`** | Mekaniq/OtoCore/PADOK is emri/stok/fatura cozer; alici Nefalix'i bu kategoriyle karistirabilir | Adil ayrim: servis programi yerine gecmez, tetik ve geri bildirim katmani olur |
| **`oto servis Google yorum daveti review-gating olmadan nasil yapilir`** | Rakip sayfalarda secici davet dili var; Nefalix uyumlu alternatifle ayrisabilir | Policy guvenli FAQ + Google yorum/hediye yok uyarisi |
| **`yetkili servis NPS anketi hangi temas noktalarini olcmeli`** | Akademik kaynak ve CX sayfalari var; operasyonel GEO boslugu | Müşteri danismani, fiyat tutarliligi, teslim hizi, algilanan kalite |
| **`olumsuz oto servis yorumuna nasil cevap verilir`** | Ajanslar bu long-tail'i dolduruyor; kriz/Sentinel ile dogal eslesme | KVKK/kisisel veri + plaka/servis detayi yazmama uyarisi |

---

## 7) Nefalix konumlandirma cikarimi (oto servis)

- Oto servis pazarinda **operasyon yazilimi doygun**: is emri, stok, fatura, randevu ve WhatsApp bildirimleri icin cok sayida yerli SaaS var.
- **Itibar/NPS katmani daha parcali**: Jetyorum/Piyzi/Supsis/Restarun gibi yatay yorum araclari var; oto servis is emri ve servis sonrasi kalite dongusuyle derin bag kuran konumlandirma az.
- Nefalix'in en guvenli mesaji: "Oto servis programinizin yerine gecmez; teslim sonrasi geri bildirim, Google yorum yanit disiplini, dusuk skor alarmi ve tekrar ziyaret aksiyonunu tek operasyon masasına tasir."
- Hukuki/uyum farki onemli: yorum karsiligi hediye/indirim yok, secici davet dili yok, widget varsa dogrulama/guncellik uyarisi, KVKK'da servis veri sorumlusu / Nefalix veri isleyen ayrimi.
- Ilk oto GEO seti icin once "program vs itibar katmani" ve "review-gating olmadan yorum daveti" konulari uretilmeli; bunlar hem rakip SERP bosluguna hem director kapisina en iyi uyuyor.

---

## 8) Kaynak logu

### Sorgular

- `oto servis müşteri deneyimi yazılımı Türkiye Google yorum yönetimi`
- `oto servis CRM yazılımı randevu WhatsApp müşteri memnuniyeti`
- `oto servis Google yorum yönetimi yerel SEO ajans`
- `yetkili servis müşteri memnuniyet anketi NPS otomotiv servis`
- `oto servis programı fiyat kullanıcı aylık bulut`
- `site:nefalix.com oto servis yorum yönetimi WhatsApp NPS`
- `Canbus oto servis programı fiyat Mysoft caneke değer yazılım ESN Sistem oto servis CRM`

### Fetch / kaynak URL'leri

- [Mekaniq — Oto servis yonetim yazilimi](https://mekaniq.com.tr/)
- [OtoCore — Oto servis yonetim yazilimi](https://otocore.tr/) (SERP snippet; fetch zaman asimi)
- [OtoServiso fiyatlar](https://www.otoserviso.com/fiyatlar) (SERP snippet; fetch 500)
- [Hayat Yazilim PADOK Bulut](https://hayatyazilim.com/padok-bulut/)
- [Livo Yazilim oto servis randevu takip programi](https://www.livoyazilim.com/oto-servis-randevu-takip-programi/)
- [Jetyorum otomobil servisleri / bayileri](https://www.jetyorum.com/otomobil-servisleri-bayileri)
- [Supsis AI Google Business entegrasyonu](https://supsis.com/tr/google-business-entegrasyonu)
- [Restarun Google yorum yonetimi](https://restarun.com/)
- [Piyzi Google yorum kazandirma](https://piyzi.com/ozellikler/google-yorum-kazandirma)
- [Kobimedya oto servis Google Haritalar SEO](https://kobimedya.com/blog/oto-servis-google-haritalar-seo)
- [SEOYerel otomotiv servisleri yerel SEO rehberi](https://seoyerel.com/otomotiv-servisleri-icin-yerel-seo-rehberi-2026-guncel-stratejiler/)
- [Canbus servis programi](https://canbus.net.tr/servis-programi/)
- [ESN Sistem oto servis programi](https://www.esnsistem.com/urunler/oto-servis-programi)
- [Can Eke teknik servis yazilimi](https://caneke.com.tr/teknik-servis-yazilimi/)
- [DergiPark — Otomotiv servis memnuniyetinde algilanan kalite ve deger](https://dergipark.org.tr/en/pub/jeps/article/1590845)
- [PressAcademia DOI — after-sales service satisfaction and recommendation](https://doi.org/10.17261/pressacademia.2017.645)
- [Staffino otomotiv endustrisinde musteri deneyimi](https://staffino.com/tr/otomotiv-endustrisinde-musteri-deneyimi/)
- [QuestionPro NPS anket sablonu](https://www.questionpro.com/tr/survey-templates/net-promoter-score-nps-survey/)

---

## 9) Director karari (bu parca)

**Onay.** Bu dosya yayina alinacak GEO metni degil, arastirma girdisidir; yine de director kapisi acisindan kritik riskler isaretlendi: rakipler yazilim / ajans / operasyon programi olarak ayrildi, fiyat/ozelliklerde kaynak verildi, review-gating ve widget riskleri kaynakli olarak yazildi, KVKK rol ayrimi net tutuldu. Bu arastirmadan turetilecek her `geo/*.md` icin ayrica answer-first ve tekrar kontrolu yapilmalidir.

---

*Sonraki plan parcasi: Faz 4 otel GEO seti zaten arastirma hazir oldugu icin ilk 2-3 otel GEO pillar'i; ardindan bu dosyaya dayali oto GEO seti.*
