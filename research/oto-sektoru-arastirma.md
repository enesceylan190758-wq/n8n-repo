# Oto servis sektoru — yorum / musteri deneyimi otomasyonu arama arastirmasi

**Tarih:** 2026-08-27  
**Kapsam:** Turkiye · oto servis, tamirhane, yetkili servis, teknik servis  
**Tema:** oto servis yorum yonetimi + musteri deneyimi otomasyonu  
**Yontem:** Canli web arama / SERP + sayfa fetch. Keyword Planner, Ahrefs veya benzeri hacim API'si yok; "en yogun" siralama **sayisal arama hacmi degil**, bu oturumda gozlenen **SERP ticari yogunlugu + sorgular arasi tekrar** degerlendirmesidir. Fiyat, ozellik ve politika iddialari yalnizca kaynak URL goruldugunde yazildi.  
**Plan referansi:** `docs/nefalix-seo-geo-ajan-plani.md` §2.3 · Faz 1'de eksik kalan oto servis arastirmasi.

---

## 0) Siradaki faz

Gap notlarina gore Faz 0 teknik indeks riski kapandi; saglik ve otel arastirmalari hazir. Bu kosuda tamamlanan ana teslimat **Faz 1 oto servis arastirmasi**dir. Bundan sonraki pratik faz **Faz 4 otel GEO seti**: `otel yorum yonetimi yazilimi`, `TripAdvisor + Booking + Google tek panel`, `PMS vs itibar SaaS` ve `misafir NPS + WhatsApp` odakli GEO dosyalari.

---

## 1) Yogun ticari sinyalli kelime obekleri (Turkce)

Sira = bu arastirmada gozlenen SERP yogunlugu / capraz tekrar (yuksek -> dusuk). Hacim iddiasi yapilmaz.

| # | Obek | SERP karakteri | Ornek sorgu |
|---|------|----------------|-------------|
| 1 | `oto servis programi` / `oto servis yazilimi` | Cok sayida servis operasyon yazilimi; fiyat sayfalari ve blog karsilastirmalari var | `oto servis programi fiyat Canbus OtoServiso` |
| 2 | `oto servis CRM yazilimi` | CRM + WhatsApp + is emri anlatimi; Rapitek / OzgurKod gibi genel CRM'ler dikey landing acmis | `oto servis CRM yazilimi randevu WhatsApp` |
| 3 | `oto servis Google yorum yonetimi` | Jetyorum/Piyzi gibi yorum toplama SaaS + ajans yerel SEO icerikleri | `oto servis Google yorum yonetimi` |
| 4 | `oto servis musteri deneyimi yazilimi` | Operasyon yazilimi ve yorum SaaS ayni niyette karisiyor | `oto servis musteri deneyimi yazilimi` |
| 5 | `yetkili servis musteri memnuniyet anketi` | Teknik servis anket modulleri; FieldCo, ESN, Mysoft, ERM gibi genel servis/CRM yazilimlari | `yetkili servis musteri memnuniyet anketi otomasyon` |
| 6 | `oto servis WhatsApp otomasyon` | OtoCore, Rapitek, OzgurKod ve OtoServiso tarafinda randevu / is durumu / hatirlatma | `oto servis WhatsApp otomasyon` |
| 7 | `yakınımdaki tamirci Google Haritalar SEO` | Ajans bloglari; kategori, NAP, yorum ve yanit hizi uzerinden satis | `oto servis Google Haritalar SEO yakınımdaki tamirci` |
| 8 | `servis sonrasi anket teknik servis` | FieldCo/SerPro/ERM/Mysoft gibi teknik servis geneli | `teknik servis musteri memnuniyet anketi` |
| 9 | `oto servis randevu programi` | Randevu + is emri + stok programlari | `oto servis randevu programi` |
| 10 | `oto servis fiyat teklif programi` | Fatura, teklif, stok ve iscilik paketleri; deneyim degil operasyon agirlikli | `oto servis teklif is emri programi` |

**Nefalix gorunurlugu:** `site:nefalix.com oto servis Nefalix geo blog auto servis` sorgusunda public blog indeksinde oto servis NPS / tekrar ziyaret yazilari gorundu; bu oturumda `geo/` altinda oto servis exact-match GEO paketi gorulmedi. Marka, oto servis SERP'inde henuz kategori sayfasi gibi siralanan belirgin bir yuzeye sahip degil.

