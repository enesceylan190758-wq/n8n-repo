# Oto servis sektoru - servis deneyimi / yorum yonetimi otomasyonu arama arastirmasi

**Tarih:** 2026-09-07
**Kapsam:** Turkiye · oto servis, oto tamir, kaporta-boya, lastik servisi, otomobil bayi/servis isletmeleri
**Tema:** oto servis musteri deneyimi + Google yorum yonetimi + WhatsApp/randevu/servis takip otomasyonu
**Yontem:** Canli web arama / SERP sonuclari + sayfa fetch. Keyword Planner / Ahrefs hacim API'si yok; "en yogun" siralama **sayisal arama hacmi degil**, ayni oturumda gozlenen **SERP ticari yogunlugu + sorgular arasi tekrar** sinyalidir. Hacim iddiasi yapilmaz.
**Plan referansi:** `docs/nefalix-seo-geo-ajan-plani.md` §2.3 ve `docs/nefalix-seo-geo-gap-notes.md` Faz 1.

**Siradaki faz karari:** Gap notes'a gore Faz 0 teknik indeks sorunu kapanmis, saglik ve otel arastirmalari hazir, saglik GEO seti tamamlanmis. Bu checkout'ta `research/oto-sektoru-arastirma.md` olmadigi icin bu kosunun ana teslimati **Faz 1 oto servis arastirmasini tamamlamak**; bundan sonraki pratik faz **Faz 4 otel GEO seti**, ardindan bu dosyaya dayali oto GEO setidir.

---

## 1) Yogun ticari sinyalli 10 kelime obegi (Turkce)

Sira = bu arastirmada gozlenen SERP ticari yogunlugu / capraz tekrar. Sayisal arama hacmi degildir.

| # | Obek | SERP karakteri | Ornek sorgu kaynagi |
|---|------|----------------|---------------------|
| 1 | `oto servis programi` / `oto servis yazilimi` | Servis/garaj yonetim yazilimlari; fiyat sayfalari ve 30 gun deneme CTA'lari | `oto servis programi is emri musteri takip WhatsApp yorum talebi fiyat` |
| 2 | `oto servis CRM` / `oto servis CRM yazilimi` | CRM + WhatsApp + pipeline urun sayfalari | `oto servis CRM yazilimi randevu WhatsApp musteri memnuniyet anketi` |
| 3 | `oto servis randevu programi` | Randevu, Google Takvim, hatirlatma, servis kabul akislarina odakli sayfalar | ayni sorgu kumesi |
| 4 | `oto servis musteri memnuniyet anketi` | NPS/anket modulu olan servis yazilimlari ve bloglar | `oto servis yazilimi musteri memnuniyet anketi NPS` |
| 5 | `oto servis WhatsApp otomasyon` | WhatsApp durum bildirimi, parca onayi, bakim hatirlatma, takim inbox | `oto servis CRM WhatsApp randevu` |
| 6 | `oto servis Google yorum yonetimi` | Genel Google yorum/itibar SaaS'lari + otomotiv sayfalari | `oto servis Google yorum yonetimi yazilimi itibar yonetimi` |
| 7 | `arac servis takip yazilimi` / `servis takip yazilimi` | Is emri, stok, fatura, cari, musteri takip | `oto servis programi is emri musteri takip` |
| 8 | `oto servis NPS` / `servis sonrasi NPS` | Kurumsal paketlerde NPS dashboard; ESN Sistem bloglari | `oto servis yazilimi NPS musteri memnuniyet` |
| 9 | `Google yorum talebi oto servis` | Yorum daveti, QR/WhatsApp ve policy riski olan yonlendirme akislarini cikariyor | `oto servis Google yorum yonetimi` |
| 10 | `oto bayi yorum yonetimi` | Jetyorum gibi otomobil bayisi/servis geliri odakli yorum toplama sayfalari | `oto bayinizi musteri yorumlari ile one cikarin` |

**Nefalix gorunurlugu:** Bu oturumda incelenen oto servis niyetli sorgularda nefalix.com ust sonuclarda gorunmedi; SERP yuzeyi servis yonetim yazilimlari, CRM/inbox araclari ve genel yorum yonetimi platformlari tarafindan dolduruluyor.

---

## 2) Kelime obeklerinde kim siralaniyor? (marka + model + neden)

### 2.1 `oto servis programi` / `oto servis yazilimi`

