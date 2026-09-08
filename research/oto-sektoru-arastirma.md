# Oto sektoru - servis deneyimi / yorum / CRM otomasyonu arama arastirmasi

**Tarih:** 2026-09-08  
**Kapsam:** Turkiye - oto servis, tamirhane, lastikci, kaporta, yetkili servis / bayi servis agi  
**Tema:** oto servis musteri deneyimi + Google yorum yonetimi + WhatsApp/CRM otomasyonu  
**Yontem:** Canli web arama / SERP sonuclari + sayfa fetch. Keyword Planner / Ahrefs hacim API'si yok; "en yogun" siralama **sayisal arama hacmi degil**, bu oturumda gozlenen **SERP ticari yogunlugu + sorgular arasi tekrar**. Hacim iddiasi yapilmaz.

**Kaynak notu:** Web arama arac ciktisi Google TR SERP'inin anlik bir gorunumudur; konum, kisisellestirme ve tarih farki olabilir. People Also Ask kutusu ayri blok olarak parse edilmedi; alt sorular siralanan sayfalarin H2/SSS metinlerinden derlendi.

---

## 0) Plan durumu ve siradaki faz

Gap notlarina gore Faz 0 teknik indeks sorunu kapatildi; saglik ve otel Faz 1 arastirmalari mevcut. Bu kosuda tamamlanan ana teslimat **Faz 1 oto sektoru arastirmasi**dir. Bundan sonraki pratik faz, plan sirasi bozulmadan **Faz 4 otel GEO seti**dir; otel arastirmasi hazir oldugu icin once `otel yorum yonetimi yazilimi`, `TripAdvisor + Booking + Google tek panel`, `PMS vs itibar SaaS` ve `misafir NPS + WhatsApp` GEO parcasi uretilmelidir. Oto GEO seti bunun ardindan bu dosyadaki kaynaklara dayanarak uretilmelidir.

---

## 1) En yogun ticari sinyalli kelime obekleri (Turkce)

Sira = bu arastirmada gozlenen SERP ticari yogunlugu ve sorgular arasi tekrar (yuksek -> dusuk).

| # | Obek | SERP karakteri | Ornek sorgu kaynagi |
|---|------|----------------|---------------------|
| 1 | `oto servis CRM` / `oto servis CRM yazilimi` | CRM, WhatsApp inbox ve randevu takip sayfalari | `oto servis CRM yazilimi fiyat WhatsApp randevu memnuniyet anketi` |
| 2 | `oto servis programi` / `oto servis yonetim yazilimi` | Garaj/servis operasyon yazilimlari; fiyat sayfalari daha gorunur | `oto servis programi fiyatlari bulut servis takip yazilimi` |
| 3 | `oto servis randevu programi` | Randevu, bakim gecmisi, is emri ve kasa akisi | `oto servis WhatsApp otomasyon yazilimi Turkiye` |
| 4 | `oto servis WhatsApp otomasyon` | CRM/inbox katmani; servis durumu, teklif onayi, bakim hatirlatma | `oto servis WhatsApp otomasyon yazilimi Turkiye` |
| 5 | `yetkili servis yazilimi` / `bayi servis otomasyonu` | Cok subeli yetkili servis ve bayi agi icin servis operasyonu | `yetkili servis musteri memnuniyet anketi yazilimi otomotiv` |
| 6 | `oto servis musteri deneyimi yazilimi` | Daha dar SERP; yorum/AI araclari ve servis yazilimlari karisik | `oto servis musteri deneyimi yazilimi Turkiye Google yorum yonetimi` |
| 7 | `oto servis Google yorum yonetimi` | Genel Google yorum AI araclari + Jetyorum otomobil servis blogu | `oto servis Google yorum yonetimi yazilimi Turkiye` |
| 8 | `otomotiv musteri memnuniyet anketi` | Pisano gibi CX platformlari + servis yazilimi bloglari | `yetkili servis musteri memnuniyet anketi yazilimi otomotiv` |
| 9 | `arac servis takip programi` / `arac bakim takip programi` | Garaj yonetimi, periyodik bakim hatirlatma | SERP capraz tekrar |
| 10 | `Google yorum AI oto tamirci` | Genel AI yorum uygulamalari oto tamircileri sektor listesinde anar | `oto servis Google yorum yonetimi yazilimi Turkiye` |

