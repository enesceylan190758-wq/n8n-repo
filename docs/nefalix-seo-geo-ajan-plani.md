# Nefalix — SEO/GEO Ön Araştırma & Ajan Operasyon Planı
*Hazırlanma tarihi: 29 Temmuz 2026*

> **Repo konumu:** `docs/nefalix-seo-geo-ajan-plani.md` (kaynak: Downloads kopyası).  
> **Canlı sistem çapraz kontrolü:** [`nefalix-seo-geo-gap-notes.md`](nefalix-seo-geo-gap-notes.md) — Faz 0: içerik var (24 GEO + 24 blog); indeks sayfaları client-side, detay GEO SSR.

---

## 0) Özet

MediDent için kurduğumuz mantık (araştırma → yönetici ajan → içerik ajanları → uyum kontrolü → yayınla & izle) **doğrudan taşınabilir**, çünkü ikisi de aynı temel probleme çözüm arıyor: doğru soruyu, doğru kanıtla, tekrarsız cevaplamak. Ama Nefalix, MediDent'ten **iş modeli olarak tamamen farklı**:

| | MediDent | Nefalix |
|---|---|---|
| Kime satıyor | Hastaya (B2C) | Klinik/otel/oto servis sahibine (B2B SaaS) |
| Pazar | DE / UK / TR hasta | Türkiye (TR odaklı, KVKK + yerel barındırma) |
| "Pazar" ayrımı | Ülke/dil | **Sektör** (Sağlık, Otel, Oto Servis) |
| En büyük risk | Sağlık turizmi reklam yönetmeliği | Google/yorum platformu politikaları + KVKK özel nitelikli veri |
| İçerik amacı | Hasta ikna etmek | Klinik/otel yöneticisini ikna etmek (demo/pilot) |

Bu belge önce sitede bulduğum somut durumu, sonra 3 sektör için gerçek rakip/anahtar kelime bulgularını, sonra uyarlanmış ajan mimarisini ve Cursor'a yapıştırılabilir promptları veriyor.

---

## 1) Sitede bulduğum durum (kanıt)

`nefalix.com/geo` ve `nefalix.com/blog` sayfalarını inceledim. İyi haber: **GEO mimarisi zaten MediDent'teki mantıkla kurulmuş** — "AI Alıntı Paketleri", "doğrudan cevap + SSS + iç link" formatı, "answer-first" video açıklamaları. Bu doğru yönde bir başlangıç.

Ama şu an her iki sayfada da içerik alanları **"Yazılar yükleniyor…" / "Paketler yükleniyor…"** yazısıyla boş görünüyor — benim erişimimden (statik sayfa çekme) hiçbir gerçek makale veya GEO paketi görünmedi. Bunun iki olası nedeni var ve agent'ın işe başlamadan önce **hangisi olduğunu netleştirmesi lazım**:

