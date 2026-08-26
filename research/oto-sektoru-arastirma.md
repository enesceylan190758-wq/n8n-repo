# Oto servis sektoru — yorum / musteri deneyimi otomasyonu arama arastirmasi

**Tarih:** 2026-08-26  
**Kapsam:** Turkiye · ozel oto servisler, teknik servisler, yedek parca / servis operasyonlari  
**Tema:** oto servis yorum yonetimi + musteri deneyimi otomasyonu + randevu/bakim hatirlatma  
**Yontem:** Canli web arama / SERP sonuclari + sayfa fetch. Keyword Planner / hacim API'si yok; "en yogun" siralama **sayisal hacim iddiasi degil**, bu oturumda gozlenen **ticari SERP yogunlugu + sorgular arasi tekrar** sinyalidir.

**Kaynak notu:** Web arama arac ciktisi anlik SERP gorunumudur; konum, kisisellestirme ve tarih farki olabilir. People Also Ask kutusu ayri parse edilmedi; alt sorular siralanan sayfalarin SSS/H2 ve urun metinlerinden derlendi.

---

## 1) Yogun ticari sinyalli kelime obekleri (Turkce)

Sira = bu oturumda gozlenen SERP ticari yogunlugu / capraz tekrar (yuksek -> dusuk).

| # | Obek | SERP karakteri | Ornek sorgu |
|---|------|----------------|-------------|
| 1 | `oto servis programi` / `oto servis yazilimi` | Cok sayida SaaS/masaustu servis operasyon yazilimi | `oto servis programi fiyatlari Turkiye` |
| 2 | `oto servis CRM yazilimi` | ESN, Canbus, Mysoft gibi CRM/servis yonetimi sayfalari | `oto servis CRM yazilimi Turkiye` |
| 3 | `oto servis randevu programi` | Randevu + WhatsApp/SMS hatirlatma odakli yazilimlar | `oto servis randevu programi WhatsApp` |
| 4 | `oto servis WhatsApp otomasyon` | OtoCore, Rocketly, Piyzi, Scuto gibi iletisim/CRM oyunculari | `oto servis WhatsApp otomasyon randevu hatirlatma` |
| 5 | `oto servis Google yorum yonetimi` | Jetyorum, Esinix, Piyzi + local SEO ajanslari | `oto servis musteri yorumlari Google yonetimi` |
| 6 | `teknik servis yorum yonetimi` | Teknik servis dikeyinde Jetyorum + local SEO sayfalari | `teknik servisler yorum yonetimi` |
| 7 | `yetkili servis musteri memnuniyet anketi` | CX/NPS icerikleri + akademik calismalar | `yetkili servis musteri memnuniyet anketi otomotiv NPS` |
| 8 | `periyodik bakim hatirlatma yazilimi` | Oto servis CRM ve WhatsApp otomasyon sayfalari | `oto servis periyodik bakim hatirlatma` |
| 9 | `oto servis lokal SEO` / `Google Isletme Profili oto servis` | Ajans hizmet sayfalari | `oto servis yerel SEO Google isletme profili` |
| 10 | `oto servis NPS` / `servis sonrasi NPS` | Staffino gibi CX yazilimlari + genel memnuniyet rehberleri | `otomotiv servis NPS musteri deneyimi` |

**Nefalix gorunurlugu:** `site:nefalix.com oto servis` aramasinda `/blog` icinde oto servis NPS/tekrar ziyaret konulari gorundu; `site:nefalix.com/geo oto servis` icin bu oturumda sonuc bulunmadi. Bu, oto tarafinda blog stoku baslamis olsa da GEO exact-match yuzeyinin henuz zayif oldugunu gosteriyor.

---

## 2) Rakipleri ayirarak kim siralaniyor?

### 2.1 Servis operasyon yazilimi / DMS-ERP benzeri oyuncular

