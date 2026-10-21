# Oto servis sektoru - yorum / musteri deneyimi otomasyonu arama arastirmasi

**Tarih:** 2026-08-06  
**Kapsam:** Turkiye - ozel oto servis, tamirhane, oto ekspertiz, yetkili servis / bayi servis agi  
**Tema:** oto servis CRM + Google yorum yonetimi + WhatsApp / SMS bilgilendirme + musteri memnuniyeti  
**Yontem:** Canli web arama / SERP + sayfa fetch. Keyword Planner / Ahrefs hacim API'si yok; "en yogun" siralama = bu oturumda gozlenen **SERP ticari yogunlugu + sorgular arasi tekrar**. Sayisal hacim iddiasi yapilmaz.  
**Plan referansi:** `docs/nefalix-seo-geo-ajan-plani.md` bolum 2.3 - Faz 1 (saglik ve otel arastirmasi sonrasi oto servis).

---

## 1) Yogun ticari sinyalli kelime obekleri (Turkce)

Sira = bu arastirmada gozlenen SERP ticari yogunlugu / capraz tekrar (yuksek -> dusuk). Bu tablo arama hacmi tahmini degildir.

| # | Obek | SERP karakteri | Ornek sorgu |
|---|------|----------------|-------------|
| 1 | `oto servis programi` / `oto servis yonetim yazilimi` | Bulut servis yazilimi, is emri, stok, fatura ve randevu urun sayfalari | `oto servis programi fiyat 2026` |
| 2 | `oto servis CRM yazilimi` | CRM/ERP ve sektor modulu sayfalari; servis sonrasi takip yan ozellik | `oto servis CRM yazilimi musteri takip` |
| 3 | `oto servis randevu programi` | Randevu + is emri + arac gecmisi; Piyzi/OtoCore/OtoServiso tipi SaaS | `oto servis randevu programi WhatsApp` |
| 4 | `oto servis WhatsApp otomasyon` | Randevu hatirlatma, arac hazir bildirimi, bakim zamani mesaji | `oto servis WhatsApp otomasyon randevu hatirlatma` |
| 5 | `oto servis Google yorum yonetimi` | Ajans blogu + yorum toplama SaaS + QR/widget araclari | `oto servis Google yorum yonetimi` |
| 6 | `yetkili servis musteri memnuniyet anketi` | Deneyim yonetimi SaaS, akademik PDF, NPS/CSAT icerikleri | `yetkili servis musteri memnuniyet anketi NPS` |
| 7 | `oto ekspertiz yazilimi` / `oto ekspertiz CRM` | Ekspertiz raporu + WhatsApp PDF + randevu/stok yazilimlari | `oto ekspertiz yazilimi fiyat` |
| 8 | `periyodik bakim hatirlatma yazilimi` | Oto servis programlarinin recall/hatirlatma ozelligi | `oto servis periyodik bakim hatirlatma` |
| 9 | `arac hazir SMS bildirimi` | SMS/NetGSM veya WhatsApp destekli servis programi ozelligi | `oto servis arac hazir SMS` |
| 10 | `oto servis itibar yonetimi` | Ajans icerigi ve genel yorum yonetimi SaaS; exact-match yazilim az | `otomotiv servis yorum yonetimi` |

**Nefalix gorunurlugu:** `nefalix oto servis musteri deneyimi Google yorum WhatsApp` sorgusunda ust sonuclar Net Oto Servis / Nerex gibi servis isletmeleri ve yorum sayfalari cikardi; Nefalix'in oto servis temasinda marka disi SERP gorunurlugu bu oturumda dogrulanmadi.

---

## 2) Kim siralaniyor? (ornek SERP'ler)

### 2.1 `oto servis programi` / `oto servis yonetim yazilimi`