1. İçerik gerçekten hiç yayınlanmamış (API'den veri gelmiyor çünkü henüz veri yok).
2. İçerik var ama tarayıcı tarafında (client-side) JS ile geç yükleniyor ve benim kullandığım araç bunu göremiyor.

**Acil eylem (Faz 0):** Agent önce gerçek tarayıcıda (veya CMS/admin panelinden) `/blog` ve `/geo` sayfalarında kaç yazı/paket olduğunu doğrulamalı. Eğer (2) ise, bu durum **Google'ın ve AI motorlarının crawler'ları için de risk** taşır — çoğu crawler JS render etmez veya geç/eksik render eder; yani bugün "boş" görünen bu sayfalar hem geleneksel SEO'da hem GEO'da hiç görünmüyor olabilir. Bu, MediDent'teki "şablon tekrarı" bulgusundan farklı ama eşit derecede acil bir teknik risk: **içerik var olsa bile hiç indekslenmiyor olabilir.**

**Kontrol listesi:**
- [ ] `/blog` ve `/geo` gerçekte kaç yazı/paket barındırıyor (CMS'den doğrula)
- [ ] Google Search Console'da bu URL'ler "indexed" mi "crawled - discovered" mı
- [ ] `curl` ile (JS çalıştırmadan) sayfa çekildiğinde içerik gerçekten boş mu geliyor — geliyorsa **server-side rendering veya prerendering şart**
- [ ] Sitemap'te bu sayfalar var mı

---

## 2) Sektör bazlı pazar araştırması — gerçek bulgular

Nefalix üç sektörü hedefliyor (Sağlık Kurumları, Oteller, Auto Servisler), ama `/kaynaklar` sayfası "SAĞLIK TURİZMİNE ÖZEL PLATFORM" başlığıyla açılıyor ve akademik bir referans (Buzcu & Birdir, 2019, Gaziantep Üniversitesi — 206 özel hastane yöneticisi araştırması) kullanıyor. Bu, **sağlık/klinik sektörünün şu anki asıl kapı (beachhead) pazar** olduğunu gösteriyor — MediDent'in kendisi de dahil olmak üzere tam da bu sektöre satılıyor olabilir. Aşağıdaki araştırma bu önceliği yansıtacak şekilde sağlık sektörüyle başlıyor, sonra otel ve oto servis geliyor.

### 2.1 SAĞLIK KURUMLARI (öncelikli sektör)

**Anahtar kelime öbekleri:**
| Kelime öbeği | Niyet |
|---|---|
| klinik itibar yönetimi yazılımı | Ana ticari sorgu |
| hasta deneyimi yönetim platformu | Kategori arama |
| Google yorum yönetimi yazılımı | Fonksiyon bazlı |
| hasta geri bildirim otomasyonu | Fonksiyon bazlı |
| HBYS entegrasyonu WhatsApp | Teknik/entegrasyon sorgusu |
| hasta recall / kayıp hasta geri kazanım yazılımı | Nefalix'in "Recall" ürününe birebir eşleşme |
| NPS yazılımı sağlık sektörü | Ölçüm odaklı |
| diş kliniği / saç ekimi merkezi itibar yönetimi | Branş bazlı long-tail |
| olumsuz yorum kriz yönetimi klinik | "Sentinel" ürününe birebir eşleşme |
| kliniğim için WhatsApp otomasyon | Yerel esnaf dili |

**Gerçek rakipler ve konumları:**
- **klinikitibar.com** — En doğrudan rakip. Diş klinikleri ve saç ekimi merkezleri için itibar yönetimi sunuyor, sağlık turizmi hastaları için Yandex (Rusya/BDT) optimizasyonuna kadar iniyor. Ama **insan/ajans modeli** (yazılım değil hizmet) — Nefalix'in "self-serve AI platform + 1 hafta kurulum" konumlanması burada net bir fark yaratıyor.
- **isletmeitibar.com** — Olumsuz yorum kaldırma/itibar temizleme odaklı, "başarısız olursa ödeme yok" garantili hizmet modeli. Nefalix'in Sentinel modülüyle kısmen örtüşüyor ama yine ajans hizmeti, yazılım değil.
- **DentSoft, Medicasimple, bulutklinik, KlinikYonetimi.com, Clinall** — Bunların hepsi **HBYS/randevu/hasta kayıt** yazılımı; itibar/WhatsApp/NPS bunlarda ya yok ya da yan özellik. Nefalix'in "HBYS'nizle entegre olur, HBYS'nizin yerine geçmez" mesajı burada net bir konumlandırma boşluğu dolduruyor.
- **Global oyuncular (Birdeye, Podium)** — ABD merkezli, 200.000+ işletmeye hizmet veriyorlar ama fiyat $299-399+/ay'dan başlıyor, KVKK/Türkiye veri barındırma yok, Türkçe NLP kalitesi belirsiz. "Yerel + KVKK uyumlu + TL fiyatlandırma" burada Nefalix'in doğal karşı-argümanı.

**Kaynak siteler:** klinikitibar.com, isletmeitibar.com, dentsoft.com.tr, medicasimple.com, bulutklinik.com, klinikyonetimi.com, klinik.clinall.com, birdeye.com, g2.com

### 2.2 OTELLER

**Anahtar kelime öbekleri:**
| Kelime öbeği | Niyet |
|---|---|
| otel yorum yönetimi yazılımı | Ana ticari sorgu |
| TripAdvisor Booking Google yorum tek panel | Fonksiyon/entegrasyon |
| otel itibar yönetimi AI | Kategori + teknoloji |
| misafir deneyimi platformu | Kategori |
| otel NPS / GRI (Guest Review Index) yazılımı | Ölçüm |

**Gerçek rakipler:**
- **VoyageRespond** — **En güçlü doğrudan rakip.** Türkiye merkezli, otel/restoran odaklı, çok dilli AI yanıt üretimi (bir Antalya otelinin Rusça/Almanca yorumlarını otomatik tespit edip aynı dilde marka tonunda cevap taslağı hazırlıyor), TripAdvisor'ın API kısıtlamasına uyumlu "Copy & Confirm" paterni kullanıyor (toplu otomatik yanıt yok — TOS ihlali riski taşımıyor). Kendi sitesinde **"En İyi Yorum Yönetim Araçları 2026: 12 Platform Karşılaştırması"** başlıklı bir karşılaştırma sayfası var — bu format (rakip karşılaştırma tablosu) GEO/SEO'da çok güçlü çalışıyor ve Nefalix'in de üretmesi gereken bir içerik türü.
- **TrustYou / ReviewPro (Shiji)** — Enterprise, 50+ otelli zincirler için sektör standardı, aylık ~€2.000+, küçük/orta ölçekli oteller için aşırı kapsamlı ve pahalı.
- **MARA Solutions** — Avrupa odaklı, €39-199/lokasyon/ay, iyi AI yanıt kalitesi ama Türkiye'ye özel değil.
- **Reviewly.ai** — Sadece Google, $29-99/ay, ucuz ama dar kapsamlı.
- **Protel, Elektraweb, DİA** — Bunlar **PMS (Property Management System)** — rezervasyon/ön büro/muhasebe odaklı, itibar yönetimi yan özellik ya da yok.

**Kaynak siteler:** voyagerespond.com, protel.com.tr, elektraweb.com, dia.com.tr, hmsotel.com

### 2.3 AUTO SERVİSLER

**Anahtar kelime öbekleri:**
| Kelime öbeği | Niyet |
|---|---|
| oto servis müşteri deneyimi yazılımı | Ana sorgu |
| oto servis CRM yazılımı | Kategori |
| oto servis Google yorum yönetimi | Fonksiyon |
| yetkili servis müşteri memnuniyet anketi | NPS/ölçüm |
| oto servis WhatsApp otomasyon | Fonksiyon |

**Gerçek rakipler:**
- **Canbus, Mysoft, caneke.com, değeryazilim, ESN Sistem, İo Medya** — Bu sektörde bulduğum tüm oyuncular **CRM/ERP odaklı** (araç geçmişi, iş emri, parça/stok, fatura, randevu hatırlatma). Bazılarında "memnuniyet anketi" yan modül olarak var (Mysoft), ama **AI destekli çok kanallı itibar/WhatsApp inbox + kriz alarmı hiçbirinde yok.**

**Sonuç:** Auto servis sektörü, üç sektör içinde **en az doymuş, en büyük boşluk** olan alan — burada gerçek bir "AI itibar + WhatsApp" rakibi bulamadım. Bu hem fırsat (rekabetsiz alan, hızlı SEO/GEO kazancı) hem risk (sektörün bu tür bir çözüme "hazır" olup olmadığı belirsiz, önce talep doğrulaması gerekebilir).

**Kaynak siteler:** canbus.net.tr, mysoft.com.tr, caneke.com.tr, degeryazilim.com, esnsistem.com, yazilimlar.iomedya.com

### 2.4 Ortak konumlandırma çıkarımı

Üç sektörde de gördüğüm ortak desen: **rakipler ya tek-fonksiyonlu (sadece yorum, ya da sadece CRM, ya da sadece PMS) ya da çok pahalı/global enterprise.** Nefalix'in "yorum + WhatsApp + NPS + recall + kriz alarmı tek panelde, KVKK uyumlu, Türkiye'de barındırılan" konumu gerçek bir boşluğu dolduruyor — ama bu farkı içerikte **somut ve tekrar tekrar** göstermek gerekiyor (bkz. §5, karşılaştırma sayfaları).

---

## 3) GEO'da (yapay zekada görünürlük) gerçekten işe yarayanlar — B2B SaaS'a uyarlanmış

MediDent'teki ilkeler burada da geçerli, üç ek nüansla:

- **Schema:** FAQPage + **SoftwareApplication/Product** schema (fiyat, özellik listesi, entegrasyonlar) — B2B alıcı genelde "X yazılımı ne kadar" diye soruyor, bu şema doğrudan cevap veriyor.
- **Karşılaştırma sayfaları en değerli GEO içeriği.** VoyageRespond'un "12 Platform Karşılaştırması" örneği gösteriyor ki bu format hem trafik hem AI-alıntı açısından güçlü. Nefalix için: "Nefalix vs Birdeye/Podium", "Nefalix vs klinikitibar.com (yazılım vs ajans hizmeti)", "En iyi klinik itibar yönetimi yazılımları 2026" gibi sayfalar üretilmeli — ama rakip adı geçen her sayfa **iddialar doğrulanabilir olmalı, aşağılayıcı olmayacak şekilde yazılmalı** (bkz. §5, hukuki not).
- **Somut sayı/vaka kanıtı.** `/kaynaklar` sayfasındaki akademik atıf (Buzcu & Birdir 2019) ve "%86,9 tedavi sonrası hiç takip yok" gibi rakamlar, GEO'da çok değerli — AI motorları isimlendirilebilir, atıf yapılabilir istatistikleri alıntılamaya eğilimli. Bu tarz veri noktaları her sektöre (otel, oto servis) özel olarak da bulunmalı/üretilmeli.

---

## 4) Yasal/uyum uyarısı — bir hukuk danışmanına sorulması gereken noktalar

*(Ben avukat değilim, bu hukuki tavsiye değildir — dikkatini çekmek istediğim gerçek bulgular.)*

MediDent'te sağlık turizmi reklam yönetmeliği risk noktasıydı; Nefalix'te üç farklı ve gerçek risk alanı buldum:

**a) Reklam Kurulu'nun "üçüncü taraf sitede doğrulanmamış yorum" kararı (Şubat 2025).** Ticaret Bakanlığı Reklam Kurulu, üçüncü taraf ticari web sitelerinde doğrulanamayan tüketici yorumlarının yayınlanmasını haksız ticari uygulama sayarak 183 dosyaya toplam 30,2 milyon TL ceza ve bazılarına erişim engeli kararı verdi. Google bunun kendi yorum sistemini etkilemediğini, yalnızca **başka sitelerin Google yorumlarını kendi ticari sitesinde yeniden yayınlamasını** hedeflediğini açıkladı. **Neden önemli:** Nefalix'in ürünü müşteri kliniklerin kendi web sitelerinde Google yorumlarını widget olarak gösteriyorsa (yaygın bir SaaS özelliği), bu tam olarak kararın hedeflediği senaryo olabilir. Agent'ın önce ürünün bu özelliği gerçekten sunup sunmadığını, sunuyorsa hangi doğrulama/uyarı mekanizmasıyla sunduğunu netleştirmesi gerekiyor.

**b) Google'ın "sahte etkileşim" politikası.** Google, yorum karşılığı indirim/ücretsiz hizmet gibi teşvik sunmayı veya olumsuz yorumun kaldırılması karşılığı teşvik vermeyi kesinlikle yasaklıyor; ihlal eden işletme profillerine yorum alma kısıtlaması geliyor. **Neden önemli:** Nefalix'in "Akıllı Geri Bildirim" ürünü, memnun hastaları otomatik olarak yorum bırakmaya yönlendiriyor — bu meşru ve yaygın bir pratik (Google'ın kendi "daha fazla yorum alma ipuçları" sayfası da bunu öneriyor), ama akışın hiçbir noktasında **seçici filtreleme** (yalnızca olumlu sinyal verenlere davet gönderip olumsuz olanları göndermeme — "review gating") yapılmamalı; bu, Google politikasında gri alan ve FTC/tüketici otoritelerinde bazı ülkelerde açıkça yasaklanmış bir pratik. Ürünün NPS-bazlı segmentasyonunun ("Memnun hasta → yorum daveti" / "NPS 6 ve altı → yöneticiye görev") bu sınırı nasıl yönettiği net şekilde belgelenmeli.

**c) KVKK — sağlık verisi "özel nitelikli kişisel veri" kategorisinde.** WhatsApp/inbox üzerinden gelen bir hasta mesajı ("zirkonyum kaplama sorusu geldi" gibi demo panelde gördüğüm örnek) dolaylı olarak sağlık verisi taşıyabilir. KVKK'ya göre sağlık verisi, açık rıza olmadan yalnızca sır saklama yükümlülüğü altındaki sağlık personeli/kurumu tarafından belirli amaçlarla işlenebilir. **Neden önemli:** Nefalix burada müşteri kliniğin "veri işleyeni" konumunda — asıl KVKK yükümlülüğü (açık rıza metni, aydınlatma metni) müşteri klinikte olsa da, Nefalix'in pazarlama materyalinde ve ürün sözleşmesinde bu sorumluluk ayrımının (veri sorumlusu = klinik, veri işleyen = Nefalix) net olması, hem hukuki hem güven açısından kritik.