---

## 2) Kim siralaniyor? (ornek SERP'ler)

### 2.1 `oto servis musteri deneyimi yazilimi` / `oto servis Google yorum yonetimi`

| # | Marka / site | Model | Neden siralaniyor |
|---|--------------|-------|-------------------|
| 1 | **Jetyorum** — `jetyorum.com/otomobil-servisleri-bayileri` | Yorum / itibar SaaS | Otomobil bayileri ve servis geliri icin yorum toplama, geri bildirim, tek panel yorum yonetimi, sosyal paylasim, widget ve CRM/ERP entegrasyon anlatimi var. |
| 2 | **Jetyorum Teknik Servisler** — `jetyorum.com/teknik-servisler` | Yorum / itibar SaaS | Teknik servis sayfasinda konum bilgisi, geri bildirim, servisler arasi performans, negatif yorum onleme ve yorum widget'i anlatiliyor. |
| 3 | **Piyzi Google Yorum Kazandirma** — `piyzi.com/ozellikler/google-yorum-kazandirma` | Otomasyon / yorum SaaS | Randevu tamamlaninca yorum linki, segment filtreleri ve raporlama anlatimi; fiyat sayfasina CTA var. |
| 4 | **OtoServiso Blog** — `otoserviso.com/blog/oto-servis-programi-fiyatlari-2026` | Servis operasyon yazilimi blogu | Fiyat karsilastirmasi ve ROI formatinda ticari niyeti yakaliyor. |
| 5 | **Kobimedya** — `kobimedya.com/blog/oto-servis-google-haritalar-seo` | Ajans / yerel SEO | "Yakınımdaki tamirci" niyetini kategori, hizmet etiketi, yorum sayisi ve yanit hiziyle bagliyor. |

**Gozlem:** "Yorum yonetimi" niyeti oto serviste ikiye bolunuyor: Jetyorum/Piyzi gibi urunler yorum daveti ve widget'i satar; ajanslar Google Haritalar / Maps Pack gorunurlugunu satar. Nefalix icin ayrim net olmali: operasyonel deneyim sinyali + WhatsApp/inbox + NPS + yorum alarmi tek panel; Google siralama garantisi degil.

### 2.2 `oto servis CRM yazilimi` / `oto servis programi`

| # | Marka / site | Model | Neden siralaniyor |
|---|--------------|-------|-------------------|
| 1 | **OtoCore** — `otocore.tr` | Oto servis yonetim yazilimi | Randevu, is emri, stok, kasa, WhatsApp, musteri portali, plaka/ruhsat AI okuma ve public fiyat tek sayfada. |
| 2 | **OtoServiso** — `otoserviso.com` / `/fiyatlar` | Oto servis yonetim yazilimi | Is emri, teklif, arac bakim takip, musteri, stok, SMS bildirim, durum takip linki ve public fiyat tablosu. |
| 3 | **Canbus / servisyazilim.com** | Oto servis / teknik servis yazilimi | Arac kabul, is emri, stok, musteri, on muhasebe ve dusuk fiyatli paketlerle siralaniyor. |
| 4 | **OzgurKod Oto Servis** — `ozgurkod.com/cozumler/oto-servis` | CRM / otomasyon | WhatsApp, Instagram ve web taleplerini tek panelde toplama; parca onayi ve pipeline diliyle oto servis niyetine uyarlanmis. |
| 5 | **Rapitek Oto Servis CRM** — `rapitek.com/oto-servis-crm` | CRM / WhatsApp-native | 5-500 kullanicili ekipler, WhatsApp Business API, ERP entegrasyonu ve hazir oto servis pipeline'i anlatiliyor. |
| 6 | **ESN Sistem Otomotiv** — `esnsistem.com/sektorler/otomotiv` | CRM + teknik servis / ERP | Servis, yedek parca, CRM, e-fatura, mobil saha ve servis sonrasi memnuniyet anketleri. |
| 7 | **Değer Yazılım** — `degeryazilim.com/blog/...oto-servis...` | ERP / ozel yazilim | Randevu, is emri, stok, cari ve muhasebe entegrasyonu bloglariyla long-tail kapsiyor. |
| 8 | **Mysoft CRM** — `mysoftcrm.com/teknik-servis-yonetimi`, `/anket-yonetimi` | Genel CRM + teknik servis modulu | Teknik servis yonetimi ve anket/geri bildirim modulu ayrik sayfalarda. |

