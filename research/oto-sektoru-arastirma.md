# Oto sektoru — servis CRM / yorum / musteri deneyimi arama arastirmasi

**Tarih:** 2026-09-29  
**Kapsam:** Turkiye · oto servis, yetkili servis, bayi servis, garaj / atölye  
**Tema:** oto servis CRM + Google yorum yonetimi + WhatsApp / randevu / memnuniyet otomasyonu  
**Yontem:** Canli web arama / SERP + sayfa fetch. Keyword Planner / Ahrefs hacim API'si yok; "en yogun" siralama = bu oturumda gozlenen **SERP ticari yogunlugu + sorgular arasi tekrar**. Sayisal hacim iddiasi yapilmaz.  
**Plan referansi:** `docs/nefalix-seo-geo-ajan-plani.md` §2.3 · Faz 1 (saglik + otel sonrasi oto)

---

## 1) Yogun ticari sinyalli kelime obekleri (Turkce)

| # | Obek | SERP karakteri | Ornek sorgu |
|---|------|----------------|-------------|
| 1 | `oto servis CRM yazilimi` | CRM / servis sureci yazilimi; Rapitek, OzgurKod, OvoCRM | `oto servis CRM yazilimi` |
| 2 | `oto servis programi` / `oto servis yazilimi` | Is emri, stok, muhasebe, SMS; Canbus, ESN, OtoWeb, Otevis | `oto servis programi fiyat` |
| 3 | `oto servis randevu programi` | Randevu + bakim hatirlatma + kasa; Piyzi, Caneke, Rocketly | `oto servis randevu programi` |
| 4 | `oto servis Google yorum yonetimi` | Daha dar ama ticari; Carzi, Jetyorum, Piyzi, Esinix | `oto servis Google yorum yonetimi yazilimi` |
| 5 | `oto servis WhatsApp otomasyon` | Randevu, parca onayi, teslim bildirimi; OzgurKod, Rapitek, Otevis, FormFabrikasi | `oto servis WhatsApp otomasyon` |
| 6 | `yetkili servis yazilimi` | Bayi / yetkili servis agi; Canbus, ESN | `yetkili servis yazilimi musteri memnuniyet` |
| 7 | `arac servis takip programi` | Arac gecmisi, is emri, stok ve e-fatura | `arac servis takip programi` |
| 8 | `servis sonrasi memnuniyet anketi` | Teknik servis geneli; FieldCo, Servis Pozitif, Canbus | `teknik servis musteri memnuniyet anketi` |
| 9 | `bakim hatirlatma otomasyonu oto servis` | Periyodik bakim / kilometre / recall benzeri akilar | `oto servis bakim hatirlatma WhatsApp` |
| 10 | `oto bayi yorum yonetimi` | Jetyorum gibi itibar / widget cozumleri | `otomobil servisi bayi yorum yonetimi` |

**Nefalix gorunurlugu:** `site:nefalix.com oto servis` ve marka disi oto sorgularinda bu oturumda Nefalix'in public yuzeyi yalnizca ana sayfa, `/sektorler` ve `/fiyatlar` olarak gorundu. `/sektorler` sayfasi auto servisleri yol haritasi olarak anar; otoya ozel GEO/pillar sayfasi bu repo icinde yok.

---

## 2) Kim siralaniyor? (ornek SERP'ler)

### 2.1 `oto servis CRM yazilimi`