**Öneri:** İçerik üretimine başlamadan önce bir KVKK/reklam hukuku danışmanına şunları sor: (1) Google yorum widget'ı özelliği varsa Reklam Kurulu kararı kapsamına girip girmediği, (2) NPS-bazlı seçici yorum daveti akışının "review gating" sınırını aşıp aşmadığı, (3) veri sorumlusu/veri işleyen ayrımının kullanıcı sözleşmesinde ve pazarlama sayfalarında tutarlı yansıtılıp yansıtılmadığı.

---

## 5) Düzeltilmiş/uyarlanmış ajan mimarisi

MediDent'teki 5 aşamalı hat aynı iskelet, farklı girdi/çıktılarla:

| # | Aşama | Nefalix'e özel görevi | Kritik kural |
|---|---|---|---|
| 1 | **Araştırma katmanı** | Sektör bazlı (Sağlık / Otel / Oto Servis) gerçek arama hacmi, rakip konumlanması, karşılaştırma verisi (fiyat, özellik) | Gerçek veri kaynağı şart — rakip fiyatları/özellikleri tahmin edilmemeli, kaynağı gösterilmeli |
| 2 | **Yönetici ajan (director)** | Araştırmayı content brief'e çevirir: hangi sektör, hangi sayfa türü (GEO SSS / karşılaştırma / vaka çalışması / playbook), hangi kanıt (akademik atıf, müşteri verisi, demo ekran görüntüsü) | Rakip adı geçen her brief'te "iddia doğrulanabilir mi" kontrolü zorunlu |
| 3 | **İçerik ajanları** | Brief'ten orijinal metin üretir | Kopyalama yok; VoyageRespond tarzı karşılaştırma sayfaları dahil her sayfa kendine özgü |
| 4 | **Uyum & kalite kontrolü** | Tekrar-içerik taraması, schema kontrolü + **§4'teki 3 hukuki risk noktasının her sayfada kontrolü** (rakip aşağılama yok, review-gating iması yok, KVKK sorumluluk ayrımı doğru) | Yayından önce son kapı |
| 5 | **Yayınla & izle** | GSC/GA4 + aylık "ChatGPT/Perplexity'ye 'en iyi klinik itibar yönetimi yazılımı' sor, Nefalix çıkıyor mu" testi | Sonuçlar aşama 1'e geri besleniyor |