Bu kume oto servislerin cekirdek operasyonunu yonetiyor: arac kabul, is emri, stok, fatura, cari, teknisyen atama, e-fatura/e-arsiv. Nefalix'in yerine gecen bir HBYS/PMS degil; oto sektoru icin benzer sistem kategorisi **servis programi / DMS-ERP**.

| Marka / site | Model | Neden siralaniyor (SERP sinyali) | Kaynak |
|---|---|---|---|
| **Canbus / servisyazilim.com** | Yazilim (bulut oto servis programi) | Arac kabul, is emri, yedek parca/stok, musteri yonetimi, on muhasebe; 30 gun ucretsiz deneme ve public fiyat | [servisyazilim.com](https://servisyazilim.com/), [canbus.net.tr/servis-yazilimi](https://canbus.net.tr/servis-yazilimi/) |
| **OtoServiso** | Yazilim (oto servis programi) | Is emri, teklif, durum takip linki, online randevu, stok/POS/muhasebe modulleri; public fiyat sayfasi | [otoserviso.com/fiyatlar](https://www.otoserviso.com/fiyatlar) |
| **OtoCore** | Yazilim (oto servis yonetimi + WhatsApp) | Randevu, is emri, stok, kasa, WhatsApp, plaka/ruhsat okuma; tek paket fiyat ve 30 gun deneme | [otocore.tr](https://otocore.tr/) |
| **PADOK Bulut / Hayat Yazilim** | Yazilim (bulut + masaustu oto servis programi) | Servis/is emri, ruhsat OCR, cari, stok, fatura, WhatsApp mesajlasma ek modulu | [hayatyazilim.com/padok-bulut](https://hayatyazilim.com/padok-bulut/) |
| **ESN Sistem** | Yazilim (CRM + teknik servis) | Arac bakim gecmisi, musteri kayitlari, parca takibi, e-fatura, mobil saha kaydi; otomotiv sektor sayfasi | [esnsistem.com/urunler/oto-servis-programi](https://www.esnsistem.com/urunler/oto-servis-programi), [esnsistem.com/sektorler/otomotiv](https://www.esnsistem.com/sektorler/otomotiv) |
| **Kursoft** | Yazilim (oto servis programi) | Is emri, ariza kaydi, yedek parca, SMS bilgilendirme, e-fatura/e-arsiv; omur boyu lisans veya yillik kiralama secenegi | [kursoft.com.tr/oto-servis-programi](https://www.kursoft.com.tr/oto-servis-programi/) |
| **Değer Yazılım** | Yazilim / ERP bloglari | Randevu, is emri, stok/parca, rezervasyon, finansal/muhasebe entegrasyonu temali icerikler | [degeryazilim.com/blog/deger-yazilim-oto-servis-cozumleri-ile-atolyenizi-dijitallestirin](https://degeryazilim.com/blog/deger-yazilim-oto-servis-cozumleri-ile-atolyenizi-dijitallestirin) |
| **Caneke** | Icerik / yazilim rehberi | Oto servis yazilimi icin is emri, CRM, durum bilgilendirme ve ucretsiz deneme kriterlerini anlatiyor | [caneke.com.tr/oto-servis-yazilimi](https://caneke.com.tr/oto-servis-yazilimi/) |

**Ortak desen:** Bu oyuncularin ana degeri servis operasyonunu dijitallestirmek. Yorum yonetimi, NPS, kriz alarmi ve AI destekli cevap akisi varsa bile cogunlukla yan modul / blog argumani olarak duruyor.

### 2.2 Yorum / itibar SaaS ve musteri geri bildirim oyunculari

| Marka / site | Model | Neden siralaniyor | Kaynak |
|---|---|---|---|
| **Jetyorum** | Yazilim (yorum toplama, yanitlama, widget) | Oto bayi/servis ve teknik servis landing'leri; Google/sosyal yorum toplama, tek panel, akilli yanitlayici, widget | [jetyorum.com/otomobil-servisleri-bayileri](https://www.jetyorum.com/otomobil-servisleri-bayileri), [jetyorum.com/teknik-servisler](https://www.jetyorum.com/teknik-servisler) |
| **Esinix** | Yazilim (online yorum & itibar yonetimi) | Google/Facebook yorumlarini tek panelde toplama, SMS/WhatsApp yorum talebi, AI yanitlar, olumsuz yorum uyarilari | [esinix.com/itibar-yonetimi](https://esinix.com/itibar-yonetimi) |
| **Piyzi** | Yazilim (Google yorum + oto servis randevu) | Google yorum kazandirma modulu ve oto servis randevu/WhatsApp hatirlatma sayfasi | [piyzi.com/ozellikler/google-yorum-kazandirma](https://piyzi.com/ozellikler/google-yorum-kazandirma), [piyzi.com/sektorler/oto-servis-randevu-programi](https://piyzi.com/sektorler/oto-servis-randevu-programi) |
| **Mysoft CRM** | Genel CRM / anket yonetimi | Anket formu, mail ile anket gonderimi, raporlama, dusuk memnuniyet skorunda otomatik gorev atama | [mysoftcrm.com/anket-yonetimi](https://mysoftcrm.com/anket-yonetimi/), [mysoft.com.tr/neden-crm-kullanilmali](https://www.mysoft.com.tr/neden-crm-kullanilmali) |
| **Staffino** | CX / NPS yazilimi | Otomotiv endustrisi sayfasinda servis, lastik servis ve kaporta temas noktalarinda CSAT/NPS programi ornegi | [staffino.com/tr/otomotiv-endustrisinde-musteri-deneyimi](https://staffino.com/tr/otomotiv-endustrisinde-musteri-deneyimi/) |

**Kritik uyum notu:** Jetyorum, Esinix ve Piyzi sayfalarinda "memnun/mutlu musteriyi Google'a yonlendirme; memnun olmayanlari ozel forma alma" benzeri ifadeler gorunuyor. Google'in resmi Maps UGC politikasi "olumsuz yorumlari caydirma veya yalnizca olumlu yorumlari secici isteme" ve yorum karsiligi tesvik verme pratiklerini yasaklar. Nefalix icerigi bu rakipleri kaynakli anlatabilir, ama bu akisi **onerilen iyi pratik gibi sahiplenmemeli**; tum gercek musterilere adil yorum daveti + ic geri bildirim opsiyonu ayrimini net kurmali. Kaynak: [Google Maps User Generated Content Policy](https://support.google.com/contributionpolicy/answer/7400114?hl=en).

### 2.3 Ajans / local SEO / Google Isletme Profili hizmetleri

| Marka / site | Model | Neden siralaniyor | Kaynak |
|---|---|---|---|
| **Marmara Dijital Medya** | Ajans (oto servis SEO) | Oto servis ve tamir atolyeleri icin lokal gorunurluk, hizmet sayfalari, musteri yorum yonetimi | [marmaradijitalmedya.com/.../oto-servis](https://marmaradijitalmedya.com/hizmetlerimiz/seo-danismanligi/oto-servis) |
| **Nexasignal** | Ajans / danismanlik (local SEO) | GBP, local keyword, NAP, yorum stratejisi ve performans takibi | [nexasignal.com/local-seo-yonetimi](https://nexasignal.com/local-seo-yonetimi/) |
| **Zeisoft** | Ajans (Google Isletme yonetimi) | Google Isletme Profili, yorum talep sureci, spam yorum kaldirma ve Maps sinyalleri | [zeisoft.com/hizmetler/google-isletme-yonetimi](https://zeisoft.com/hizmetler/google-isletme-yonetimi/) |
| **Prisma** | Ajans (GBP + yerel SEO) | Profil optimizasyonu, citation, yorum akisi, coklu lokasyon yonetimi | [prisma.com.tr/google-isletme-profili](https://prisma.com.tr/google-isletme-profili) |
| **Türkal Partners** | Ajans (lokal SEO + Maps) | Oto servisleri dahil fiziksel isletmeler icin GBP, review akisi, lokal landing, citation | [turkalpartners.com/hizmetler/lokal-seo](https://turkalpartners.com/hizmetler/lokal-seo/) |

**Ortak desen:** Ajanslar harita siralamasi, lokasyon sayfalari ve yorum stratejisi satiyor. Nefalix'in farki "ajans hizmeti" degil; servis sonrasi mesaj, NPS, yorum takibi, inbox ve kriz alarmi gibi operasyonel akislari yazilimla surdurmek olmali.

---

## 3) Alt sorular (PAA benzeri + sayfa SSS/H2)

1. Oto servis programi **ne ise yarar**; is emri, stok, fatura ve cari takip tek panelde olur mu? (Canbus, OtoServiso, Hayat Yazilim, Kursoft)
2. Oto servis yazilimi **bulut mu masaustu mu** olmali; internet kesintisi / kalici lisans nasil degerlendirilmeli? (Hayat Yazilim)
3. Randevuya gelmeyen musteri icin **WhatsApp/SMS hatirlatma** nasil kurulur? (OtoCore, Livo, Piyzi)
4. Periyodik bakim zamani gelen araclara **km veya tarih bazli otomatik hatirlatma** gonderilebilir mi? (OtoCore, Rocketly, Piyzi)
5. Servis sonrasi memnuniyet **NPS/CSAT ile nasil olculur**; hangi temas noktasi dusuk puan veriyor? (Staffino, DergiPark otomotiv servis memnuniyeti calismasi)
6. Google yorum daveti gonderirken **review-gating riski** nasil onlenir? (Google Maps UGC politikasi)
7. Google yorum widget'i web sitesinde kullaniliyorsa **dogrulama/uyari** nasil verilmeli? (Plan §4a Reklam Kurulu riski; Jetyorum widget vaadi)
8. Oto servis yazilimi ile yorum/itibar yazilimi **ayni sey mi**? (SERP ayrimi: DMS-ERP vs yorum/itibar SaaS)

---

## 4) Fiyat / ozellik seffafligi (bu oturumda dogrulanan)

| Rakip | Tip | Public fiyat / seffaflik | Kaynak |
|---|---|---|---|
| **Canbus / servisyazilim.com** | Oto servis operasyon yazilimi | Demo ucretsiz; Standart **149 TL/ay**'dan, sinirsiz kullanicili Uzman **249 TL/ay**'dan baslar; sayfada 30 gun deneme ve PayTR odeme notu var | [servisyazilim.com](https://servisyazilim.com/) |
| **OtoServiso** | Oto servis operasyon yazilimi | Profesyonel **999 TL/ay**, Kurumsal **1.599 TL/ay**; KDV dahil; 14 gun ucretsiz; yillik odemede 2 ay hediye | [otoserviso.com/fiyatlar](https://www.otoserviso.com/fiyatlar) |
| **OtoCore** | Oto servis operasyon + WhatsApp | Tek paket: **1.500 TL/ay** veya **15.000 TL/yil** (KDV haric); 30 gun ucretsiz; WhatsApp, plaka okuma ve musteri portali dahil | [otocore.tr](https://otocore.tr/) |
| **PADOK Bulut** | Oto servis operasyon yazilimi | Ana program **990 TL/ay + KDV**; e-fatura +200 TL, stok+barkod +400 TL, WhatsApp mesajlasma +150 TL; ilk 2 kullanici dahil, kullanici basi +390 TL | [hayatyazilim.com/padok-bulut](https://hayatyazilim.com/padok-bulut/) |
| **Kursoft** | Oto servis programi | Public rakam bu oturumda gorulmedi; omur boyu lisans veya yillik kiralama secenekleri oldugu belirtiliyor | [kursoft.com.tr/oto-servis-programi](https://www.kursoft.com.tr/oto-servis-programi/) |
| **ESN Sistem** | CRM + teknik servis yazilimi | Ozellik seffaf; public aylik TL bu oturumda dogrulanmadi | [esnsistem.com/urunler/oto-servis-programi](https://www.esnsistem.com/urunler/oto-servis-programi) |
| **Jetyorum / Esinix / Piyzi** | Yorum/itibar + otomasyon | Ozellik seffaf; oto servis ozel public paket fiyatlari bu oturumda dogrulanmadi | Kaynaklar §2.2 |
| **Nefalix** (karsilastirma) | Yorum + WhatsApp + NPS + kriz alarmi SaaS | Saglik/otel arastirmalarinda kullanilan public fiyat yuzeyi: Baslangic **9.500 TL/ay** + kurulum, Pro **14.900 TL/ay** + kurulum, Kurumsal **45.000 TL+/ay**; oto icin ayri public fiyat bu oturumda dogrulanmadi | [nefalix.com/fiyatlar](https://nefalix.com/fiyatlar) |

**Fiyat yorumu:** Oto operasyon yazilimlari Nefalix'ten belirgin daha dusuk aylik fiyatlarla listeleniyor; bu dogrudan karsilastirma "ucuz/pahali" diye yazilmamali, cunku kapsamlari farkli. Nefalix iceriginde fiyat konumlandirmasi "servis programinin yerine gecmez; servis sonrasi iletisim, yorum, NPS ve kriz katmanini tamamlar" diye ayrilmali.

---

## 5) nefalix.com'da oto servis yuzeyi

Doğrulama: canli web aramasi `site:nefalix.com oto servis` ve `site:nefalix.com/geo oto servis` (2026-08-26).

| Yuzey | Durum |
|---|---|
| `/blog` | Oto servis NPS / tekrar ziyaret temali blog yazilari gorunuyor: "Oto Servislerde NPS ve Tekrar Ziyaret Oranini Artirma..." ve benzeri auto etiketli icerikler |
| `/geo` | Bu oturumda oto servis odakli `/geo` sonucu bulunmadi |
| `/sektorler#oto` | Plan/landing baglaminda sektor hedefi var; bu checkout'ta landing public repo degil |
| `/fiyatlar` | Genel Nefalix fiyat yuzeyi var; oto icin ayri paket/fiyat dogrulanmadi |

### Eksik / zayif (Faz 4 oto GEO seti icin backlog)

| Bosluk | Neden kritik | Onerilen GEO konusu |
|---|---|---|
| Exact-match oto pillar yok | `oto servis yorum yonetimi` ve `oto servis Google yorum` sorgulari Jetyorum/ajanslara gidiyor | `Oto servislerde Google yorum yonetimi nasil yapilir?` |
| Servis programi vs Nefalix ayrimi yok | SERP'te Canbus/OtoServiso/OtoCore operasyon yazilimi baskin; Nefalix farki karisabilir | `Oto servis programi ile itibar yonetimi yazilimi farki nedir?` |
| WhatsApp + NPS akisi GEO yok | Piyzi/OtoCore/Rocketly WhatsApp-randevu dilini sahipleniyor | `Oto servislerde servis sonrasi NPS WhatsApp ile nasil olculur?` |
| Periyodik bakim recall iceriği zayif | Oto servis icin tekrar ziyaret = bakim hatirlatma; Nefalix Recall anlatimina baglanabilir | `Periyodik bakim hatirlatma oto serviste tekrar ziyareti nasil destekler?` |
| Review-gating uyumlu yorum daveti sayfasi yok | Rakiplerde riskli "mutlu musteri Google'a, mutsuz ozel forma" dili var | `Oto servislerde Google yorum daveti review-gating yapmadan nasil kurulur?` |
| Google yorum widget uyarisi yok | Jetyorum widget ve rich snippet vaadi SERP'te gorunuyor; Reklam Kurulu riski plan §4a | `Google yorum widget'i oto servis sitesinde nasil guvenli kullanilir?` |

---

## 6) Konumlandirma cikarimi (oto servis)

- Oto servis SERP'i **saglik ve otelden farkli**: en baskin kume "itibar" degil, **servis operasyon yazilimi**. Alıcı once is emri/stok/fatura/randevu ariyor.
- Yorum/itibar kumesinde Jetyorum ve Esinix gibi genel SaaS'lar, ajans kumesinde local SEO oyunculari var; oto servis odakli "AI itibar + WhatsApp inbox + NPS + kriz alarmi" birlesimi hala zayif gorunuyor.
- Nefalix'in oto icerigi servis programlariyla rekabet eder gibi yazilmamali. Dogru mesaj: **Canbus/OtoServiso/OtoCore servis operasyonunu yonetir; Nefalix servis sonrasi musteri sesi, yorum, NPS, WhatsApp geri donus ve kriz katmanini yonetir.**
- KVKK rol ayrimi: oto servis musteri ve arac/veri surecinde **veri sorumlusu servis**, Nefalix ise yazilim hizmeti icin **veri isleyen** olarak anlatilmali. "KVKK'yi tamamen cozer" gibi kesin garanti dili kullanilmamali.

---

## 7) Director denetimi

**Onay.** Bu arastirma dosyasi answer-first GEO taslagi degil, Faz 1 kaynak dokumanidir; yine de director kapisina gore kontrol edildi:

- Tekrar icerik: Saglik/otel dosyalarinin yapisi korunuyor, sektor bulgulari ve rakip kumeleri farkli.
- Cevap gec gelmesi: Dosya arastirma formatinda; ilk bolumde yontem ve ana sorgu yogunlugu veriliyor.
- Rakip iddialari: Her rakip iddiasi kaynak URL ile baglandi; fiyat rakamlari yalniz public sayfada gorulenlerle sinirli.
- Review-gating: Rakiplerdeki riskli akislari kaynakli risk olarak isaretliyor; Nefalix'e onerilen pratik gibi sunmuyor.
- Widget uyarisi: Jetyorum widget vaadi Reklam Kurulu / dogrulama uyarisi backlog'una alindi.
- KVKK: Veri sorumlusu = oto servis, veri isleyen = Nefalix ayrimi acik.
- Kaynaksiz istatistik: Staffino ve DergiPark gibi kaynaklar isimlendirildi; sayisal hacim iddiasi yok.

---

## 8) Kaynak logu

- `oto servis CRM yazilimi Turkiye Canbus Mysoft Caneke Değer Yazılım ESN Sistem`
- `oto servis musteri deneyimi yazilimi Google yorum yonetimi Turkiye`
- `oto servis programi fiyatlari Turkiye servis takip is emri stok fatura`
- `yetkili servis musteri memnuniyet anketi otomotiv NPS Turkiye`
- `oto servis WhatsApp otomasyon randevu hatirlatma musteri takip`
- `Mysoft oto servis programi fiyat musteri memnuniyet anketi`
- `Caneke oto servis yazilimi fiyat ozellik is emri musteri takip`
- `Değer Yazılım oto servis programi fiyat is emri stok fatura`
- `Google Business Profile review gating incentives policy reviews Turkey`
- `site:nefalix.com oto servis Nefalix geo blog fiyatlar sektorler`
- `site:nefalix.com/geo oto servis NPS tekrar ziyaret auto`
- Fetch / result kaynaklari: Canbus, OtoServiso, OtoCore, PADOK Bulut, ESN Sistem, Kursoft, Değer Yazılım, Caneke, Jetyorum, Esinix, Piyzi, Mysoft, Staffino, DergiPark, Marmara Dijital Medya, Nexasignal, Zeisoft, Prisma, Türkal Partners, Google Maps UGC Policy.

---

*Sonraki plan parcasi: Faz 4 otel GEO seti (otel arastirmasi hazir) veya oto GEO seti icin bu dosyadan brief uretimi.*