**Gozlem:** Bu kumede ana is "itibar" degil; servis operasyonunu dijitallestirme. Rakipler arac gecmisi, is emri, stok, fatura, e-Fatura ve durum takip linkiyle kazaniyor. Nefalix bu sayfalara "DMS/ERP'nin yerine gecmez; servis kapanisi sonrasi deneyim, yorum ve tekrar ziyaret katmanidir" diye cevap vermeli.

### 2.3 `yetkili servis musteri memnuniyet anketi` / `teknik servis NPS`

| # | Marka / site | Model | Neden siralaniyor |
|---|--------------|-------|-------------------|
| 1 | **FieldCo** — `fieldco.com.tr/.../musteri-memnuniyet-anketi-teknik-servis-programi` | Teknik servis yazilimi blog/modul | Is emri kapandiktan 2 saat sonra SMS/e-posta anketi, 5 puanli emoji skalasi, dusuk puanda yonetici bildirimi anlatiliyor. |
| 2 | **SerPro** — `serpro.com.tr` | Teknik servis SaaS | Is emri, takip linki, SMS/WhatsApp otomasyon, memnuniyet anketi ve yildiz puanlama ozellikleriyle gorunuyor. |
| 3 | **ERM CRM** — `erm.com.tr/.../memnuniyet-anketleri` | Servis icin CRM / anket | Kural bazli otomatik anket gonderimi, e-posta/SMS linki ve dashboard anlatimi. |
| 4 | **Mysoft CRM Anket Yonetimi** — `mysoftcrm.com/anket-yonetimi` | CRM / anket | Anket formu, mail gonderimi, CRM uzerinde raporlama ve dusuk memnuniyette otomatik gorev atama. |
| 5 | **Palmate AI / SmileYou** | Genel CSAT/NPS / kiosk-QR | Destek gorusmesi veya temas noktasindan sonra CSAT/NPS; oto servis dahil genis sektor dili. |

**Gozlem:** Bu niyet daha cok teknik servis geneline kayiyor. Oto servis icin Nefalix'in avantaji, anketi yalniz raporlamak degil; WhatsApp mesajlari, Google yorumlari ve tekrar ziyaret/Recall sinyaliyle ayni operasyon akisina baglamak olabilir.

### 2.4 `oto servis Google Haritalar SEO` / ajans sonuclari

| # | Marka / site | Model | Neden siralaniyor |
|---|--------------|-------|-------------------|
| 1 | **Kobimedya** | Ajans / yerel SEO | Oto servis icin "yakınımdaki tamirci" blogu; kategori, hizmet etiketi, yorum sayisi, yanit hizi ve panel olcumu. |
| 2 | **Zeisoft** | Ajans / Google Isletme yonetimi | QR, fatura alti link, satis sonrasi SMS ile gercek yorum talebi ve spam yorum basvuru sureci anlatimi. |
| 3 | **TCISLEM** | Ajans / yerel SEO | Google Business Profile, NAP, citation, yorum yonetimi, AutoRepair/AutoDealer schema gibi yerel SEO mimarisi. |
| 4 | **Web4Medya** | Ajans / GBP yonetimi | Google Harita kaydi, yorum toplama stratejisi, QR/e-posta/SMS ve olumsuz yorum krizi anlatimi. |
| 5 | **Murat Reklam Ajansi Group** | Ajans / Google Harita yorum | Silinen yorumlar / yorum yonetimi odakli icerik; garanti tonu icin dikkatle ele alinmali. |

**Gozlem:** Ajanslar "siralamada 1. sira" ve yorum sayisi/puan artisi vaadini one cikariyor. Nefalix icerigi bu hatta girerse kesin garanti veya manipulative yorum dili kullanmamali; olcum, yanit disiplini ve operasyonel aksiyon dili daha guvenli.

---

## 3) Rakip ayrimi (yazilim / ajans / DMS-ERP)