---

## 6) Cursor'a yapıştırılabilir — Yönetici Ajan (Director) master promptu

```
Sen Nefalix için SEO/GEO içerik operasyonunun yönetici (director) ajanısın.
Görevin içerik üretmek değil, üretilen her parçayı yayına çıkmadan önce denetlemek.

BAĞLAM: Nefalix, klinikler (diş/saç ekimi/estetik/hastane), oteller ve oto servisler için
Google yorum yönetimi, WhatsApp/inbox, NPS/eNPS, recall ve itibar kriz alarmını tek panelde
birleştiren bir B2B SaaS platformudur. Türkiye odaklı, KVKK uyumlu, veriler Türkiye'de barınır.

GİRDİ: Bir araştırma ajanından gelen sektör bazlı content brief + bir içerik ajanından gelen taslak metin.

REDDET ve düzelt iste, eğer:
1. Taslak, sitedeki başka bir sayfayla (özellikle /geo/ altındaki paketlerle) %30'dan fazla
   cümle/kalıp benzerliği taşıyorsa.
2. Taslak, hedef sorunun cevabını ilk 2 cümlede vermiyorsa (GEO için parça-bazlı okunabilirlik şart).
3. Taslak bir rakibi (Birdeye, Podium, VoyageRespond, klinikitibar.com vb.) adıyla anıyorsa VE
   iddia doğrulanabilir bir kaynağa dayanmıyorsa veya aşağılayıcı/haksız rekabet tonu taşıyorsa.
4. Taslak, "yorum karşılığı indirim/hediye" ima eden veya seçici (yalnızca memnun müşteriye)
   yorum daveti gönderimini pazarlama diliyle övüyor gibi okunan bir ifade içeriyorsa (review-gating
   izlenimi — Google politikasına aykırı algı riski).
5. Taslak, Nefalix'in Google yorumlarını müşteri sitesinde yeniden yayınlama (widget) özelliğini
   anlatıyorsa VE doğrulama/uyarı mekanizmasından bahsetmiyorsa (Reklam Kurulu Şubat 2025 kararı riski).
6. Taslak, veri sorumlusu (klinik/otel/servis) ile veri işleyen (Nefalix) ayrımını bulanıklaştırıyorsa
   veya KVKK/sağlık verisi konusunda kesin/abartılı bir güvence veriyorsa.
7. Taslakta bir istatistik/akademik atıf varsa ve kaynağı isimlendirilmemişse.

ONAYLA, eğer:
- Cevap ilk cümlede net, sonrası kanıt/detay.
- FAQ/Schema formatına uygun (soru = H2/H3, cevap = ilk paragraf).
- Hedef sektör (Sağlık/Otel/Oto Servis) doğru ve o sektörün gerçek arama kalıbına uygun.
- Rakip karşılaştırmaları varsa, adil ve doğrulanabilir (fiyat/özellik kaynağı belirtilmiş).
- Sitedeki diğer sayfalarla anlamlı şekilde farklı.

ÇIKTI: Onay / Red + gerekçe + (red ise) hangi maddenin düzeltilmesi gerektiği.
Kararını her zaman kısa bir gerekçe ile ver, sessizce onaylama veya reddetme.
```

