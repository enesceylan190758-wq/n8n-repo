# Oto servis sektoru — yorum / musteri deneyimi otomasyonu arama arastirmasi

**Tarih:** 2026-08-11  
**Kapsam:** Turkiye · oto servis, tamirhane, lastikci, kaporta-boya, oto elektrik, yetkili servis sonrasi hizmetler  
**Tema:** oto servis Google yorum yonetimi + servis sonrasi NPS/memnuniyet + WhatsApp/bakim hatirlatma otomasyonu  
**Yontem:** Canli web arama / SERP + sayfa fetch. Keyword Planner, Ahrefs veya benzeri hacim API'si yok; "en yogun" siralama = bu oturumda gozlenen **SERP ticari yogunlugu + sorgular arasi tekrar**. Sayisal hacim iddiasi yapilmaz.  
**Plan referansi:** `docs/nefalix-seo-geo-ajan-plani.md` §2.3 · Faz 1'in son eksigi.

**Kaynak notu:** Web arama arac ciktisi Google TR SERP'inin anlik bir gorunumudur; konum/kisisellestirme farki olabilir. People Also Ask kutusu ayri parse edilmedi; alt sorular siralanan sayfalarin SSS/H2'lerinden ve otomotiv satis sonrasi hizmet literaturunden derlendi.

---

## 1) En yogun ticari sinyalli 10 kelime obegi (Turkce)

Sira = bu arastirmada gozlenen ticari sayfa yogunlugu / tekrar (yuksek -> dusuk).

| # | Obek | SERP karakteri | Ornek sorgu |
|---|------|----------------|-------------|
| 1 | `oto servis programi` / `oto servis yazilimi` | Bulut servis ERP/garaj programlari; fiyat sayfalari gorunur | `oto servis CRM yazilimi Turkiye servis takip programi fiyat` |
| 2 | `oto servis CRM` | CRM + servis pipeline + WhatsApp katmani; genel CRM oyunculari da cikiyor | `oto servis CRM AI randevu bakim takip` |
| 3 | `oto servis randevu takip programi` | Online randevu, is emri, WhatsApp/SMS hatirlatma sayfalari | `oto servis WhatsApp otomasyon randevu hatirlatma yazilimi` |
| 4 | `arac bakim takip yazilimi` | Periyodik bakim, arac gecmisi, plaka/servis kaydi | SERP icinde Mekaniq/OtoServiso/ServisDefteri tekrar |
| 5 | `oto servis musteri memnuniyet anketi` | NPS modulu olan servis ERP'leri + teknik servis anket bloglari | `oto servis musteri memnuniyet anketi yazilimi NPS Turkiye` |
| 6 | `yetkili servis musteri memnuniyet anketi` | Akademik/otomotiv CX icerigi; bayi/yetkili servis niyeti | `yetkili servis musteri memnuniyet anketi otomotiv NPS` |
| 7 | `oto servis WhatsApp otomasyon` | Randevu, arac hazir, bakim zamani, kampanya mesajlari | `oto servis WhatsApp otomasyon randevu hatirlatma yazilimi` |
| 8 | `oto servis Google yorum yonetimi` | Otoya ozellesmis sonuc zayif; genel Google yorum SaaS'lari geliyor | `oto servis Google yorum yonetimi yazilimi` |
| 9 | `oto servis NPS` / `otomotiv NPS` | Pisano/Staffino gibi otomotiv CX ve NPS oyunculari | `otomotiv NPS musteri deneyimi servis` |
| 10 | `periyodik bakim hatirlatma WhatsApp` | Oto servis CRM/WhatsApp akisi; tekrar ziyaret niyeti | Piyzi/Rocketly/ServisDefteri sayfalari |

**Nefalix gorunurlugu:** Canli `/blog` indeksinde oto servis NPS ve tekrar ziyaret konulu iki blog gorundu; `/geo` tarafinda bu oturumda oto servis odakli pillar dosyasi yok. Marka disi oto servis sorgularinda Nefalix SERP varligi bu arastirmada dogrulanmadi.

---

## 2) Kim siralaniyor? Rakipleri modeline gore ayirma