| # | Marka / site | Model | Neden siralaniyor |
|---|--------------|-------|-------------------|
| 1 | **OtoCore** - [otocore.tr](https://otocore.tr/) | Yazilim (bulut oto servis SaaS) | Randevu, is emri, stok, cari, WhatsApp, musteri portali ve plaka/ruhsat AI tek paket; fiyat sayfada gorunur |
| 2 | **OtoServiso** - [otoserviso.com](https://www.otoserviso.com/) | Yazilim (bulut servis programi) | Is emri, teklif, arac bakim takibi, SMS bildirimleri, GIB e-arsiv entegrasyonu |
| 3 | **Mekaniq** - [mekaniq.com.tr](https://mekaniq.com.tr/) | Yazilim (bulut oto servis programi) | Musteri/arac karti, stok, fatura, WhatsApp bildirimleri; ucretsiz paket limiti public |
| 4 | **Canbus** - [canbus.net.tr](https://canbus.net.tr/servis-programi/) / [caneke.com.tr](https://caneke.com.tr/canbus-otomotiv-yazilimlari/) | Yazilim (teknik servis / yedek parca / ekspertiz) | Bulut tabanli yerli servis yazilimi, musteri-arac-stok-fatura akisi |
| 5 | **DIA / Indemsoft / Infinity** | ERP veya kurulumlu servis programi | "Oto servis programi nedir" ve fiyat/ozellik rehberleriyle kategori sorgularini dolduruyor |

### 2.2 `oto servis CRM yazilimi` / `yetkili servis CRM`

| # | Marka / site | Model | Neden siralaniyor |
|---|--------------|-------|-------------------|
| 1 | **ESN Sistem** - [esnsistem.com/sektorler/otomotiv](https://www.esnsistem.com/sektorler/otomotiv) | ERP + CRM + saha servis | Otomotiv servis, yedek parca, filo bakim icin sektor landing; lisans modul/kullaniciya gore |
| 2 | **Otosoft** - [otosoft.com.tr](https://otosoft.com.tr/otosoft-kurumsal-arac-satis-servis-yazilimi/) | Kurumsal bayi/servis ERP | 2S (satis + servis) bayi operasyonu, CRM, servis sonrasi memnuniyet anketi |
| 3 | **Mysoft CRM** - [mysoftcrm.com/anket-yonetimi](https://mysoftcrm.com/anket-yonetimi/) | Genel CRM + anket modulu | Anket formu, mail ile gonderim, skor bazli otomatik gorev akislarini anlatir; oto servis dikeyi degil |
| 4 | **Pisano** - [pisano.com/tr/sektorel-cozumler/otomotiv](https://www.pisano.com/tr/sektorel-cozumler/otomotiv) | Deneyim yonetimi SaaS | Otomotiv satis/servis ekipleri icin NPS, CSAT, hizmet verimliligi metrikleri |
| 5 | **Staffino** - [staffino.com/tr/otomotiv-endustrisinde-musteri-deneyimi](https://staffino.com/tr/otomotiv-endustrisinde-musteri-deneyimi/) | CX / NPS platformu | Motor-Car ornegiyle servis/lastik/kaporta temas noktalarinda CSAT ve NPS toplama |

### 2.3 `oto servis Google yorum yonetimi`

| # | Marka / site | Model | Neden siralaniyor |
|---|--------------|-------|-------------------|
| 1 | **Kobimedya** - [kobimedya.com/blog/otomotiv-servis-yorum-yonetimi](https://kobimedya.com/blog/otomotiv-servis-yorum-yonetimi) | Ajans / itibar blogu | Oto servis icin tek kotu yorumun telefon trafigine etkisini anlatan sektor odakli icerik |
| 2 | **Jetyorum** - [jetyorum.com/otomobil-servisleri-google-isletme](https://www.jetyorum.com/otomobil-servisleri-google-isletme) | Yorum toplama / widget SaaS | Otomobil servisleri icin Google yorum faydalari ve deneyim geri bildirim dongusu |
| 3 | **Piyzi** - [piyzi.com/ozellikler/google-yorum-kazandirma](https://piyzi.com/ozellikler/google-yorum-kazandirma) | Yazilim (Google yorum otomasyonu) | Randevu tamamlandiktan sonra yorum linki gonderimi, filtreleme ve raporlama anlatimi |
| 4 | **Notet** - [notet.net/google-yorum-talebi](https://notet.net/google-yorum-talebi) | Yorum / itibar otomasyonu | Randevu sonrasi memnuniyet anketi, dusuk sinyali ic ekibe tasima, Google yonlendirme |
| 5 | **Akilli Isler** - [akilliisler.com](https://akilliisler.com/) | Genel AI yorum yanit SaaS | Google/Tripadvisor/Yemeksepeti yorum analizi ve cevap taslagi; otomotiv dikeyi genel liste icinde |

**Uyum notu:** Piyzi, Jetyorum ve Notet gibi sayfalarda "memnun musteriyi Google'a tasima" dili goruluyor. Nefalix icerikleri bu noktada secici yorum davetini ovmemeli; yorum daveti gonullu, tesviksiz ve tum uygun temas noktalarina adil sekilde tasarlanmalidir.

### 2.4 `oto servis WhatsApp otomasyon`

| # | Marka / site | Model | Neden siralaniyor |
|---|--------------|-------|-------------------|
| 1 | **OtoCore** | Yazilim | Randevu hatirlatma, bakim zamani, kampanya ve arac hazir bilgilendirmesini WhatsApp ile anlatir |
| 2 | **OtoServiso** | Yazilim | NetGSM SMS bildirimi ve arac hazir/randevu mesajlari; WhatsApp yerine SMS vurgusu daha net |
| 3 | **OnarMatik / Tera Sistem** - [terasistem.com](https://www.terasistem.com/onarmatik-oto-servis-takip-programi/) | Yazilim | Randevu, PDF, WhatsApp ve SMS paylasim destegi |
| 4 | **GarageBox** - [garagebox.io/tr](https://www.garagebox.io/tr) | Global garaj yonetim yazilimi | SMS, e-posta veya WhatsApp ile randevu/tahmin/denetim guncellemeleri |
| 5 | **OTO help** - [help.tryoto.com](https://help.tryoto.com/tr/support/solutions/articles/150000198518-whatsapp-business-entegrasyonu) | Lojistik / operasyon platformu entegrasyon dokumani | WhatsApp Business API kurulum mantigini anlatan kaynak; oto servis dikeyi degil |

### 2.5 `oto ekspertiz yazilimi`

| # | Marka / site | Model | Neden siralaniyor |
|---|--------------|-------|-------------------|
| 1 | **Ekspertiz.app** - [ekspertiz.app](https://ekspertiz.app/) | Yazilim (ekspertiz SaaS) | QR dogrulamali PDF rapor, WhatsApp ile rapor gonderimi, net fiyat |
| 2 | **OtoEkspertizYazilim.com** - [otoekspertizyazilim.com](https://www.otoekspertizyazilim.com/) | Yazilim | Paket fiyatlari, sinirsiz rapor, kredi karti taksit, demo |
| 3 | **OzgurKod** - [ozgurkod.com/cozumler/oto-ekspertiz](https://ozgurkod.com/cozumler/oto-ekspertiz) | CRM / sektor modulu | WhatsApp, Instagram ve web mesajlarini tek panelde toplama; randevu/teklif/tahsilat |
| 4 | **EksperJet** - [eksperjet.com.tr](https://eksperjet.com.tr/oto-ekspertiz-programi/) | Yazilim / sektor icerigi | Ekspertiz raporu, musteri bilgisi, randevu, CRM faydasi |

---

## 3) Alt sorular (PAA benzeri + siralanan sayfa SSS/H2)

People Also Ask kutusu bu aracta ayri parse edilmedi. Asagidakiler siralanan sayfa SSS/H2, fiyat sayfasi ve akademik kaynak tekrarlarindan derlendi.

1. Oto servis programi defter/Excel yerine hangi akislari tek panelde toplar? (OtoCore, OtoServiso, Canbus, DIA)
2. Randevu, is emri, stok ve fatura ayni sistemde olmali mi? (OtoServiso, Indemsoft, Infinity)
3. Arac hazir bildirimi SMS mi WhatsApp mi gitmeli; resmi WhatsApp API gerekir mi? (OtoCore, OnarMatik, OTO help)
4. Periyodik bakim veya vade/garanti hatirlatmasi musteri geri kazanimi icin nasil calisir? (OtoCore, Infinity)
5. Google yorum daveti ne zaman gonderilmeli ve tesvik/review-gating riski nasil onlenmeli? (Piyzi, Jetyorum, Kobimedya + Google politika riski)
6. Yetkili servislerde memnuniyet anketi hangi metriklerle okunur: NPS, CSAT, CES? (Pisano, Staffino, DergiPark)
7. Oto ekspertiz raporu WhatsApp ile gonderildiginde CRM kaydi nasil tutulur? (Ekspertiz.app, OzgurKod)

---

## 4) Rakiplerde fiyat / ozellik seffafligi (somut rakam + kaynak)

| Rakip | Tip | Public fiyat / paket | Kaynak |
|-------|-----|----------------------|--------|
| **OtoCore** | Yazilim (oto servis SaaS) | Yillik liste **15.000 TL + KDV**; yeni versiyon ozel **12.500 TL**; iki yillik **20.000 TL**; 30 gun deneme | [otocore.tr](https://otocore.tr/) |
| **OtoServiso** | Yazilim (oto servis SaaS) | Fiyat sayfasinda **999 TL/ay** Profesyonel ve **1.599 TL/ay** Kurumsal (KDV dahil); blog/fiyat rehberinde farkli **1.999 / 2.999 TL** metni de goruldu -> guncel fiyat icin fiyat sayfasi esas alinmali | [otoserviso.com/fiyatlar](https://www.otoserviso.com/fiyatlar) |
| **OtoServisYazilimi.com** | Yazilim | **239 / 479 / 799 TL/ay**; yillik faturalandirma **2.868 / 5.748 / 9.588 TL** | [otoservisyazilimi.com](https://otoservisyazilimi.com/) |
| **Indemsoft Oto Servis Programi** | Kurulumlu / paket yazilim | Sayfada **21.000 TL** liste fiyat goruldu | [indemsoft.com](https://www.indemsoft.com/programlar/11/oto-servis-programi.html) |
| **Ekspertiz.app** | Ekspertiz SaaS | **6.900 TL/ay + KDV**; yillik **69.000 TL/yil** (5.750 TL/ay denk); 14 gun deneme | [ekspertiz.app](https://ekspertiz.app/) |
| **OtoEkspertizYazilim.com** | Ekspertiz yazilimi | Paketlerde **500 / 750 / 1.500 TL** ve toplu sure paketleri; sayfa para birimi TL | [otoekspertizyazilim.com](https://www.otoekspertizyazilim.com/) |
| **Akilli Isler** | Genel AI yorum yanit SaaS | **490 TL/ay** ve **990 TL/ay** planlar; kurumsal ozel | [akilliisler.com](https://akilliisler.com/) |
| **ESN Sistem** | ERP + CRM + saha servis | Sabit fiyat yok; lisans bedeli kullanici sayisi ve modul secimine gore, fiyat icin iletisim | [esnsistem.com/sektorler/otomotiv](https://www.esnsistem.com/sektorler/otomotiv) |
| **Canbus** | Oto servis / yedek parca / ekspertiz yazilimi | Bu oturumda public fiyat kesin dogrulanmadi; 1 ay ucretsiz deneme sayfada | [canbus.net.tr](https://canbus.net.tr/servis-programi/) |
| **Piyzi** | Randevu + Google yorum otomasyonu | Bu oturumda oto servis sayfasinda fiyat dogrulanmadi; ucretsiz deneme / kredi kartsiz baslama dili var | [piyzi.com](https://piyzi.com/en/sektorler/oto-servis-randevu-programi) |
| **Nefalix** (karsilastirma) | Yazilim (yorum + WhatsApp/inbox + NPS + recall + kriz alarmi) | Baslangic **9.500 TL/ay** + **25.000 TL** kurulum; Pro **14.900 TL/ay** + **50.000 TL** kurulum; Kurumsal **45.000 TL+/ay**; Sentinel **+3.500 TL/ay**, Recall **+2.500 TL/ay** | [nefalix.com/fiyatlar](https://nefalix.com/fiyatlar) |

**Gozlem:** Oto servis SERP'inde fiyat seffafligi saglik ve otel arastirmalarina gore daha yuksek. OtoCore, OtoServiso, OtoServisYazilimi.com, Indemsoft ve ekspertiz yazilimlari rakami acik veriyor. Nefalix'in oto servis icerigi uretilecekse "daha ucuz/pahali" iddiasi yerine **hangi katmani sattigi** net ayrilmali: servis ERP'si degil, itibar + geri bildirim + mesaj / recall operasyon katmani.

---

## 5) Rakipleri ayir: yazilim / ajans / servis-ERP

| Kategori | Ornekler | Nefalix icin konumlandirma notu |
|----------|----------|---------------------------------|
| **Servis ERP / oto servis programi** | OtoCore, OtoServiso, Mekaniq, Canbus, Indemsoft, Infinity, DIA, ESN, Otosoft | Randevu, is emri, stok, fatura, arac gecmisi ana odak. Nefalix bunlarin yerine gecmez; teslimat sonrasi geri bildirim, yorum, NPS, WhatsApp/inbox ve recall katmani olarak konumlanmali. |
| **Yorum / itibar SaaS** | Piyzi Google yorum, Jetyorum, Notet, Akilli Isler | Yorum talebi ve yanit otomasyonu yakin komsu kategori. Review-gating ve tesvik dili dikkatle ayiklanmali. |
| **Deneyim yonetimi / NPS** | Pisano, Staffino, Mysoft anket modulu | Yetkili servis ve bayi aginda NPS/CSAT ihtiyaci var; ozel servislerde daha cok pratik "arac hazir, memnuniyet, tekrar bakim" dili calisiyor. |
| **Ajans / icerik** | Kobimedya otomotiv servis yorum yonetimi blogu | Exact-match itibar icerigini ajanslar dolduruyor; Nefalix'in yazilim sayfasi bu sorguda henuz gorunmuyor. |
| **Gercek servis / yorum vitrinleri** | Net Oto Servis, Nerex, VosvosPark | SERP'te isletme yorum sayfalari da cikiyor. Google yorum widget'i kullaniliyorsa kaynak/dogrulama uyarisi ve guncel puan tutarliligi sart. |

---

## 6) nefalix.com'da oto servis yuzeyi

Bu checkout public landing repo degil; bu oturumda canli siteye kod degisikligi yapilmadi. Web aramasinda Nefalix'in oto servis temali marka disi SERP gorunurlugu dogrulanmadi.

| Yuzey | Durum |
|-------|-------|
| `/sektorler#oto` veya oto servis sektor bolumu | Plan Nefalix'in oto servisleri hedefledigini soyler; bu checkout'ta landing dosyasi yok, canli icerik degistirilmedi |
| `/geo` oto servis paketleri | Bu repo icinde mevcut `geo/*.md` dosyalari saglik odakli; oto servis GEO dosyasi yok |
| `/blog` oto servis icerigi | Bu oturumda canli blog API listesi cekilmedi; onceki gap notunda sektor bazli eksik otel/oto olarak duruyor |
| `/fiyatlar` | Nefalix public fiyatlari saglik arastirmasinda kaynaklanmis; oto karsilastirmada fiyat yazilacaksa ayni URL kaynak verilmeli |

### Eksik / zayif (Faz 4 oto icin backlog)

- `oto servis yorum yonetimi yazilimi` exact-match GEO
- `oto servis WhatsApp otomasyon ve arac hazir bildirimi` GEO
- `oto servis programi ile itibar yazilimi farki` karsilastirma sayfasi
- `yetkili servis NPS / CSAT takip yazilimi` GEO
- `periyodik bakim recall otomasyonu` oto servis GEO
- Piyzi / OtoCore / OtoServiso / Akilli Isler gibi rakipleri ayiran adil karsilastirma brief'i

---

## 7) Nefalix konumlandirma cikarimi (oto servis)

- Oto servis SERP'i **servis ERP / is emri / stok / fatura** odakli yazilimlarla dolu; bu alan Nefalix'in dogrudan ikame alani degil.
- En yakin bosluk: teslimat sonrasi **musteri geri bildirimi + Google yorum disiplini + WhatsApp/inbox + periyodik bakim recall + kriz alarmi** katmanini servis ERP'sinin ustune baglamak.
- Ozel servislerde "NPS" terimi daha zayif; "arac tesliminden sonra memnuniyet", "arac hazir bildirimi", "periyodik bakim hatirlatma", "olumsuz yorum alarmi" dili daha dogal.
- Yetkili servis / bayi aginda Pisano ve Staffino gibi CX platformlari NPS/CSAT dilini tasiyor; Nefalix bu segmente girecekse lokasyon bazli skor, ekip gorevi ve bayi merkezi raporu gerekir.
- Review-gating riski yuksek: "memnun musterilere yorum daveti" ifadesi pazarlama metninde kolayca politika riski dogurur. Nefalix icerikleri tesvik, hediye veya secici olumlu davet imasi kurmamalidir.
- Google yorum widget'i anlatilacaksa VosvosPark ornegindeki gibi "Google'in izin verdigi sinir / tum yorumlar icin profil linki" turu dogrulama uyarisi gerekir; aksi Reklam Kurulu ve yaniltici yorum vitrini riski vardir.

---

## 8) Director / uyum kapisi

**Onay - arastirma dosyasi.** Gerekce: Kaynak URL'leri yazildi; rakip fiyat/ozellik iddialari yalnizca SERP/fetch ciktisinda gorulen bilgilerle sinirlandi; hacim iddiasi yapilmadi; rakipler yazilim / ajans / ERP / CX olarak ayrildi; review-gating ve Google yorum widget riskleri acikca uyarildi; KVKK rol ayrimi kesin hukuki garanti gibi sunulmadi.

---

## 9) Kaynak logu

- `oto servis musteri deneyimi yazilimi Turkiye oto servis CRM Google yorum yonetimi`
- `oto servis CRM yazilimi fiyat randevu is emri musteri memnuniyeti Turkiye`
- `oto servis Google yorum yonetimi musteri memnuniyet anketi yetkili servis`
- `oto servis WhatsApp otomasyon randevu hatirlatma yazilimi`
- `oto servis programi Canbus Mysoft Caneke Deger Yazilim ESN Sistem fiyat ozellik`
- `Mysoft oto servis programi musteri memnuniyet anketi fiyat`
- `Deger Yazilim oto servis programi fiyat ozellik`
- `yetkili servis musteri memnuniyet anketi otomotiv yazilimi Turkiye NPS`
- `oto ekspertiz yazilimi musteri takip Google yorum otomasyon Turkiye fiyat`
- `nefalix oto servis musteri deneyimi Google yorum WhatsApp`
- Fetch / SERP kaynaklari: OtoCore, OtoServiso, Mekaniq, Piyzi, Kobimedya, Jetyorum, Notet, Canbus, ESN Sistem, Otosoft, Mysoft CRM, Deger Yazilim, Indemsoft, Infinity, DIA, Pisano, Staffino, DergiPark, Ekspertiz.app, OtoEkspertizYazilim.com, OzgurKod, Nerex, VosvosPark.

---

*Dosya yolu: `research/oto-sektoru-arastirma.md` - Bu kosuda landing repo yok; canli deploy iddiasi yok.*