| Kume | Ornekler | Ne satarlar? | Nefalix icin mesaj |
|------|----------|--------------|--------------------|
| **Servis operasyon yazilimi / DMS-ERP** | OtoCore, OtoServiso, Canbus, ESN Sistem, Değer Yazılım | Is emri, arac kabul, stok, teklif, fatura, randevu, servis gecmisi | Nefalix bu katmanin yerine gecmez; servis kapanisi sonrasi deneyim, yorum, NPS ve tekrar ziyaret katmanini baglar. |
| **CRM / WhatsApp-native operasyon** | Rapitek, OzgurKod, Mysoft CRM | CRM kaydi, pipeline, WhatsApp ekip gelen kutusu, kampanya/anket | Nefalix'in farki oto servis sahibine ozel itibar + memnuniyet + kriz sinyalini daha dar ve alintilanabilir anlatmak olmali. |
| **Yorum / itibar SaaS** | Jetyorum, Piyzi | Yorum talebi, Google yonlendirme, yorum izleme, widget, AI yanit | Review-gating ve widget dogrulama uyarisi olmadan kopyalanmamali; Nefalix tarafsiz yorum daveti ve kaynakli widget uyarisini vurgulamali. |
| **Ajans / local SEO** | Kobimedya, Zeisoft, TCISLEM, Web4Medya | Google Business Profile, NAP/citation, yorum stratejisi, spam basvuru, lokasyon SEO | Nefalix ajans degil; siralama garantisi yerine veri akislarini ve isletme icindeki aksiyon takibini konumlamali. |
| **Genel CSAT/NPS araclari** | FieldCo, SerPro, ERM, SmileYou, Palmate AI | Anket, dusuk puan bildirimi, saha/teknik servis raporu | Nefalix'in farki CSAT/NPS sonucunu yorum, WhatsApp ve recall ile birlikte ele almasidir. |

---

## 4) Fiyat / ozellik seffafligi (bu oturumda dogrulanan)