### 2.1 Servis ERP / garaj yonetim yazilimlari

Bu kume, HBYS/PMS benzeri "ana operasyon sistemi" rolundedir: is emri, arac/musteri kaydi, stok, fatura, kasa, randevu ve teknisyen takibi.

| Marka / site | Model | Kaynakli gozlem | Nefalix icin anlam |
|---|---|---|---|
| **OtoServiso** — `otoserviso.com` | Oto servis ERP / servis programi | Is emri, teklif, arac bakim takip, stok, faturalama; fiyat sayfasi Profesyonel **999 TL/ay**, Kurumsal **1.599 TL/ay**, KDV dahil, 14 gun deneme diyor. Kaynak: https://www.otoserviso.com/fiyatlar | Nefalix, bu sistemin yerine gecmek yerine servis sonrasi geri bildirim, Google yorum ve kriz/WhatsApp katmani olarak konumlanmali. |
| **Mekaniq** — `mekaniq.com.tr` | Oto servis yonetim yazilimi | Is emri, musteri/arac, stok, fatura, randevu, WhatsApp bildirim; ucretsiz paket + **799 / 1.499 / 2.099 / 3.499 TL/ay** planlari ve WhatsApp eklentisi gorundu. Kaynak: https://mekaniq.com.tr/ | Fiyat ve moduller seffaf; Nefalix'in ayrimi "yorum + NPS + inbox + recall/kriz" uzmanligi olmali. |
| **OtoCore** — `otocore.tr` | Oto servis yonetim yazilimi | SERP snippet: randevu, is emri, stok, kasa, WhatsApp; tek Pro paket **1.500 TL/ay**, yillik **15.000 TL**, 30 gun deneme. Kaynak: https://otocore.tr/ | Oto servis CRM/ERP sorgusunda guclu; fiyat iddiasi SERP/fetch snippet'inden yazilmali, yeniden fetch timeout verdi. |
| **ServisDefteri.tr** — `servisdefteri.tr` | Bulut servis takip yazilimi | Is emri, stok, kasa, randevu, Paraşut, WhatsApp bildirimi, AI ariza analizi; **30 gun ucretsiz**, yillik **5.000 TL + KDV** plan sayfada gorundu. Kaynak: https://servisdefteri.tr/ | AI ariza/rapor taslagi anlatimi var; yorum/NPS derinligi sinirli gorunuyor. |
| **Bulut Oto Servis** — `bulutotoservis.com` | Web tabanli oto servis programi | Kurumsal pakette SMS anket, 1-10 puan, otomatik NPS hesaplama, dusuk puan tespiti ve dashboard anlatiliyor. Kaynak: https://bulutotoservis.com/bulut-otoservis-programi-ozellikleri.html | NPS modulu olan dogrudan kategori rakibi; ancak Google yorum/itibar ve cok kanalli inbox anlatimi Nefalix kadar merkezde degil. |

### 2.2 CRM / WhatsApp / servis sonrasi iletisim katmani

Bu kume ana garaj ERP'si olmayabilir; musteri iletisim kanali, pipeline, randevu ve bakim hatirlatma uzerine kurulur.

| Marka / site | Model | Kaynakli gozlem | Nefalix icin anlam |
|---|---|---|---|
| **Rocketly Oto Servis CRM** — `gorocketly.com/sektorler/oto-servis` | CRM + AI agent + omnichannel inbox | WhatsApp/Instagram/web form tek inbox, servis pipeline, periyodik bakim WhatsApp hatirlatma; "garaj yonetim yazilimi degil, CRM katmani" aciklamasi var. Fiyat: Free, Starter **$29/ay**, Professional **$79/ay**, Business **$199/ay**. Kaynak: https://gorocketly.com/sektorler/oto-servis | Nefalix'e en yakin "iletisim katmani" rakibi; ancak Google yorum/NPS/itibar kapisi ayrica vurgulanmali. |
| **Piyzi Oto Servis Randevu Programi** — `piyzi.com/sektorler/oto-servis-randevu-programi` | Randevu + WhatsApp Business + periyodik bakim otomasyonu | Meta Tech Provider olarak WhatsApp Business, randevu oncesi/sonrasi otomatik iletisim, bakim hatirlatma ve yorum talebi anlatiliyor. Kaynak: https://piyzi.com/sektorler/oto-servis-randevu-programi | "Bakim hatirlatma + yorum talebi" dili Nefalix'in Recall/geri bildirim kurgusuna yakin; review-gating imasi kurmadan ayrismak gerekir. |
| **FieldCo** — teknik servis blogu | Teknik servis yonetimi + anket modulu | Is emri kapandiktan **2 saat sonra** SMS/e-posta anket; 3 soru, dusuk puanda servis mudurune bildirim, gonulluluk vurgusu. Kaynak: https://www.fieldco.com.tr/tr/blog/teknikservisprogrami/musteri-memnuniyet-anketi-teknik-servis-programi | Oto servise dogrudan degil ama "servis sonrasi anket zamanlamasi" icin iyi operasyonel kaynak. |