**Nefalix gorunurlugu:** `nefalix.com/sektorler` sayfasi auto servisleri yol haritasinda anar; Nefalix'in bu sorgular icin exact-match oto GEO/pillar yuzeyi bu checkout'ta yok. Canli landing'e dokunulmadigi icin deploy/gorunurluk iddiasi yapilmaz.

---

## 2) Kelime obeklerinde kim siralaniyor? (marka + model + neden)

### 2.1 Servis / garaj yonetim yazilimlari

| Marka / site | Model | Neden siralaniyor (SERP sinyali) | Kaynak |
|---|---|---|---|
| **Mekaniq** | Servis/garaj yonetim yazilimi | Is emri, musteri-arac karti, stok, fatura, randevu, WhatsApp bildirim ve fiyat tablolarini tek sayfada veriyor. | [mekaniq.com.tr](https://mekaniq.com.tr/) |
| **PADOK Bulut / Hayat Yazilim** | Bulut oto servis programi | Arac kabul, is emri, ruhsat/plaka okuma, cari-stok-fatura, musteri takip portali ve WhatsApp mesajlasma modullerini detaylandiriyor. | [hayatyazilim.com/padok-bulut](https://hayatyazilim.com/padok-bulut/) |
| **OtoServiso** | Oto servis programi | SERP'te fiyat sayfasi ve 2026 fiyat rehberi gorundu; fetch denemesi 500 verdigi icin fiyat bilgisi raporda yalniz "SERP'te goruldu, sayfa fetch dogrulamasi basarisiz" notuyla sinirli tutuldu. | [otoserviso.com/fiyatlar](https://www.otoserviso.com/fiyatlar) |
| **Canbus** | Yetkili servis / bayi servis yazilimi | Cok sube, arac kabul, is emri, stok, garanti, SMS/e-posta bildirim ve raporlama anlatimiyla yetkili servis sorgularina oturuyor. | [canbus.net.tr/yetkili-servis-yazilimi](https://canbus.net.tr/yetkili-servis-yazilimi/) |
| **Piyzi** | Oto servis randevu ve bakim takip programi | Online randevu, periyodik bakim otomasyonu, WhatsApp hatirlatma, kasa ve Google yorum otomasyonu basliklariyla sektor sayfasi uretiyor. | [piyzi.com/sektorler/oto-servis-randevu-programi](https://piyzi.com/sektorler/oto-servis-randevu-programi) |

### 2.2 CRM / WhatsApp / inbox katmani

| Marka / site | Model | Neden siralaniyor (SERP sinyali) | Kaynak |
|---|---|---|---|
| **Rocketly** | Oto servis CRM ve mesaj/inbox katmani | WhatsApp, Instagram, web formu, servis pipeline'i, teklif onayi, periyodik bakim hatirlatmasi ve AI taslaklarini servis is akisiyle anlatiyor. Kendini garaj yonetim yazilimi degil, CRM/iletisim katmani olarak konumluyor. | [gorocketly.com/sektorler/oto-servis](https://gorocketly.com/sektorler/oto-servis) |
| **Rapitek CRM** | Yapilandirilan CRM | Oto servis icin WhatsApp Business API / QR esleme, ERP entegrasyonu, AI satis pipeline'i ve $25/kullanici/ay baslangic fiyatini acik yaziyor. | [rapitek.com/oto-servis-crm](https://rapitek.com/oto-servis-crm/) |
| **OzgurKod** | Oto servis CRM | SERP snippet'inde arac durum bilgilendirme, parcali teklif onayi ve WhatsApp uzerinden yazili onay temalariyla gorundu; bu kosuda ayrica fetch edilmedi. | [ozgurkod.com/cozumler/oto-servis](https://ozgurkod.com/cozumler/oto-servis) |
| **Ulako** | Omnichannel CRM / hazir sektor akislar | WhatsApp, Telegram, Instagram ve web mesajlarini tek panelde toplar; sektor sablonlari arasinda oto servisi anar, fiyatlari aciktir. | [ulako.co](https://ulako.co/) |

### 2.3 Google yorum / itibar / AI yanit araclari

| Marka / site | Model | Neden siralaniyor (SERP sinyali) | Kaynak |
|---|---|---|---|
| **Sparkavis** | Google Business Profile yorum mobil uygulamasi | Google yorum goruntuleme, AI yanit, analiz, otomatik yanit ve yorum widget'i sunuyor; sektor listesinde oto servisi/oto tamircileri aniyor. | [sparkavis.app/tr](https://sparkavis.app/tr) |
| **Cevaply** | Yorum yonetim platformu | Google + TripAdvisor yorumlarini tek panelde, dusuk puanli yorum onceliklendirme ve WhatsApp/e-posta uyarisi ile konumluyor; daha cok otel/restoran dilinde. | [cevaply.com](https://cevaply.com/) |
| **Akilli Isler** | AI destekli itibar yonetimi SaaS | Google, Tripadvisor ve Yemeksepeti yorumlarini AI ile analiz/yanit odagina aliyor; oto disinda daha genis yerel isletme dili var. | [akilliisler.com](https://akilliisler.com/) |
| **Replai / Digital Kure** | Google yorum AI yanit araci | Google yorumlarina marka tonu ile AI yanit; 1-3 yildiz yorumlar icin kontrol vurgusu var. | [digitalkure.com/replai](https://www.digitalkure.com/replai) |
| **Jetyorum** | Yorum toplama / sosyal kanit | Otomobil bayileri ve servisleri icin Google/Facebook yorumlarinin yerel itibar ve musteri deneyimi faydalarini anlatan sektor blogu var. | [jetyorum.com/otomobil-servisleri-google-isletme](https://www.jetyorum.com/otomobil-servisleri-google-isletme) |

**Ortak SERP deseni:** Oto servis sorgularinda "operasyon yazilimi" ve "yorum/itibar yazilimi" henuz tam birlesmemis. Servis yazilimlari is emri, stok, fatura ve randevuyu; yorum araclari Google profilini; CRM oyunculari WhatsApp/inbox ve teklif onayini sahipleniyor. Nefalix icin bosluk, **servis sonrasi memnuniyet + Google yorum + WhatsApp takip + kriz uyarisi** paketini garaj yaziliminin yerine gecmeden tamamlayici katman olarak anlatmak.

---

## 3) Alt sorular (PAA benzeri + sayfa SSS/H2)

1. Oto servis CRM'i **garaj/servis yonetim yaziliminin yerine mi gecer**, yoksa iletisim katmani midir? (Rocketly bunu acikca "garaj yonetim yazilimi degil" diye ayiriyor.)
2. Tek WhatsApp numarasini **birden fazla servis danismani** kullanabilir mi? (Rapitek ortak gelen kutusu ve Meta/QR secenekleriyle anlatiyor.)
3. "Aracim ne durumda?" telefonlarini azaltmak icin **musteri portal linki veya WhatsApp durum bildirimi** nasil calisir? (PADOK, Mekaniq, Rocketly.)
4. Periyodik bakim hatirlatmasi tarih/km esigine gore **otomatik nasil tetiklenir**? (Piyzi, Rocketly, Mekaniq.)
5. Servis sonrasi memnuniyet anketi ve dusuk puanlarda **erken aksiyon** nasil alinmali? (Pisano / ESN Sistem SERP sinyali; Google yorum yonlendirmesi ayrica politika kontrollu olmali.)
6. Bakimdan sonra Google yorum istemek **Google politikalarina uygun mu**? Uygun sinir: tesvik yok, puan/icerik etkileme yok, olumsuz yorum engelleme yok.
7. Google yorumlarini web sitesinde widget olarak gostermek **dogrulama/uyari gerektirir mi**? Sparkavis/Jetyorum tipi sosyal kanit anlatimlarinda Reklam Kurulu riski nedeniyle kaynak ve dogrulama mekanizmasi netlesmeli.

---

## 4) Rakiplerde fiyat / ozellik seffafligi (somut rakam + kaynak)

| Rakip | Tip | Seffaflik | Somut rakam / not | Kaynak |
|-------|-----|-----------|-------------------|--------|
| **Mekaniq** | Servis/garaj yonetim yazilimi | Yuksek | Ucretsiz plan; Baslangic **999 TL/ay**, Profesyonel **1.999 TL/ay**, Premium **2.499 TL/ay**, Kurumsal **3.999 TL/ay**; WhatsApp eklentisi **99 TL/ay**, e-fatura **299 TL/ay**, sektor modulleri **699 TL/ay**. | [mekaniq.com.tr](https://mekaniq.com.tr/) |
| **PADOK Bulut** | Bulut oto servis programi | Yuksek | Ana program **1.150 TL/ay + KDV**; yillik **11.500 TL + KDV**; ilk 2 kullanici dahil, ek kullanici **390 TL/ay + KDV**; WhatsApp mesajlasma eklentisi **300 TL/ay**. | [hayatyazilim.com/padok-bulut](https://hayatyazilim.com/padok-bulut/) |
| **Rapitek CRM** | CRM / WhatsApp / ERP entegrasyon | Yuksek | Oto servis sayfasinda **$25/kullanici/ay'dan baslar**; kurulum, egitim, destek dahil oldugunu belirtiyor; 2-4 hafta canliya gecis iddiasi var. | [rapitek.com/oto-servis-crm](https://rapitek.com/oto-servis-crm/) |
| **Sparkavis** | Google yorum AI uygulamasi | Yuksek | Free **0 EUR/ay**; Pro **9,99 EUR/ay**; Business **29,99 EUR/ay**; Business planinda onaysiz otomatik yanit. | [sparkavis.app/tr](https://sparkavis.app/tr) |
| **Cevaply** | Yorum yonetim platformu | Dusuk-orta | 30 gun ucretsiz deneme / erken erisim; bu oturumda public aylik fiyat dogrulanmadi. | [cevaply.com](https://cevaply.com/) |
| **Canbus** | Yetkili servis yazilimi | Ozellik seffaf, fiyat kapali | Cok sube, is emri, stok, garanti, SMS/e-posta bildirim var; public fiyat bu oturumda gorulmedi. | [canbus.net.tr/yetkili-servis-yazilimi](https://canbus.net.tr/yetkili-servis-yazilimi/) |
| **Piyzi** | Oto servis randevu / bakim takip | Ozellik seffaf, fiyat bu fetch'te kapali | 14 gun deneme, online randevu, periyodik bakim, WhatsApp hatirlatma ve Google yorum otomasyonu; fetch edilen kisimda aylik fiyat dogrulanmadi. | [piyzi.com/sektorler/oto-servis-randevu-programi](https://piyzi.com/sektorler/oto-servis-randevu-programi) |
| **OtoServiso** | Oto servis programi | Belirsiz | SERP snippet'inde fiyat sayfasi ve 2026 fiyat rehberi gorundu; WebFetch iki kez 500 aldigi icin somut fiyat rapora dogrulanmis veri olarak alinmadi. | [otoserviso.com/fiyatlar](https://www.otoserviso.com/fiyatlar) |
| **Nefalix** | Yorum + mesaj + NPS/Sentinel/Recall katmani | Yuksek | Baslangic **9.500 TL/ay** + **25.000 TL** kurulum; Profesyonel **14.900 TL/ay** + **50.000 TL** kurulum; Kurumsal **45.000 TL+/ay**; Sentinel **+3.500 TL/ay**, Recall **+2.500 TL/ay**. | [nefalix.com/fiyatlar](https://nefalix.com/fiyatlar) |

**Yorum:** Garaj yonetim yazilimlari Nefalix'ten daha dusuk aylik fiyata operasyon omurgasi sunuyor; Nefalix'in oto mesajlasmasi "servis programi yerine gecen ERP" gibi anlatilmamali. Daha dogru konum: mevcut servis programi / defter / Excel uzerine **musteri deneyimi, yorum, WhatsApp, NPS ve kriz alarmi katmani**.

---

## 5) Politika / uyum notlari

### Google yorum tesviki ve review-gating

Google Haritalar Katkida Bulunulan Icerik Politikasi, yorum veya puan karsiliginda odeme, indirim, ucretsiz urun/hizmet gibi tesvikleri yasaklar; saticilarin olumsuz yorumlari engellemesine veya ozellikle olumlu yorum istemesine izin vermez. Ayni sayfa, tesvik sunmadan ve puan/icerigi etkilemeden gercek deneyimi yansitan yorum istemeye izin verir. Kaynak: [Google Haritalar politikasi](https://support.google.com/contributionpolicy/answer/7400114?hl=tr).

Bu nedenle Piyzi sayfasinda gecen "bakimdan cikan memnun musteriye otomatik Google yorum talebi" ifadesi, **Nefalix iceriginde model alinmamali**; Nefalix dili "servis sonrasi tum uygun musterilere tarafsiz geri bildirim daveti; dusuk puanda ic aksiyon, yorum daveti akisi politikalara gore tasarlanir" seklinde olmalidir.

### Google yorum widget / sosyal kanit

Sparkavis "Google yorumlarinizi web sitenizde gosterin" ozelligini, Jetyorum ise Google yorumlarini sosyal kanita cevirmeyi anlatiyor. Nefalix oto iceriginde widget konusu acilacaksa, kaynak platform, yorum dogrulama mekanizmasi ve "ucuncu taraf yorumlarinin ticari sitede yeniden yayini" riski mutlaka belirtilmelidir. Bu uyari olmadan widget dili director kuralina gore RED sebebidir.

### KVKK rol ayrimi

Oto servislerde veri sorumlusu servis / bayi / yetkili servis agidir; Nefalix ve benzeri yazilim saglayicilari islenen veri kapsaminda genellikle veri isleyen konumundadir. Plaka, telefon, arac servis gecmisi, hasar/kasko dosyasi, teklif ve WhatsApp yazismalari kisisel veri icerebilir. Icerik "KVKK'yi tamamen cozer" gibi kesin vaat kurmamali; rol ayrimi, sozlesme, aydinlatma ve saklama politikasi gerekliligini net tutmalidir.

---

## 6) nefalix.com'da oto yuzeyi

Canli fetch: `nefalix.com/sektorler` auto servisleri "ayni motorun yol haritasi" olarak konumluyor; onceligin saglik kurumlari oldugunu acikca yaziyor. `nefalix.com/fiyatlar` sektor seciminde "Auto Servis" secenegini gosteriyor ve paket fiyatlarini seffaf yayinliyor.

| Yuzey | Durum |
|-------|-------|
| `/sektorler` | Auto servis yol haritasinda; detayli oto landing / deep URL yok. |
| `/fiyatlar` | Auto servis sektor secimi var; fiyatlar public. |
| `/geo` | Bu checkout'taki `geo/*.md` saglik odakli 6 pillar; oto GEO parcasi yok. |
| `/blog` | Bu kosuda oto blog envanteri taranmadi; ana teslimat arastirma dosyasidir. |
| Landing repo | Bu checkout'ta public site koduna dokunulmadi; smoke/deploy iddiasi yok. |

### Eksik / zayif (SERP bosluklarina gore)

| Bosluk | Neden kritik | Onerilen sayfa tipi |
|--------|--------------|---------------------|
| `oto servis musteri deneyimi yazilimi` GEO | SERP'te servis yazilimi ve yorum araclari ayrik; Nefalix tamamlayici katmani anlatabilir. | GEO answer-first |
| `oto servis Google yorum yonetimi` GEO | Google yorum AI araclari ve Jetyorum sektor blogu gorunuyor; policy uyumlu Nefalix dili gerekli. | GEO + policy SSS |
| `oto servis WhatsApp otomasyon` GEO | Rocketly/Rapitek/Piyzi bu niyeti sahipleniyor; Nefalix mesaj + yorum + NPS baglantisini kurabilir. | GEO |
| `servis programi vs musteri deneyimi platformu` | Mekaniq/PADOK gibi oyuncularla haksiz rekabet yapmadan kategori ayrimini netlestirir. | Karsilastirma / pillar |
| `periyodik bakim hatirlatma + yorum talebi` | Google review-gating riski yuksek; dogru akisi anlatan tarafsiz rehber eksik. | GEO + compliance brief |

---

## 7) Nefalix konumlandirma cikarimi (oto)

1. **Kategori boslugu:** Oto servis SERP'i garaj yonetim yazilimi ile genel Google yorum araci arasinda bolunmus. Nefalix bu ikisinin ortasinda, "servis sonrasi deneyim ve itibar katmani" olarak konumlanmali.
2. **Fiyat karsilastirmasi dikkatli olmali:** Mekaniq/PADOK gibi araclar daha ucuz gorunur cunku operasyon yazilimi fiyatlaridir; Nefalix'in daha yuksek fiyatini servis programi ile ayni kategoriye koymak yaniltici olur. Karsilastirma "yerine gecme" degil "tamamlama" uzerinden kurulmalidir.
3. **WhatsApp dili guclu firsat:** "Aracim ne durumda?", teklif onayi, teslim bildirimi, periyodik bakim hatirlatmasi gibi gercek oto is akislari SERP'te tekrar ediyor. Nefalix oto GEO seti bu mikro sorulara answer-first yanit vermeli.
4. **Policy riski:** Google yorum talebi, sadece memnun musteriyi secen veya tesvik ima eden dille anlatilirsa RED. Tarafsiz davet, ic aksiyon ve insan onayi ayrimi korunmali.
5. **KVKK riski:** Plaka/telefon/arac gecmisi ve hasar yazismalari iceren akislar kisisel veri barindirir; "veri sorumlusu servis, veri isleyen Nefalix" ayrimi her oto iceriginde net olmali.

---

## 8) Director kapisi

**Karar:** Onay  

**Gerekce:** Bu arastirma dosyasi canli SERP/WebFetch kaynaklarina dayaniyor, rakipleri yazilim / CRM-inbox / yorum-itibar kategorilerine ayiriyor ve fiyat/ozellik iddialarini yalniz kaynakli oldugu yerde yaziyor. OtoServiso gibi fetch dogrulamasi basarisiz kalan kaynaklarda rakam iddiasi kurulmadi. Google yorum tesviki, widget ve KVKK rol ayrimi riskleri ayrica isaretlendi.

**Kontrol maddeleri:**

1. Tekrar icerik: **Onay** - saglik/otel arastirma formatini izliyor ama otoya ozgu rakipler, sorgular ve riskler var.
2. Cevap gec geliyor mu: **Onay** - dosya basinda faz ve teslimat durumu yazildi.
3. Kaynaksiz veya asagilayici rakip iddiasi: **Onay** - rakipler adil kategoriyle anlatildi; dogrulanmayan fiyatlar yazilmadi.
4. Yorum karsiligi hediye / secici davet imasi: **Onay** - riskli "memnun musteri" dili kaynakta rakip ifadesi olarak isaretlendi, Nefalix icin onerilmedi.
5. Google yorum widget + dogrulama uyarisi: **Onay** - widget/sosyal kanit anlatimlarina uyari eklendi.
6. KVKK bulanik mi: **Onay** - veri sorumlusu servis/bayi, veri isleyen Nefalix/yazilim saglayici ayrimi yazildi.
7. Kaynaksiz istatistik: **Onay** - sayisal hacim iddiasi yok; istatistik kaynaklari tekrarlanmadigi yerde kullanilmadi.

---

## 9) Kaynak logu

### Sorgular

- `oto servis musteri deneyimi yazilimi Turkiye Google yorum yonetimi`
- `oto servis CRM yazilimi fiyat WhatsApp randevu memnuniyet anketi`
- `oto servis Google yorum yonetimi yazilimi Turkiye`
- `yetkili servis musteri memnuniyet anketi yazilimi otomotiv`
- `oto servis WhatsApp otomasyon yazilimi Turkiye`
- `oto servis programi fiyatlari bulut servis takip yazilimi`

### Fetch / kaynak URL'leri

- [Mekaniq - oto servis yonetim yazilimi](https://mekaniq.com.tr/)
- [PADOK Bulut - oto servis programi](https://hayatyazilim.com/padok-bulut/)
- [Rapitek CRM - oto servis CRM](https://rapitek.com/oto-servis-crm/)
- [Rocketly - oto servis CRM ve bakim takip](https://gorocketly.com/sektorler/oto-servis)
- [Piyzi - oto servis randevu programi](https://piyzi.com/sektorler/oto-servis-randevu-programi)
- [Canbus - yetkili servis yazilimi](https://canbus.net.tr/yetkili-servis-yazilimi/)
- [Sparkavis - Google yorum AI](https://sparkavis.app/tr)
- [Cevaply - yorum yonetim platformu](https://cevaply.com/)
- [Jetyorum - otomobil servisleri Google yorumlari](https://www.jetyorum.com/otomobil-servisleri-google-isletme)
- [Google Haritalar Katkida Bulunulan Icerik Politikasi](https://support.google.com/contributionpolicy/answer/7400114?hl=tr)
- [Nefalix fiyatlar](https://nefalix.com/fiyatlar)
- [Nefalix sektorler](https://nefalix.com/sektorler)
- OtoServiso fiyat ve blog URL'leri fetch denemesinde 500 verdi; SERP'te goruldu ama somut fiyat kaniti olarak kullanilmadi.

---

*Dosya yolu: `research/oto-sektoru-arastirma.md` - Bu kosuda landing/public site degistirilmedi.*