| Rakip | Tip | Public fiyat / fiyat durumu | Kaynak |
|-------|-----|-----------------------------|--------|
| **OtoCore** | Oto servis yonetim yazilimi | **1.500 TL/ay**, **15.000 TL/yil**, **20.000 TL/2 yil**; KDV haric; 30 gun deneme; WhatsApp ve musteri portali pakette | [otocore.tr](https://otocore.tr/) |
| **OtoServiso** | Oto servis yonetim yazilimi | Web arama sonucunda fiyat sayfasinda **999 TL/ay Profesyonel** ve **1.599 TL/ay Kurumsal** gorundu; ayni oturumdaki blog sonucunda eski/alternatif **1.999 / 2.999 TL** rakamlari da gorundu. Guncel iddia icin fiyat sayfasi yeniden kontrol edilmeli. | [otoserviso.com/fiyatlar](https://www.otoserviso.com/fiyatlar), [otoserviso.com/blog/oto-servis-programi-fiyatlari-2026](https://www.otoserviso.com/blog/oto-servis-programi-fiyatlari-2026) |
| **Canbus / servisyazilim.com** | Oto servis yazilimi | Standart **149 TL/ay**'dan, Uzman **249 TL/ay**'dan baslar; 30 gun deneme | [servisyazilim.com](https://servisyazilim.com/), [canbus.net.tr/teknik-servis-yazilimi](https://canbus.net.tr/teknik-servis-yazilimi/) |
| **Rapitek Oto Servis CRM** | CRM / WhatsApp-native | **$25/kullanici/ay**'dan baslar; kurulum, egitim ve destek dahil iddiasi; 2-4 hafta canliya gecis | [rapitek.com/oto-servis-crm](https://rapitek.com/oto-servis-crm/) |
| **ESN Sistem** | CRM + teknik servis / ERP | Public liste fiyat yok; lisans bedeli kullanici sayisi ve modul secimine gore degisir, iletisim istenir | [esnsistem.com/sektorler/otomotiv](https://www.esnsistem.com/sektorler/otomotiv) |
| **Jetyorum** | Yorum / itibar SaaS | Bu oturumda public TL liste fiyat dogrulanmadi; bilgi iste CTA | [jetyorum.com/otomobil-servisleri-bayileri](https://www.jetyorum.com/otomobil-servisleri-bayileri), [jetyorum.com/teknik-servisler](https://www.jetyorum.com/teknik-servisler) |
| **Piyzi Google Yorum Kazandirma** | Otomasyon / yorum SaaS | Sayfada "Fiyatlara Bak" ve 14 gun deneme CTA var; bu oturumda paket TL rakami fetch edilmedi | [piyzi.com/ozellikler/google-yorum-kazandirma](https://piyzi.com/ozellikler/google-yorum-kazandirma) |
| **Nefalix** | B2B SaaS | Baslangic **9.500 TL/ay + 25.000 TL kurulum**; Profesyonel **14.900 TL/ay + 50.000 TL kurulum**; Kurumsal **45.000 TL+/ay**; Sentinel **+3.500 TL/ay**, Recall **+2.500 TL/ay** | [nefalix.com/fiyatlar](https://nefalix.com/fiyatlar) |

**Fiyat yorumu:** Oto servis operasyon yazilimlari Nefalix'ten daha dusuk aylik fiyatlarla giriyor; bu nedenle Nefalix oto servis GEO iceriginde "servis programi" yerine **itibar + deneyim + tekrar ziyaret + WhatsApp/NPS** katmanini satmali. Aksi halde fiyat karsilastirmasi yanlis kategoriye cekilir.

---

## 5) Politika / uyum bulgulari

### 5.1 Google yorum politikasi

Google Haritalar katkı politikasinda yorumlarin gercek deneyimi yansitmasi gerektigi, yorum karsiligi odeme/indirim/ucretsiz hizmet gibi tesviklerin yasak oldugu ve saticilarin olumsuz yorumlari engellemesine ya da ozellikle olumlu yorum istemesine izin verilmedigi yaziyor. Ayni sayfa, tesvik sunmadan ve puani/icerigi etkilemeye calismadan gercek deneyime dayali yorum istemeye izin verildigini belirtiyor. Kaynak: [Google Katki Politikasi](https://support.google.com/contributionpolicy/answer/7400114?hl=tr).

**Icerik sonucu:** Oto servis GEO icerigi "memnun musteriyi Google'a, memnun olmayanı iceriye" gibi secici yorum davetini ovmemeli. Geri bildirim akisi herkes icin tarafsiz olmalı; dusuk puanlar ic aksiyon icin kullanilabilir, ancak public yorum davetinin puan manipülasyonu gibi okunmasindan kacinilmali.

### 5.2 Widget / yeniden yayinlama riski

Jetyorum otomobil ve teknik servis sayfalarinda yorum widget'i / iFrame / API ile yorum ve puanlari isletme sitesine ekleme anlatiliyor. Plan §4a'daki Reklam Kurulu uyarisi nedeniyle Nefalix icerigi Google yorum widget'ini anlatirsa kaynak, tarih, dogrulama ve secilmis yorum manipülasyonu uyarisini eklemeli.

### 5.3 KVKK rolu

Oto servis baglaminda veri sorumlusu servis/bayi; Nefalix gibi yazilim saglayici veri isleyen konumunda anlatilmali. Arac plakasi, ruhsat, iletisim bilgisi, servis gecmisi ve mesaj icerigi kisisel veri icerebilir. "KVKK'yi tamamen cozer" gibi kesin garanti dili yerine, aydinlatma/izin/saklama suresi sorumlulugunun isletmede oldugu, yazilimin teknik ve sozlesmesel sinirlarda isledigi yazilmali.

---

## 6) Nefalix.com'da oto servis yuzeyi

| Yuzey | Durum |
|-------|-------|
| `/blog` | Public aramada oto servis NPS / tekrar ziyaret odakli en az iki blog sonucu gorundu. |
| `/geo` | Bu checkout'ta `geo/` altinda saglik odakli 6 dosya var; oto servis exact-match GEO dosyasi yok. |
| `/sektorler` | Plan notlarinda Auto Servis hedef sektorlerden biri; bu kosuda landing repo degistirilmedi. |
| `/fiyatlar` | Sektor seciminde "Auto Servis" opsiyonu ve Nefalix public paket fiyatlari gorundu. |

**Eksik (Faz 4 / oto GEO backlog):**

- `oto servis musteri deneyimi yazilimi` answer-first GEO
- `oto servis Google yorum yonetimi` GEO (review-gating uyari zorunlu)
- `oto servis WhatsApp otomasyon ve NPS` GEO
- `servis programi vs itibar/deneyim katmani` GEO (OtoCore/OtoServiso/Canbus gibi DMS-ERP ayrimi)
- `oto servislerde olumsuz yorum kriz yonetimi` GEO
- `Nefalix vs oto servis programi` karsilastirma sayfasi: rakipleri asagilamadan, kategori farkini aciklayarak

---

## 7) Nefalix konumlandirma cikarimi (oto servis)

- Oto servis SERP'i sagliktan farkli: "itibar" kelimesi tek basina baskin degil; "oto servis programi" ve "CRM/WhatsApp" niyeti daha yogun.
- Operasyon yazilimlari fiyat ve ozellikte seffaf; Nefalix daha pahali gorunecegi icin dogrudan "servis programi" kategorisine sokulmamali.
- En guclu bosluk: is emri kapandiktan sonra musteri deneyimi sinyalini toplamak, dusuk puani ic aksiyona baglamak, Google yorum/yanit surecini kacirmamak ve tekrar ziyaret hatirlatmasini ayni panelde izlemek.
- Icerik tonu "Google'da uste cikarir" degil; "yorumu, NPS'i, WhatsApp'i ve tekrar ziyaret sinyalini kacirmayan operasyon katmani" olmali.

---

## 8) Director denetimi

**Onay — arastirma teslimati.** Gerekce: Canli web/SERP ve fetch kaynaklari kullanildi; rakipler yazilim / ajans / DMS-ERP olarak ayrildi; public fiyat olmayan yerlerde rakam uydurulmadi; Google yorum politikasi, review-gating ve widget riski acikca isaretlendi; KVKK rolu "servis/bayi = veri sorumlusu, Nefalix = veri isleyen" olarak ayrildi.

**Red gerektiren bulgu yok.** Not: OtoServiso fiyatinda ayni oturumda fiyat sayfasi ve blog sonucu arasinda farkli rakamlar goruldugu icin gelecek karsilastirma iceriginde guncel fiyat sayfasi tekrar fetch edilmeden kesin fiyat karsilastirmasi yapilmamali.

---

## 9) Kaynak logu

Arama sorgulari:

- `oto servis musteri deneyimi yazilimi Google yorum yonetimi Turkiye`
- `oto servis CRM yazilimi randevu WhatsApp musteri memnuniyet anketi`
- `yetkili servis musteri memnuniyet anketi NPS otomasyon Turkiye`
- `oto servis Google yorum yonetimi sikayetvar local SEO ajans`
- `oto servis programi fiyat Canbus Mysoft Caneke Değer Yazılım ESN Sistem`
- `Caneke oto servis programi ozellikleri fiyat`
- `Değer Yazılım oto servis programi ozellikleri fiyat`
- `Mysoft oto servis programi musteri memnuniyet anketi fiyat`
- `site:nefalix.com oto servis Nefalix geo blog auto servis`

Fetch / kaynak URL'leri:

- [OtoCore](https://otocore.tr/)
- [OtoServiso fiyatlar](https://www.otoserviso.com/fiyatlar)
- [OtoServiso fiyat blogu](https://www.otoserviso.com/blog/oto-servis-programi-fiyatlari-2026)
- [Canbus / Servis Yazilim](https://servisyazilim.com/)
- [Canbus teknik servis yazilimi](https://canbus.net.tr/teknik-servis-yazilimi/)
- [Jetyorum otomobil servisleri / bayileri](https://www.jetyorum.com/otomobil-servisleri-bayileri)
- [Jetyorum teknik servisler](https://www.jetyorum.com/teknik-servisler)
- [Piyzi Google yorum kazandirma](https://piyzi.com/ozellikler/google-yorum-kazandirma)
- [Kobimedya oto servis Google Haritalar SEO](https://kobimedya.com/blog/oto-servis-google-haritalar-seo)
- [Rapitek oto servis CRM](https://rapitek.com/oto-servis-crm/)
- [OzgurKod oto servis](https://ozgurkod.com/cozumler/oto-servis)
- [ESN Sistem otomotiv](https://www.esnsistem.com/sektorler/otomotiv)
- [FieldCo teknik servis memnuniyet anketi](https://www.fieldco.com.tr/tr/blog/teknikservisprogrami/musteri-memnuniyet-anketi-teknik-servis-programi)
- [Google Haritalar katki politikasi](https://support.google.com/contributionpolicy/answer/7400114?hl=tr)
- [Nefalix fiyatlar](https://nefalix.com/fiyatlar)

---

*Dosya yolu: `research/oto-sektoru-arastirma.md` · Landing repo degistirilmedi; canli deploy veya GSC indexing iddiasi yok.*