### 2.3 Google yorum / itibar yazilimlari

Bu kume sektor bagimsizdir; "oto servis Google yorum yonetimi" sorgusunda otoya ozellesmis dikey oyuncu yerine genel Google yorum SaaS'lari gelir.

| Marka / site | Model | Kaynakli gozlem | Uyum notu |
|---|---|---|---|
| **Restarun** — `restarun.com` | Google yorum yonetimi SaaS | Google yorum takibi, AI yanit onerisi, anlik bildirim, rapor; 14 gun deneme. Kaynak: https://restarun.com/ | Otoya ozel degil; Nefalix oto servis sayfasi "servis sonrasi NPS + yorum + bakim recall" bilesimini one cikarmali. |
| **Sparkavis** — `sparkavis.app/tr` | Mobil Google Business yorum uygulamasi | Free / **9,99 EUR/ay** Pro / **29,99 EUR/ay** Business; AI yanit, QR kod, yorum widget'i, coklu isletme. Kaynak: https://sparkavis.app/tr | Widget anlatiminda Reklam Kurulu/Google dogrulama uyarisiz yeniden yayinlama dili kullanilmamali; Nefalix iceriginde dogrulama ve kaynak etiketi sarti yazilmali. |
| **Esinix Itibar Yonetimi** — `esinix.com/itibar-yonetimi` | Google/Facebook yorum ve itibar SaaS | Sayfa "memnun -> Google, memnun degil -> ozel form" akisini "review gating" diye anlatiyor. Kaynak: https://esinix.com/itibar-yonetimi | Bu pratik Nefalix iceriginde olumlu ornek gibi kullanilmamali; Google politika riski olarak not edilmeli. |
| **VoyageRespond Google AI sayfasi** — `voyagerespond.com/platform/google-yorumlari-icin-yapay-zeka` | Genel/otel agirlikli AI yorum yanit | Google Business Profile API, tek panel, manuel/onayli veya otomatik yanit modlari anlatiliyor. Kaynak: https://voyagerespond.com/platform/google-yorumlari-icin-yapay-zeka | Otel arastirmasinda ana rakipti; oto sorgusunda genel AI yorum kaynagi olarak gorunuyor. |

### 2.4 Otomotiv CX / NPS platformlari ve literatur

Bu kume daha cok bayi/yetkili servis ve cok lokasyonlu otomotiv aglari icindir.