---

## 7) Araştırmacı ajan promptu (örnek — Sağlık sektörü için)

```
Görev: Sağlık kurumları (diş, saç ekimi, estetik, hastane) sektöründe Türkiye'deki
"klinik itibar yönetimi / hasta deneyimi otomasyonu" temalı gerçek arama davranışını araştır.
Zorunlu: Yalnızca gerçek web arama/SERP verisine dayan, tahmin üretme.
Çıktı formatı:
- En çok aranan 10 kelime öbeği (Türkçe)
- Bu kelimelerde şu an kim sıralanıyor (ilk 5 sonuç, marka adı + iş modeli: yazılım mı ajans mı +
  neden sıralandığı)
- Bu kelimeler etrafında sorulan 5 alt soru (People Also Ask / forum)
- Rakiplerin fiyatlandırma/özellik şeffaflığı nasıl (varsa somut rakam)
- Nefalix'in bu konuda şu an hangi sayfası var (/geo/, /blog/, /kaynaklar/ içinde), hangisi eksik
```
(Otel ve Oto Servis sektörleri için aynı şablonu sektöre özel terimlerle kopyala — bkz. §2.2 ve §2.3'teki kelime listeleri.)

---

## 8) Uygulama fazları

- **Faz 0 (bu hafta):** `/geo/` ve `/blog/` sayfalarının gerçekten boş mu yoksa JS-render sorunu mu olduğunu netleştir (bkz. §1 kontrol listesi). Bu çözülmeden üretilecek hiçbir içerik görünür olmaz.
- **Faz 1:** Sağlık sektörü için gerçek anahtar kelime + rakip haritasını çıkar (öncelik, çünkü `/kaynaklar` sayfası zaten bu sektöre kilitlenmiş görünüyor) — ardından Otel, ardından Oto Servis.
- **Faz 2:** Sağlık sektörü için 5-10 GEO sayfası (itibar yönetimi, HBYS entegrasyonu, recall, NPS, kriz yönetimi konularında) + FAQPage/SoftwareApplication schema.
- **Faz 3:** Rakip karşılaştırma sayfaları (§5, madde 3 kuralına tabi — hukuki onaydan geçmiş) — "Nefalix vs [kategori]" formatında, VoyageRespond'un kendi kategorisinde yaptığı gibi.
- **Faz 4:** Otel ve Oto Servis sektörleri için aynı GEO+karşılaştırma seti.
- **Faz 5:** Aylık ölçüm ve iterasyon — ChatGPT/Perplexity/Gemini'ye "en iyi klinik itibar yönetimi yazılımı Türkiye" gibi sorular sorup Nefalix'in çıkıp çıkmadığını test et.

---

## 9) Takip metrikleri

- Google Search Console: sektör bazlı (Sağlık/Otel/Oto Servis) sorgu/tıklama/pozisyon.
- GA4: sektör sayfası bazlı trafik ve demo talebi dönüşümü.
- Aylık manuel test: AI motorlarına sektör bazlı "en iyi X yazılımı" sorusu sor, Nefalix çıkıyor mu kontrol et.
- `/geo` ve `/blog` sayfalarının Search Console'da gerçekten "indexed" durumuna geçtiğini doğrula (Faz 0'ın başarı ölçütü).

---

*Not: Bu rapor gerçek web arama sonuçlarına dayanır; tahmini/uydurma veri içermez. Rakip sitelerden birebir metin alınmamış, yalnızca yapı/strateji/kalıp/fiyat bilgisi (kaynağı belirtilerek) anlatılmıştır.*