| Marka / site | Model | Neden siralaniyor |
|---|---|---|
| **Canbus** - [servisyazilim.com](https://servisyazilim.com/) | Servis/garaj yonetim yazilimi | Arac kabul, is emri, yedek parca/stok, musteri CRM, on muhasebe ve SMS bilgilendirme tek sayfada; fiyat bolumu acik. |
| **Bulut Oto Servis Yazilimi** - [bulutotoservis.com](https://bulutotoservis.com/) | Servis yonetim yazilimi | Is emri, stok, e-fatura, raporlama, SMS/WhatsApp belge paylasimi; Kurumsal pakette NPS/memnuniyet anketi anlatimi. |
| **OtoCore** - [otocore.tr](https://otocore.tr/) | Servis yonetim yazilimi | Randevu, is emri, musteri/arac kayitlari, stok, kasa, WhatsApp mesajlari ve musteri portali tek panel vaadi. |
| **ServisDefteri** - [servisdefteri.tr](https://servisdefteri.tr/) | Servis takip yazilimi | Is emri, stok, kasa, randevu, WhatsApp bildirimi, musteri takip linki ve AI ariza/rapor taslagi; fiyat acik. |
| **Carzi** - [carzi.com.tr](https://carzi.com.tr/) | Oto servis/stok yonetim sistemi | Servis, stok, tahsilat, personel primi ve akilli asistan; yillik paket fiyatlari ve ek hizmet fiyatlari acik. |
| **OtoServiso** - [otoserviso.com/fiyatlar](https://www.otoserviso.com/fiyatlar) | Oto servis programi | Fiyat karsilastirma sayfasi SERP'te gorundu; Profesyonel/Kurumsal paket, kullanici sayisi ve ozellik matrisi acik. |

**Ortak desen:** Bu kume Nefalix'in birebir yerine gecen rakipleri degil; servis operasyonunun cekirdegini (is emri, stok, fatura, cari, randevu) tasiyor. Nefalix icin konumlama cumlesi: "garaj/servis programinin yerine gecmez; yorum, WhatsApp, NPS ve kriz sinyallerini bu operasyonun ustune musteri deneyimi katmani olarak ekler."

### 2.2 `oto servis CRM` / WhatsApp pipeline

| Marka / site | Model | Neden siralaniyor |
|---|---|---|
| **Rocketly** - [gorocketly.com/sektorler/oto-servis](https://gorocketly.com/sektorler/oto-servis) | CRM + AI inbox | WhatsApp, Instagram ve web formundan gelen mesajlari tek inbox'ta toplama; servis pipeline, randevu, teklif ve periyodik bakim hatirlatmasi. |
| **OzgurKod** - [ozgurkod.com/cozumler/oto-servis](https://ozgurkod.com/cozumler/oto-servis) | AI destekli CRM / servis surec takibi | "Aracim ne durumda?" sorulari, parca onayi, WhatsApp/SMS hatirlatma, Google Takvim senkronu ve pipeline anlatimi. |
| **Piyzi** - [piyzi.com/sektorler/oto-servis-randevu-programi](https://piyzi.com/sektorler/oto-servis-randevu-programi) | Oto servis randevu + bakim takip | Meta Tech Provider olarak WhatsApp Business; randevu oncesi/sonrasi iletisim, bakim hatirlatma ve Google yorum talebi. |
| **Rapitek** - [rapitek.com/oto-servis-crm](https://rapitek.com/oto-servis-crm/) | CRM + WhatsApp Business API | 5-500 kullanicili oto servis ekipleri, WhatsApp Business API/QR esleme, Logo/SAP/Netsis/Mikro entegrasyonlari, hazir oto servis workflow'lari. |

**Ortak desen:** Bu kume Nefalix'e daha yakin; musteri iletisim katmanini ve WhatsApp operasyonunu sahipleniyor. Fark alani: Nefalix'in "yorum + WhatsApp + NPS + kriz alarmi + recall" paketini tek itibar/musteri deneyimi operasyonu olarak anlatmasi gerekir.

### 2.3 `oto servis Google yorum yonetimi` / itibar SaaS

| Marka / site | Model | Neden siralaniyor |
|---|---|---|
| **Jetyorum** - [jetyorum.com/otomobil-servisleri-bayileri](https://www.jetyorum.com/otomobil-servisleri-bayileri) | Yorum toplama + itibar yazilimi | Otomobil bayileri/servisleri icin yorum toplama, widget/API ile yorumlari siteye tasima, CRM/ERP entegrasyonu ve AI yorum analizi anlatimi. |
| **Akilli Isler** - [akilliisler.com](https://akilliisler.com/) | Genel AI itibar yonetimi SaaS | Google, Tripadvisor, Yemeksepeti ve diger platformlari baglama; AI analiz/yanit; onayli veya otomatik mod; kriz erken uyari. |
| **YorumTopla** - [yorumtopla.com](https://yorumtopla.com/) | Google profil analizi + yorum yonetimi | QR/WhatsApp daveti, uygulamasiz geri bildirim, Google yorumlari, AI taslaklari; "her puana ayni deneyim" ve "esit Google paylasimi" uyum dili. |
| **Cevaply** - [cevaply.com](https://cevaply.com/) | Yorum yonetim platformu | Google ve TripAdvisor hesaplarini tek panelde gorme; dusuk puanlari one cikarma; AI taslagi kontrol ederek yayinlama. |
| **Sparkavis** - [sparkavis.app/tr](https://sparkavis.app/tr) | Google Business Profile yorum uygulamasi | Google yorumlarina AI ile yanit, mobil yonetim, otomatik yanit ve web sitesinde dogrulanmis Google yorumlarini gosterme iddiasi. |
| **Esinix** - [esinix.com/itibar-yonetimi](https://esinix.com/itibar-yonetimi) | Genel online itibar yonetimi | Google/Facebook yorum paneli, otomatik yorum talebi, AI yanit ve olumsuz yorum uyarisi anlatimi. |

**Policy riski:** Jetyorum'un otomobil servisleri sayfasi "sadece mutlu musterileri yorum birakma surecine yonlendirin" ifadesini, Esinix sayfasi ise "memnun musteriler Google'a, memnun olmayanlar ozel form'a" akislarini anlatir. Bu tur secici yonlendirme, Google yorum politikasi acisindan review-gating algisi dogurur; Nefalix iceriginde boyle bir akis ovulmemeli.

---

## 3) Alt sorular (PAA benzeri + sayfa SSS/H2 tekrarlarindan)

People Also Ask kutusu arac ciktisinda ayri parse edilmedi. Asagidaki sorular siralanan urun sayfalarinin SSS/H2 tekrarlarindan ve SERP niyetinden derlendi:

1. Oto servis programi ile oto servis CRM ayni sey mi?
   - Canbus/Bulut Oto Servis/ServisDefteri "is emri, stok, cari, fatura" cekirdegini anlatirken Rocketly/OzgurKod/Rapitek "WhatsApp, inbox, randevu, teklif, pipeline" katmanina odaklaniyor.
2. Oto serviste musterinin "aracim ne durumda?" sorusu nasil otomatiklestirilir?
   - OzgurKod, ServisDefteri, Bulut Oto Servis ve Carzi durum bildirimi, takip linki veya WhatsApp belge/paylasim akislarini one cikariyor.
3. Periyodik bakim hatirlatmasi WhatsApp veya SMS ile nasil calisir?
   - Rocketly, Piyzi, ServisDefteri ve Bulut Oto Servis km/tarih bazli hatirlatma veya randevu bildirimi anlatir.
4. Servis sonrasi memnuniyet anketi / NPS nasil gonderilir?
   - Bulut Oto Servis Kurumsal pakette SMS anket + NPS dashboard; ESN Sistem blogu servis tamamlandiktan sonra e-posta/SMS anket ve CRM'e aktarim anlatir.
5. Bakimdan cikan musteriden Google yorumu nasil istenir?
   - Piyzi Google yorum talebini, Jetyorum QR/yorum yonlendirmeyi, YorumTopla QR/WhatsApp davetini anlatir. Google resmi yardim sayfasi, yorum baglantisi/QR paylasmaya izin verir ama yorum karsiligi hediye/indirim gibi tesvikleri yasaklar.
6. Oto servis yazilimi fiyatlari ne kadar?
   - Canbus, OtoCore, ServisDefteri, Carzi ve OtoServiso public fiyat verir; Rocketly/OzgurKod/Piyzi gibi CRM sayfalarinda bu oturumda net public fiyat dogrulanmadi.
7. Mevcut ERP/muhasebe veya servis programi ile entegre olur mu?
   - Rapitek Logo/SAP/Netsis/Mikro entegrasyonlarini, ServisDefteri Paraşut entegrasyonunu, Jetyorum CRM/ERP/muhasebe entegrasyonu imkanini sayfalarinda anlatir.

---

## 4) Rakiplerde fiyat / ozellik seffafligi (yalnizca kaynakta gorulen)

| Rakip | Tip | Public fiyat / seffaflik | Kaynak |
|-------|-----|--------------------------|--------|
| **Canbus** | Servis/garaj yonetim yazilimi | Demo ucretsiz; Standart **149 TL/ay**'dan, Uzman **249 TL/ay**'dan baslar; sayfada eski/yeni fiyat gosterimi de var. | [servisyazilim.com](https://servisyazilim.com/) |
| **OtoCore** | Servis yonetim yazilimi | **1.500 TL/ay**, **15.000 TL/yil**, **20.000 TL/2 yil**, KDV haric; 30 gun ucretsiz deneme. | [otocore.tr](https://otocore.tr/) |
| **ServisDefteri** | Servis takip yazilimi | Deneme **0 TL**; yillik plan **5.000 TL**, kampanya **4.500 TL/yil + KDV**; tum ozellikler dahil iddiasi. | [servisdefteri.tr](https://servisdefteri.tr/) |
| **Carzi** | Oto servis/stok yonetim sistemi | Carzi Servis/Kaporta/Boya **25.000 TL/yil KDV dahil** kampanyali; Carzi Satis Stok **15.000 TL/yil KDV dahil**; ek kullanici **250 TL/yil**, ek sube **3.000 TL/yil**, e-Fatura **10.000 TL**. | [carzi.com.tr](https://carzi.com.tr/) |
| **OtoServiso** | Oto servis programi | Profesyonel **999 TL/ay**, Kurumsal **1.599 TL/ay**, KDV dahil; yillik alima 2 ay hediye. | [otoserviso.com/fiyatlar](https://www.otoserviso.com/fiyatlar) |
| **Rapitek Oto Servis CRM** | CRM + WhatsApp | **$25/kullanici/ay**'dan baslar; kurulum, egitim, destek dahil; 2-4 hafta canliya gecis iddiasi. | [rapitek.com/oto-servis-crm](https://rapitek.com/oto-servis-crm/) |
| **Bulut Oto Servis** | Servis yonetim yazilimi | 30 gun ucretsiz deneme; bu oturumda aylik TL paket fiyatlari sayfada dogrulanmadi. NPS ve WhatsApp belge paylasimi Kurumsal pakete ozel olarak anlatiliyor. | [bulutotoservis.com](https://bulutotoservis.com/) |
| **Rocketly / OzgurKod / Piyzi** | CRM, inbox, randevu, bakim takip | Bu oturumda public liste fiyat dogrulanmadi; ozellik ve sektor sayfalari acik. | [Rocketly](https://gorocketly.com/sektorler/oto-servis), [OzgurKod](https://ozgurkod.com/cozumler/oto-servis), [Piyzi](https://piyzi.com/sektorler/oto-servis-randevu-programi) |
| **Jetyorum / Akilli Isler / YorumTopla / Cevaply** | Yorum / itibar SaaS | Bu oturumda oto servis sayfalarinda net oto ozel fiyat dogrulanmadi; Akilli Isler fiyat bilgisi otel arastirmasinda ayrica dogrulanmisti. | Ilgili urun sayfalari |
| **Nefalix** | Musteri deneyimi / itibar SaaS | Plan ve onceki arastirmada public fiyat yuzeyi: Baslangic **9.500 TL/ay + 25.000 TL kurulum**, Pro **14.900 TL/ay + 50.000 TL kurulum**, Kurumsal **45.000 TL+/ay**, Sentinel **+3.500 TL/ay**, Recall **+2.500 TL/ay**. Bu oturumda Nefalix fiyat sayfasi yeniden fetch edilmedi; rakamlar `research/saglik-sektoru-arastirma.md` kaynak notuna dayanir. | [nefalix.com/fiyatlar](https://nefalix.com/fiyatlar) ve mevcut repo arastirmasi |

**Fiyat yorumu:** Oto servis operasyon yazilimlari genelde Nefalix'ten daha dusuk fiyatli gorunuyor cunku stok/is emri/fatura odakli KOBI araclari. Nefalix bu pazarda "servis programi alternatifi" diye konumlanirsa fiyat ankori zorlasir; "mevcut servis programinin uzerine yorum, WhatsApp, NPS ve kriz/recall katmani" diye konumlanirsa fiyat karsilastirmasi daha adil olur.

---

## 5) Uyum ve politika bulgulari

### 5.1 Google yorum daveti ve tesvik

Google Business Profile yardim sayfasi, isletmelerin yorum istemek icin baglanti veya QR kodu olusturup bunu makbuzlara, tesekkur e-postalarina, sohbet sonlarina ve basili QR olarak kullanabilecegini soyler. Ayni sayfada, Google Haritalar yorumlarinin gercek deneyimi yansitmasi gerektigi ve yorum karsiliginda ucretsiz/indirimli urun veya hizmet gibi tesviklerin "sahte etkilesim" sayilarak kesinlikle yasak oldugu belirtilir. Kaynak: [Google Isletme Profili Yardim](https://support.google.com/business/answer/16816815?hl=tr).

### 5.2 Review-gating riski

Bu arastirmada iki rakip yuzeyi review-gating diline yaklasiyor:

- Jetyorum otomobil sayfasi: "sadece mutlu musterilerinizi yorum birakma surecine yonlendirin" ifadesi.
- Esinix itibar sayfasi: "memnun musteriler Google'a, memnun olmayanlar ozel form'a" akisi.

Nefalix oto icerikleri bu dili kullanmamali. Uyumlu ifade: "Her musteriden ayni, tarafsiz ve tesviksiz geri bildirim istenir; dusuk puanlar ic aksiyon icin onceliklendirilir, fakat public yorum baglantisi memnuniyet skoruna gore saklanmaz."

### 5.3 Google yorum widget'i / dogrulama uyarisi

Jetyorum ve Sparkavis gibi yuzeyler Google yorumlarini isletme web sitesinde gostermeyi anlatir. Nefalix yeni oto icerikleri Google yorum widget'i anlatacaksa, Reklam Kurulu ve Google dogrulanabilirlik riskleri nedeniyle "kaynak, tarih, dogrulama ve secici gostermeme" uyarisi eklenmelidir. Bu arastirma dosyasi widget'i urun vaadi olarak onermiyor; yalnizca pazardaki rakip iddiasini kaynakli not ediyor.

### 5.4 KVKK rolu

Oto servis sektorunde saglik verisi gibi ozel nitelikli veri riski baskin degil; yine de musteri telefonu, plaka, arac sasi/motor numarasi, servis gecmisi, odeme/tahsilat bilgisi ve WhatsApp yazismalari kisisel veri icerebilir. Pazarlama dilinde veri sorumlusu **oto servis / bayi**, yazilim saglayici **veri isleyen** olarak ayrilmalidir. Nefalix, musterisi adina sinirli amacla isleme, saklama suresi, alt isleyen ve silme/iade sureclerini net anlatmalidir.

---

## 6) nefalix.com'da oto servis yuzeyi - var / eksik

Bu kosuda public landing reposuna dokunulmadi ve canli deploy iddiasi yapilmadi. Mevcut repo notlarina ve bu arastirma ihtiyacina gore:

| Yuzey | Durum |
|-------|-------|
| `/sektorler#oto` | Plan/gap baglaminda sektor yuzeyi oldugu biliniyor; bu kosuda landing checkout'u yok. |
| `/geo` | Saglik GEO pillar dosyalari bu repoda var; oto servis GEO dosyasi bu checkout'ta yok. |
| `/blog` | Oto servis odakli blog stok durumu bu kosuda tam taranmadi; ana teslimat arastirma dosyasi. |
| `/fiyatlar` | Onceki saglik arastirmasinda fiyat yuzeyi kaynaklandi; oto ozel fiyat anlatimi yok. |

**Eksik / GEO firsatlari:**

1. `oto servis musteri deneyimi yazilimi nedir?` exact-match GEO.
2. `oto servis Google yorum yonetimi nasil yapilir?` policy uyumlu GEO.
3. `oto servis CRM ile itibar yonetimi ayni sey mi?` ayristirma GEO.
4. `oto serviste WhatsApp randevu ve bakim hatirlatmasi nasil kurulur?` operasyon GEO.
5. `oto servis NPS ve servis sonrasi memnuniyet anketi nasil olculur?` NPS GEO.
6. `oto servis programi vs musteri deneyimi platformu` adil karsilastirma sayfasi.
7. `Jetyorum / YorumTopla / Akilli Isler alternatifi mi?` gibi rakip adli sayfalar ancak kaynakli, adil ve hukuki onayli yazilmali.

---

## 7) Nefalix konumlandirma cikarimi (oto servis)

- Oto servis SERP'i sagliktan farkli: "itibar ajansi" degil, **servis operasyon yazilimi** ve **WhatsApp/CRM** daha baskin.
- Dogrudan bosluk: servis programlari is emri/stok/faturayi cozer; yorum SaaS'lari Google/TripAdvisor yanitini cozer; CRM/inbox araclari WhatsApp ve randevuyu cozer. Nefalix'in kazanabilecegi alan, bunlari **servis sonrasi musteri deneyimi, yorum daveti, NPS, dusuk puan uyarisi ve recall** akisi olarak birlestirmek.
- Satis dili "oto servis programinizi degistirin" olmamali. Daha guvenli mesaj: "Mevcut servis programiniz ve WhatsApp akisiniza musteri deneyimi/itibar katmani ekleyin."
- Policy avantaji: Rakiplerde review-gating'e yaklasan ifadeler var. Nefalix, "herkese ayni tarafsiz yorum daveti, dusuk puana ic aksiyon" dilini net kullanirsa GEO ve guven tarafinda ayrisir.
- KVKK mesaji: Oto servis veri sorumlusu; Nefalix/yazilim saglayici veri isleyen. Plaka, telefon, arac gecmisi ve WhatsApp konusmalari icin aydinlatma/saklama/erisim yetkisi net olmali.

---

## 8) Director kapisi

**Onay.** Gerekce:

- Tekrar icerik degil; saglik ve otel arastirmalarinin formatini koruyor ama sektor bulgulari, rakip kumesi ve policy riskleri oto servise ozgu.
- Cevap/karar ilk bolumde net: siradaki faz ve bu kosunun ana teslimati yazildi.
- Rakip iddialari kaynak URL'leriyle ayrildi; yazilim / CRM-inbox / yorum-itibar SaaS kumesi ayrica siniflandi.
- Rakipler hakkinda asagilayici dil yok; dogrulanmayan fiyatlar "dogrulanmadi" olarak isaretlendi.
- Review-gating riski, rakip sayfalardan alintilanan kaynakli ifadelerle ve Nefalix icin yasak/uyumlu dil ayrimiyla yazildi.
- Google yorum widget konusu urun vaadi olarak kullanilmadi; yalnizca kaynakli risk notu eklendi.
- KVKK rolu acik: veri sorumlusu oto servis/bayi, veri isleyen yazilim saglayici/Nefalix.
- Kaynaksiz istatistik veya arama hacmi iddiasi yok; SERP siralamasi "ticari yogunluk + tekrar" olarak sinirlandi.

---

## 9) Kaynak logu

### Arama sorgulari

- `oto servis musteri deneyimi yazilimi Google yorum yonetimi Turkiye`
- `oto servis CRM yazilimi randevu WhatsApp musteri memnuniyet anketi`
- `oto servis Google yorum yonetimi yazilimi itibar yonetimi`
- `oto servis yazilimi musteri memnuniyet anketi NPS fiyat Turkiye Canbus Mysoft ESN Sistem`
- `oto servis programi is emri musteri takip WhatsApp yorum talebi fiyat`
- `Google yorum politikasi yorum karsiligi tesvik isletme profili`
- `Google Business Profile review gating ask all customers for reviews policy`

### Fetch / kaynak URL'leri

- [Canbus Oto Servis Programi](https://servisyazilim.com/)
- [OtoCore](https://otocore.tr/)
- [ServisDefteri](https://servisdefteri.tr/)
- [Carzi](https://carzi.com.tr/)
- [OtoServiso fiyatlar](https://www.otoserviso.com/fiyatlar)
- [Bulut Oto Servis Yazilimi](https://bulutotoservis.com/)
- [Rocketly Oto Servis CRM](https://gorocketly.com/sektorler/oto-servis)
- [OzgurKod Oto Servis CRM](https://ozgurkod.com/cozumler/oto-servis)
- [Piyzi Oto Servis Randevu Programi](https://piyzi.com/sektorler/oto-servis-randevu-programi)
- [Rapitek Oto Servis CRM](https://rapitek.com/oto-servis-crm/)
- [Jetyorum Otomobil Servisleri/Bayileri](https://www.jetyorum.com/otomobil-servisleri-bayileri)
- [YorumTopla](https://yorumtopla.com/)
- [Cevaply](https://cevaply.com/)
- [Akilli Isler](https://akilliisler.com/)
- [Sparkavis TR](https://sparkavis.app/tr)
- [Esinix Itibar Yonetimi](https://esinix.com/itibar-yonetimi)
- [Google Isletme Profili Yardim - yorum baglantisi/QR ve tesvik yasagi](https://support.google.com/business/answer/16816815?hl=tr)

---

*Dosya yolu: `research/oto-sektoru-arastirma.md`. Landing reposuna dokunulmadi; canli yayin/deploy/smoke iddiasi yoktur.*