| Kaynak | Model | Kaynakli gozlem | Icerik kullanimi |
|---|---|---|---|
| **Pisano Otomotiv** — `pisano.com/tr/sektorel-cozumler/otomotiv` | Voice of Customer / CX platformu | Otomotiv yolculugunda NPS, CSAT, hizmet verimliligi, cok lokasyonlu bayi/servis agi ve gercek zamanli geri bildirim anlatiliyor. Kaynak: https://www.pisano.com/tr/sektorel-cozumler/otomotiv | Oto GEO iceriklerinde "servis sonrasi NPS" kategorisini kaynaklamak icin uygun. |
| **Staffino otomotiv CX** — `staffino.com/tr/otomotiv-endustrisinde-musteri-deneyimi/` | CX platform vaka icerigi | Araba servisi, lastik servisi ve kaporta temas noktalarinda CSAT/NPS programi anlatiliyor. Kaynak: https://staffino.com/tr/otomotiv-endustrisinde-musteri-deneyimi/ | Temas noktasi mantigi icin kaynak; rakam iddiasi alinmadi. |
| **PressAcademia DOI 2017.645** | Akademik makale | Yetkili otomobil servislerinde satis sonrasi hizmet memnuniyetinin tavsiye davranisina etkisi; danisman memnuniyeti ve teslimatta ilk fiyata sadakat faktorleri one cikiyor. Kaynak: https://doi.org/10.17261/pressacademia.2017.645 | "Tavsiye davranisi servis danismani ve fiyat seffafligindan etkilenir" temasi kaynakli kullanilabilir. |
| **DergiPark IJMEB 2023** | Akademik makale | Otomotiv satis sonrasi hizmetlerde musteri beklentisi/memnuniyeti ve marka karsilastirmasi; must-be ve attractive hizmet beklentileri ayrimi. Kaynak: https://dergipark.org.tr/tr/pub/ijmeb/article/1292817 | GEO iceriginde "sadece araci teslim etmek yetmez; beklenti kategorileri ayrismali" argumani icin kaynak. |

**Ortak SERP deseni:** "Oto servis programi" sorgularinda ERP/garaj yazilimlari baskin; "oto servis Google yorum yonetimi" sorgusunda dikey oto rakip az, genel yorum SaaS'lari geliyor; "otomotiv NPS/musteri deneyimi" sorgusunda ise bayi/yetkili servis odakli CX platformlari ve akademik kaynaklar gorunuyor.

---

## 3) Alt sorular (SSS/H2/PAA benzeri)

1. Oto servis programi sadece is emri mi tutar, yoksa randevu, stok, fatura ve bakim hatirlatma da yapar mi? (OtoServiso, Mekaniq, ServisDefteri)
2. Servis sonrasi memnuniyet anketi ne zaman gonderilmeli: arac tesliminde hemen mi, yoksa 2 saat / ertesi gun gibi gecikmeyle mi? (FieldCo)
3. Periyodik bakim hatirlatmasi km'ye mi, tarihe mi, ikisine birden mi baglanmali? (Rocketly, Piyzi, ServisDefteri)
4. WhatsApp mesajlari otomatik mi gider, yoksa servis danismani onaylar mi? (OtoCore SERP snippet, Rocketly, Piyzi)
5. Dusuk NPS/puan gelince ne olur: servis mudurune bildirim mi, gorev mi, geri kazanma akisi mi? (Bulut Oto Servis, FieldCo, SmileYou/Pisano)
6. Memnun musteriden Google yorumu nasil istenir; secici yorum daveti veya hediye/indirim riski var mi? (Esinix risk ornegi, Google politika kapisi)
7. Oto servis yorumlarini web sitesinde gostermek guvenli mi; dogrulama/kaynak etiketi nasil verilmeli? (Sparkavis widget ornegi + Reklam Kurulu uyarisi)
8. Oto servis CRM ile garaj yonetim yazilimi ayni sey mi? (Rocketly "CRM katmani, garaj yonetimi degil" SSS)

---

## 4) Rakiplerde fiyat / ozellik seffafligi (somut kaynakli)