| # | Marka / site | Model | Neden siralaniyor |
|---|--------------|-------|-------------------|
| 1 | **OzgurKod** — [ozgurkod.com/cozumler/oto-servis](https://ozgurkod.com/cozumler/oto-servis) | Yazilim (CRM + WhatsApp / satis otomasyonu) | "Aracim ne durumda?" trafigi, fotografli parca onayi, pipeline ve tek gelen kutusu anlatimi |
| 2 | **Rapitek** — [rapitek.com/oto-servis-crm](https://rapitek.com/oto-servis-crm/) | Yazilim (kurulumlu CRM) | Arac karti, is emri, parca hareketi, bakim hatirlatmasi ve takim WhatsApp gelen kutusu |
| 3 | **OvoCRM** — [ovocrm.com/sektorler/oto-servis](https://www.ovocrm.com/sektorler/oto-servis) | Yazilim (operasyon / CRM) | Arac parki, is emri, yedek parca stok, periyodik bakim hatirlatma |
| 4 | **OtoWeb** — [otoweb.com.tr](https://www.otoweb.com.tr/) | Yazilim (servis yonetimi) | QR, AI veri girisi, WhatsApp / SMS otomasyonu ve musteri portali SERP snippet'lerinde gorundu |
| 5 | **Otevis** — [otevis.com](https://otevis.com/) | Yazilim (offline / cihazda veri) | Verinin cihazda kalmasi, bakim hatirlatici, randevu ve servis takip linki |

### 2.2 `oto servis programi` / `arac servis takip programi`

| # | Marka / site | Model | Neden siralaniyor |
|---|--------------|-------|-------------------|
| 1 | **Canbus** — [servisyazilim.com](https://servisyazilim.com/) | Yazilim (bulut servis programi) | Arac kabul, is emri, stok, CRM, kasa / on muhasebe ve SMS bilgilendirme tek platform |
| 2 | **ESN Sistem** — [esnsistem.com/urunler/oto-servis-programi](https://www.esnsistem.com/urunler/oto-servis-programi) | Yazilim (CRM + teknik servis) | Arac karti, iscilik / parca, e-fatura, mobil saha kaydi |
| 3 | **Otevis** | Yazilim (tek seferlik lisans) | Offline calisma, cihazlar arasi sifreli senkron, Google Drive yedekleme |
| 4 | **OtoWeb** | Yazilim | QR servis gecmisi, musteri portali, WhatsApp / SMS otomasyonu |
| 5 | **Can Eke** — [caneke.com.tr/oto-servis-yazilimi](https://caneke.com.tr/oto-servis-yazilimi/) | Yazilim / rehber | Randevu, online randevu ve otomatik hatirlatma konulariyla uzun form icerik |

### 2.3 `oto servis randevu programi` / bakim hatirlatma

| # | Marka / site | Model | Neden siralaniyor |
|---|--------------|-------|-------------------|
| 1 | **Piyzi** — [piyzi.com/sektorler/oto-servis-randevu-programi](https://piyzi.com/sektorler/oto-servis-randevu-programi) | Yazilim | Randevu takvimi, arac bakim gecmisi, is emri, periyodik bakim hatirlatmasi ve kasa |
| 2 | **Rocketly** — [gorocketly.com/sektorler/oto-servis](https://gorocketly.com/sektorler/oto-servis) | Yazilim (CRM katmani) | Randevu, ariza talebi, teklif onayi, teslim bildirimi; servis programinin yerine degil yaninda konum |
| 3 | **OzgurKod** | Yazilim (CRM) | Online randevu sayfasi, Google Takvim senkronu, WhatsApp / SMS hatirlatma |
| 4 | **Otevis** | Yazilim | Web sitesinden randevu alma, periyodik bakim icin WhatsApp / e-posta hatirlatmasi |
| 5 | **FieldCo** — [fieldco.com.tr/.../musteri-memnuniyet-anketi](https://www.fieldco.com.tr/tr/blog/teknikservisprogrami/musteri-memnuniyet-anketi-teknik-servis-programi) | Yazilim (teknik servis geneli) | Is emri kapandiktan 2 saat sonra SMS/e-posta memnuniyet anketi; otoya komsu teknik servis SERP'i |

### 2.4 `oto servis Google yorum yonetimi`

| # | Marka / site | Model | Neden siralaniyor |
|---|--------------|-------|-------------------|
| 1 | **Carzi** — [carzi.com.tr/ozellikler/google-yorum-yonetimi](https://carzi.com.tr/ozellikler/google-yorum-yonetimi) | Yazilim (oto servis + Google yorum) | Google Business Profile yorumlarini operasyon ekraninda toplar; yanit yayini kullanici onayiyla olur |
| 2 | **Piyzi** — [piyzi.com/ozellikler/google-yorum-kazandirma](https://piyzi.com/ozellikler/google-yorum-kazandirma) | Yazilim (yorum talebi otomasyonu) | Randevu sonrasi yorum talebi ve segment filtreleri; sayfada review-gating riski doguran ifadeler var |
| 3 | **Jetyorum** — [jetyorum.com/otomobil-servisleri-bayileri](https://www.jetyorum.com/otomobil-servisleri-bayileri) | Yazilim (itibar / yorum / widget) | Bayi ve servisler icin yorum toplama, sosyal paylasim, widget, tek panel yanit |
| 4 | **Esinix** — [esinix.com/itibar-yonetimi](https://esinix.com/itibar-yonetimi) | Yazilim (itibar) | Google/Facebook yorum takibi, SMS/WhatsApp yorum talebi; SERP snippet'inde memnun/memnun degil ayrimi |
| 5 | **FormFabrikasi** — [formfabrikasi.com](https://formfabrikasi.com/) | Hizmet / otomasyon paketi | Oto servis dijital paketi, WhatsApp randevu ve "itibar filtresi" dili |

**Director notu:** Bu alt SERP'te bazi rakip sayfalar "sadece mutlu/memnun musteri Google'a, memnun olmayan ozel forma" dilini acik kullaniyor. Nefalix icerigi bu dili tekrar etmemeli; Google yorum daveti gonullu, tesviksiz ve ayrimci olmayan operasyon kuralina baglanmali.

---

## 3) Alt sorular (PAA benzeri + sayfa SSS/H2)

1. Oto servis CRM'i, stok / muhasebe programinin yerine mi gecer, yaninda mi calisir? — Rapitek ve Rocketly sayfalari CRM'i operasyon / iletisim katmani olarak ayiriyor.
2. Periyodik bakim hatirlatmasi kilometreye mi, tarihe mi, son is emrine mi baglanmali? — Rapitek, OvoCRM, Otevis, Piyzi.
3. Musteri "aracim ne durumda?" diye aramadan durumu nasil gorur? — Otevis servis takip linki, OtoWeb QR / musteri portali, Canbus SMS.
4. Google yorum yaniti otomatik mi yayinlanir, kullanici onayi gerekir mi? — Carzi, yayinlama isleminin otomatik olmadigini ve kullanicinin acikca onayladigini yazar.
5. Servis sonrasi memnuniyet anketi ne zaman gonderilmeli? — FieldCo is emri kapandiktan 2 saat sonra SMS/e-posta modeli anlatir.
6. Google yorum talebi herkese mi gider? — Piyzi "segment filtreleri" ve "kotu deneyim yasamis musteri elenebilir" der; bu ifade Nefalix director kapisinda review-gating riski olarak isaretlenmeli.
7. Google yorum widget'i web sitesinde gosterilecekse dogrulama / guncellik nasil saglanir? — Jetyorum widget ve zengin snippet vaadi verir; Nefalix iceriginde Reklam Kurulu / dogrulama uyarisi olmadan bu ozellik ovulmemeli.

---

## 4) Rakiplerde fiyat / ozellik seffafligi (somut kaynak)

| Rakip | Tip | Public fiyat | Kaynak / not |
|-------|-----|--------------|--------------|
| **Canbus** | Yazilim (bulut oto servis programi) | Demo ucretsiz; Standart **149 TL/ay'dan**, Uzman **249 TL/ay'dan** baslar; 30 gun deneme | [servisyazilim.com](https://servisyazilim.com/) fetch 2026-09-29 |
| **Otevis** | Yazilim (tek seferlik lisans + yillik) | Coklu Kullanici temel lisans **30.000 TL** (lansman ozel %50 indirim iddiasi sayfada), **5.000 TL + 2.500 TL/yil**; KDV dahil degil; Kurumsal ozel fiyat | [otevis.com](https://otevis.com/) fetch 2026-09-29 |
| **Rapitek Oto Servis CRM** | Yazilim (kurulumlu CRM) | Bu fetch'te net paket fiyati yok; kurulum / aktarim / entegrasyon bedeli kesif gorusmesinde yazili paylasilir | [rapitek.com/oto-servis-crm](https://rapitek.com/oto-servis-crm/) |
| **ESN Sistem** | Yazilim (CRM + teknik servis) | Oto servis sayfasinda public tutar yok; SSS'de lisans bedeli kullanici sayisi ve modul secimine gore degisir, iletisim denir | [esnsistem.com/urunler/oto-servis-programi](https://www.esnsistem.com/urunler/oto-servis-programi) + SERP SSS |
| **Carzi Google Yorum Yonetimi** | Yazilim (oto servis + Google yorum) | Bu fetch'te public tutar yok; deneme hesabi / kurulum beklemeden baslama CTA | [carzi.com.tr](https://carzi.com.tr/ozellikler/google-yorum-yonetimi) |
| **Piyzi Google Yorum Kazandirma** | Yazilim (yorum talebi) | Bu fetch'te public tutar yok | [piyzi.com/ozellikler/google-yorum-kazandirma](https://piyzi.com/ozellikler/google-yorum-kazandirma) |
| **Jetyorum otomobil servisleri / bayileri** | Yazilim (itibar / widget) | Bu fetch'te public tutar yok | [jetyorum.com](https://www.jetyorum.com/otomobil-servisleri-bayileri) |
| **Nefalix** (karsilastirma) | Yazilim (B2B SaaS) | Baslangic / Pro / Kurumsal paketler; fiyat sayfasi sektor ve modullere gore hesaplayici sunar | [nefalix.com/fiyatlar](https://nefalix.com/fiyatlar) |

**Gozlem:** Oto servis SERP'inde iki fiyat deseni var: dusuk girisli servis programlari (Canbus gibi) ve kesif / demo ile fiyatlanan CRM-itibar katmanlari (Rapitek, Carzi, Jetyorum gibi). Nefalix oto icin pozisyon alirken "stok/muhasebe programinin yerine gecmez; yorum + inbox + NPS + kriz/recall katmani" ayrimini acik yazmali.

---

## 5) nefalix.com'da oto yuzeyi

| Yuzey | Durum |
|-------|-------|
| `/sektorler` | Auto servisler yol haritasinda; metin, temel motorun ayni oldugunu ve tetikleyici anlarin degistigini soyluyor |
| `/fiyatlar` | Genel paket hesaplayici; otoya ozel fiyat / kurulum akisi ayri gorunmedi |
| `/blog` | Bu oturumda oto exact-match blog dogrulanmadi |
| `/geo` | Repo icinde mevcut `geo/*.md` yalnizca saglik pillar seti; oto GEO yok |
| `/kaynaklar` | Agirlik saglik turizmi / klinik kaynaklari |

**Eksik (Faz 4 oto icin backlog):**

- `oto servis Google yorum yonetimi yazilimi` exact-match GEO
- `oto servis CRM mi itibar SaaS mi?` ayrim sayfasi
- `arac teslim sonrasi NPS / memnuniyet anketi` GEO
- `periyodik bakim hatirlatma + WhatsApp + yorum daveti` GEO
- Carzi / Piyzi / Jetyorum karsisinda adil, kaynakli kategori karsilastirmasi

---

## 6) Nefalix konumlandirma cikarimi (oto)

- Oto servis SERP'i **servis operasyon yazilimi** tarafinda dolu: is emri, stok, e-fatura, arac gecmisi ve randevu temel kategori beklentisi.
- Google yorum / itibar tarafinda daha dar ama gercek rakipler var: Carzi oto icine Google yorum modulu koyuyor; Jetyorum ve Piyzi yorum talebi / widget / segmentleme ile geliyor.
- Bosluk: "stok programi" degil, **servis sonrasi sinyal katmani**. Nefalix; Google yorum, WhatsApp mesaj, NPS/anket, dusuk puan krizi ve periyodik bakim/recall gorevlerini tek operasyon kuyruğunda anlatmali.
- Uyum riski: Oto sektorunde review-gating dili rakiplerde yaygin gorunuyor. Nefalix icerikleri "sadece memnun musteriye yorum daveti" veya "kotuyu Google'a dusmeden engelle" gibi ifadeleri kullanmamali.
- Widget riski: Jetyorum tipi yorum widget'i anlatilacaksa, Google yorumlarinin kaynak dogrulamasi, guncelligi ve Reklam Kurulu kararina iliskin uyari olmadan fayda iddiasi kurulmamali.
- KVKK rolu: Oto servis / bayi veri sorumlusudur; Nefalix veya benzer yazilim saglayici veri isleyen / alt isleyen konumunu sozlesme ve isleme amaciyla sinirlamalidir. Arac plakasi, telefon, servis gecmisi ve mesaj icerikleri kisisel veri olarak ele alinmalidir.

---

## 7) Director denetimi (bu arastirma parcasi)

**Onay.** Gerekce: Bu dosya taslak GEO yayin metni degil arastirma notudur; yine de director kapisi uygulanmistir.

- Tekrar icerik: **Onay** — saglik/otel arastirmasiyla ayni format korunur, otoya ozgu SERP ve rakipler kullanilir.
- Cevap gec geliyor mu: **Onay** — dosya ilk bolumde yontem ve ticari sorgu haritasini verir.
- Rakip iddialari kaynakli mi: **Onay** — fiyat/ozellik iddialari URL ile yazildi; dogrulanmayan fiyatlar "public tutar yok" olarak isaretlendi.
- Review-gating imasi: **Onay** — rakiplerdeki riskli dil tavsiye olarak degil, uyum riski olarak isaretlendi.
- Google yorum widget uyarisi: **Onay** — Jetyorum widget satiri Reklam Kurulu / dogrulama uyarisi ile baglandi.
- KVKK ayrimi: **Onay** — veri sorumlusu oto servis / bayi, veri isleyen yazilim saglayici ayrimi acik yazildi.
- Kaynaksiz istatistik: **Onay** — rakiplerin kendi pazarlama istatistikleri (ornegin memnuniyet yuzdeleri) Nefalix iddiasi gibi kullanilmadi; fiyat ve ozellikler kaynakla sinirlandi.

---

## 8) Kaynak logu

- `oto servis musteri deneyimi yazilimi Turkiye oto servis CRM Google yorum`
- `oto servis CRM yazilimi randevu hatirlatma memnuniyet anketi`
- `oto servis Google yorum yonetimi yazilimi WhatsApp otomasyon`
- `oto servis programi fiyat Canbus Mysoft caneke degeryazilim ESN Sistem`
- `yetkili servis musteri memnuniyet anketi otomotiv yazilimi Turkiye`
- `site:nefalix.com oto servis Nefalix Google yorum WhatsApp`
- Fetch: rapitek.com/oto-servis-crm, servisyazilim.com, carzi.com.tr/ozellikler/google-yorum-yonetimi, otevis.com, piyzi.com/sektorler/oto-servis-randevu-programi, piyzi.com/ozellikler/google-yorum-kazandirma, ozgurkod.com/cozumler/oto-servis, jetyorum.com/otomobil-servisleri-bayileri, esnsistem.com/urunler/oto-servis-programi, fieldco.com.tr/tr/blog/teknikservisprogrami/musteri-memnuniyet-anketi-teknik-servis-programi

---

*Sonraki plan parcasi: Faz 4 otel GEO seti (`otel yorum yonetimi yazilimi`, `TripAdvisor + Booking + Google tek panel`, `PMS vs itibar SaaS`, `misafir NPS + WhatsApp`).*