| Rakip | Tip | Public fiyat / ozellik | Kaynak |
|---|---|---|---|
| **OtoServiso** | Oto servis ERP | Profesyonel **999 TL/ay**, Kurumsal **1.599 TL/ay**, KDV dahil; 14 gun deneme; SMS, online randevu, durum takip linki, cok sube gibi moduller | https://www.otoserviso.com/fiyatlar |
| **Mekaniq** | Oto servis ERP | Ucretsiz plan; Baslangic **799 TL/ay**, Profesyonel **1.499 TL/ay**, Premium **2.099 TL/ay**, Kurumsal **3.499 TL/ay**; WhatsApp eklentisi **99 TL/ay**, AI Nitro paketleri | https://mekaniq.com.tr/ |
| **ServisDefteri.tr** | Oto servis takip yazilimi | 30 gun deneme; yillik plan **5.000 TL**, kampanyali **4.500 TL/yil + KDV**; AI ariza analizi, WhatsApp bildirimi, Paraşut entegrasyonu | https://servisdefteri.tr/ |
| **OtoCore** | Oto servis yazilimi | SERP/fetch snippet: Pro **1.500 TL/ay**, yillik **15.000 TL**, 30 gun deneme; randevu/is emri/stok/kasa/WhatsApp | https://otocore.tr/ |
| **Bulut Oto Servis** | Oto servis ERP + NPS modulu | Kurumsal pakete ozel SMS anket, 1-10 puanlama, otomatik NPS, dusuk puan tespiti ve dashboard | https://bulutotoservis.com/bulut-otoservis-programi-ozellikleri.html |
| **Rocketly Oto Servis CRM** | CRM / inbox / workflow | Free; Starter **$29/ay**, Professional **$79/ay**, Business **$199/ay**; WhatsApp/Instagram/web inbox, periyodik bakim workflow | https://gorocketly.com/sektorler/oto-servis |
| **Sparkavis** | Google yorum uygulamasi | Free; Pro **9,99 EUR/ay**, Business **29,99 EUR/ay**; AI yanit, QR kod, widget | https://sparkavis.app/tr |
| **Nefalix** | Yorum + NPS + WhatsApp + itibar katmani | Baslangic **9.500 TL/ay** + **25.000 TL** kurulum; Profesyonel **14.900 TL/ay** + **50.000 TL** kurulum; Kurumsal **45.000 TL+/ay**; Sentinel **+3.500 TL/ay**, Recall **+2.500 TL/ay** | https://nefalix.com/fiyatlar |

**Gozlem:** Oto servis ERP rakipleri fiyat seffafliginde guclu ve aylik giris fiyatlari Nefalix'ten dusuk. Bu dogrudan "ucuz/pahali" kiyasina donmemeli; Nefalix'in sayfasi **ERP degil, servis sonrasi deneyim/yorum/WhatsApp/NPS katmani** olarak konumlanmali.

---

## 5) nefalix.com'da oto servis yuzeyi

Read-only smoke (2026-08-11):

| Yuzey | Durum |
|---|---|
| `/geo` | 200; bugunun `/geo/2026-08-11` sayfasi HTML'de h1 + SSS ile donuyor. |
| `/blog` | SSR index 200; `Yazilar yukleniyor` gorunmedi, blog linkleri HTML'de var. |
| `/blog` oto servis icerigi | Index'te en az iki oto servis blog basligi gorundu: `Oto Servislerde NPS ve Tekrar Ziyaret...` varyantlari. |
| `/geo` oto servis pillar | Bu repo `geo/` altinda oto servis markdown'i yok; mevcut 6 dosya saglik odakli. |
| Landing repo | Bu checkout'ta `nefalix-landing` yok; canli deploy veya landing degisikligi iddiasi yapilmaz. |

### Eksik / Faz 4 backlog

1. `oto servis NPS yazilimi` exact-match GEO.
2. `oto servis Google yorum yonetimi` GEO; genel Google yorum SaaS'larindan ayrismali.
3. `oto servis WhatsApp bakim hatirlatma` GEO; ERP/CRM farkini netlestirmeli.
4. `oto servis programi vs musteri deneyimi katmani` karsilastirmasi; OtoServiso/Mekaniq/ServisDefteri gibi ERP'leri adil anlatmali.
5. `yetkili servis musteri memnuniyet anketi` GEO; Pisano/akademik kaynaklarla desteklenmeli.
6. Review-gating ve yorum widget uyari kutusu; Esinix/Sparkavis ornekleri kaynakli ama Nefalix tavsiyesi politikalara uygun olmali.

---

## 6) Nefalix konumlandirma cikarimi (oto servis)

- **Kategori boslugu:** Oto servis SERP'i ERP/garaj programi ile dolu; servis sonrasi yorum + NPS + WhatsApp + itibar kriz alarmi tek sayfada anlatan dikey icerik zayif.
- **Rakip ayrimi:** OtoServiso/Mekaniq/ServisDefteri/OtoCore ana operasyon sistemi; Rocketly/Piyzi iletisim-CRM katmani; Restarun/Sparkavis/Esinix genel yorum araci; Pisano/Staffino kurumsal otomotiv CX. Nefalix bunlarin arasinda "servis sonrasi deneyim ve itibar otomasyonu" olarak durmali.
- **Fiyat mesaji:** ERP rakipleri daha dusuk aylik fiyatlarla gelir; Nefalix fiyatini "garaj programi yerine gecen yazilim" gibi anlatmak riskli. Dogru cevap: mevcut servis programina eklenen, yorum/NPS/WhatsApp/recall katmani.
- **Uyum mesaji:** Yorum daveti tum uygun musterilere gonullu ve tarafsiz gitmeli; "memnun -> Google, memnun degil -> ozel form" review-gating dili Nefalix GEO setinde kullanilmamali. Google yorum widget'i anlatilacaksa kaynak, tarih ve dogrulama/yeniden yayin uyarisi yazilmali.
- **Oto icin ilk GEO basliklari:** `Oto servislerde NPS nasil olculur?`, `Oto servis Google yorum yonetimi yazilimi ne ise yarar?`, `Periyodik bakim hatirlatmasi WhatsApp ile nasil kurulur?`, `Oto servis programi ile musteri deneyimi yazilimi ayni sey mi?`, `Yetkili servislerde dusuk puan alarmi nasil calismali?`

---

## 7) Director kapisi

**Onay.** Gerekce:

- Tekrar icerik: Bu dosya saglik/otel arastirma formatini izliyor ancak oto servis SERP, rakip ve kaynaklari ayridir; mevcut `geo/*.md` saglik kaliplariyla sayfa metni olarak cakismiyor.
- Cevap yapisi: Arastirma dosyasi oldugu icin answer-first GEO parcasi degil; ozet ve faz karari ilk bolumlerde net.
- Rakip iddialari: Fiyat/ozellik iddialari kaynak URL ile yazildi; yeniden fetch edilemeyen OtoCore icin "SERP/fetch snippet" siniri belirtildi.
- Review-gating: Esinix'teki secici yonlendirme yalnizca risk ornegi olarak kaydedildi; Nefalix icin onerilmedi.
- Google yorum widget: Sparkavis widget ornegi, dogrulama/uyari sartiyla not edildi.
- KVKK: Veri sorumlusu/isleyen ayrimi detayli islenmedi cunku bu arastirma oto servis odakli; sonraki GEO iceriklerinde "servis veri sorumlusu, Nefalix veri isleyen" cumlesi eklenmeli.
- Istatistik: Kaynaksiz pazar hacmi veya performans rakami kullanilmadi; rakiplerin kendi sitelerindeki fiyat/ozellikler kaynakli yazildi.

---

## 8) Kaynak logu

- `oto servis CRM yazilimi Turkiye servis takip programi fiyat`
- `oto servis musteri memnuniyet anketi yazilimi NPS Turkiye`
- `oto servis Google yorum yonetimi yazilimi`
- `oto servis WhatsApp otomasyon randevu hatirlatma yazilimi`
- `yetkili servis musteri memnuniyet anketi otomotiv NPS`
- Fetch: `otoserviso.com/fiyatlar`, `mekaniq.com.tr`, `bulutotoservis.com/bulut-otoservis-programi-ozellikleri.html`, `fieldco.com.tr/.../musteri-memnuniyet-anketi-teknik-servis-programi`, `pisano.com/tr/sektorel-cozumler/otomotiv`, `piyzi.com/sektorler/oto-servis-randevu-programi`, `gorocketly.com/sektorler/oto-servis`, `restarun.com`, `sparkavis.app/tr`, `esinix.com/itibar-yonetimi`, `servisdefteri.tr`, `nefalix.com/fiyatlar`

---

## 9) Siradaki faz

Faz 1 sektor arastirmasi bu dosyayla tamamlandi. Siradaki ana teslimat: **Faz 4 otel GEO seti** (`geo/*.md`), otel arastirmasindaki VoyageRespond / Akilli Isler / PMS ayrimini kaynakli ve director onayli kullanarak.
