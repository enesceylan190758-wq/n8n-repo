# Oto servis sektörü — yorum / müşteri deneyimi otomasyonu arama araştırması

**Tarih:** 2026-08-18  
**Kapsam:** Türkiye · özel oto servis, yetkili servis, tamirhane, lastik/kaporta/oto elektrik  
**Tema:** oto servis müşteri deneyimi + Google yorum yönetimi + WhatsApp/randevu otomasyonu  
**Yöntem:** Canlı web arama / SERP sonuçları + kaynak sayfa fetch. Keyword Planner / Ahrefs hacim API'si yok; "en yoğun" sıralama **arama hacmi iddiası değil**, bu oturumda gözlenen **ticari SERP yoğunluğu + sorgular arası tekrar** ölçüsüdür. Public kaynakta doğrulanmayan fiyat veya özellik yazılmaz.

**Plan referansı:** `docs/nefalix-seo-geo-ajan-plani.md` Faz 1'de sağlık ve otelden sonra sıradaki eksik araştırma oto servis idi. Bu dosyadan sonraki pratik faz: **Faz 4 — otel GEO seti**, ardından oto GEO seti.

---

## 1) Yoğun ticari sinyalli kelime öbekleri (Türkçe)

| # | Öbek | SERP karakteri | Örnek sorgu |
|---|------|----------------|-------------|
| 1 | `oto servis müşteri deneyimi yazılımı` | CRM/AI randevu sayfaları + servis yönetim yazılımları | `oto servis müşteri deneyimi yazılımı Türkiye oto servis CRM Google yorum` |
| 2 | `oto servis CRM programı` | WhatsApp/inbox, pipeline, müşteri/araç kartı | `oto servis CRM programı randevu memnuniyet anketi WhatsApp Türkiye` |
| 3 | `oto servis randevu programı` | Online randevu, iş emri, WhatsApp/SMS hatırlatma | `oto servis WhatsApp otomasyon randevu hatırlatma müşteri takip programı` |
| 4 | `oto servis yönetim yazılımı` / `oto servis programı` | Stok, iş emri, fatura, kasa, personel performansı | SERP içinde Mekaniq, OtoCore, Livo, Piyzi tekrarları |
| 5 | `oto servis Google yorum yönetimi` | Yerel SEO ajansı ve genel Google yorum rehberleri | `oto servis Google yorum yönetimi itibar yönetimi Türkiye` |
| 6 | `yakınımdaki tamirci Google Haritalar SEO` | Oto servis özelinde ajans blog içeriği | Kobimedya sonucu |
| 7 | `periyodik bakım hatırlatma WhatsApp oto servis` | CRM + servis yönetim yazılımları | Rocketly / Piyzi / Livo / OtoCore sayfaları |
| 8 | `yetkili servis müşteri memnuniyet anketi` | Akademik kaynaklar + teknik servis anket yazılımı | `yetkili servis müşteri memnuniyet anketi otomotiv satış sonrası Türkiye` |
| 9 | `oto servis WhatsApp otomasyon` | WhatsApp Business API, mesaj şablonu, durum bildirimi | Rocketly / ÖzgürKod / Livo |
| 10 | `oto servis AI yorum yanıt` | Doğrudan oto servis dikeyinde zayıf; genel AI yorum/yerel SEO sayfaları | Google yorum + AI sorgu varyasyonları |

**Nefalix görünürlüğü:** Canlı `nefalix.com/sektorler` sayfası auto servisleri yol haritası olarak anlatıyor; öncelik sağlık kurumları. Bu oturumdaki oto servis ticari sorgularında Nefalix doğrudan üst sonuç olarak görünmedi.

---

## 2) Kim sıralanıyor? Rakipleri modele göre ayırma

### 2.1 Servis yönetim yazılımı / ERP-program

| Marka / site | Model | SERP'te neden görünür |
|--------------|-------|-----------------------|
| **OtoCore** — `otocore.tr` | Oto servis yönetim yazılımı | Randevu, iş emri, stok, kasa ve WhatsApp'ı tek panelde anlatıyor; WebSearch kesitinde public fiyat: aylık **1.500 TL**, yıllık **15.000 TL**, 2 yıllık **20.000 TL**; KDV hariç ve kampanyalar dönemsel notu var. |
| **Mekaniq** — `mekaniq.com.tr` | Oto servis/tamirhane yönetim yazılımı | İş emri, müşteri/araç kartı, stok, fatura, kasa, randevu ve WhatsApp bildirim modüllerini aynı sayfada topluyor. Public fiyat: ücretsiz paket; **799 / 1.499 / 2.099 / 3.499 TL/ay** planları; WhatsApp eklentisi **99 TL/ay**, Kurumsal'da dahil. |
| **Piyzi** — `piyzi.com/sektorler/oto-servis-randevu-programi` | Oto servis randevu ve bakım takip yazılımı | Online randevu, araç bakım geçmişi, iş emri/adisyon, periyodik bakım otomasyonu, teknisyen performansı ve WhatsApp hatırlatma anlatımı. 14 gün ücretsiz deneme; bu oturumda public aylık TL fiyat doğrulanmadı. |
| **Livo Yazılım** — `livoyazilim.com/oto-servis-randevu-takip-programi` | Oto servis randevu takip / teknik servis yönetimi | Online randevu, araç kabul, iş emri, WhatsApp/SMS bildirim, usta iş dağıtımı ve raporlama. Demo/tanıtım seansı var; public fiyat doğrulanmadı. |
| **OnarMatik / Tera Sistem** — `terasistem.com` | Oto servis/tamir takip programı | SMS, WhatsApp, müşteri/araç, veresiye ve randevu takip vurgusu. SERP'te geleneksel servis programı diliyle görünüyor. |

### 2.2 CRM / WhatsApp / AI müşteri iletişimi katmanı

| Marka / site | Model | SERP'te neden görünür |
|--------------|-------|-----------------------|
| **Rocketly** — `gorocketly.com/sektorler/oto-servis` | CRM + AI agent + WhatsApp/inbox | Oto servis sorularını AI ile yanıtlama, WhatsApp/Instagram/web formunu tek inbox'ta toplama, servis pipeline, periyodik bakım hatırlatma ve online randevu anlatımı. Kendi SSS'inde "servis/garaj yönetim yazılımı değil; müşteri iletişimi ve CRM katmanı" diye konumlanıyor. Free plan: 100 müşteri ve 1 kullanıcı. |
| **ÖzgürKod** — `ozgurkod.com/cozumler/oto-servis` | CRM + WhatsApp'lı satış/servis otomasyonu | "Aracım ne durumda?" trafiği, fotoğraflı parça onayı, kabulden teslime pipeline, WhatsApp/Instagram/web mesajlarını tek panelde toplama. 7 gün ücretsiz deneme; kredi kartı gerekmez. |
| **OvoCRM** — `ovocrm.com/sektorler/oto-servis` | Genel CRM + ön muhasebe/ERP + saha servis | Oto servis dikeyinde değil ama CRM/ERP/saha servis paketi olarak SERP'te görünüyor; KVKK ve Türkiye veri merkezi iddiası sayfa kesitinde yer alıyor. |

### 2.3 Google yorum / yerel SEO ajansları

| Marka / site | Model | SERP'te neden görünür |
|--------------|-------|-----------------------|
| **Kobimedya** — `kobimedya.com/blog/oto-servis-google-haritalar-seo` | Ajans / yerel SEO | Oto servis için "yakınımdaki tamirci" Google Haritalar SEO rehberi; yorum sayısı, yanıt hızı, kategori/hizmet etiketi ve randevu butonlarını anlatıyor. |
| **ADWEBX** — `adwebx.com.tr/tr/blog/google-yorum-sayisini-artirma` | Ajans / AI Google yorum yönetimi | Etik yorum toplama akışlarını ve Google politikasını anlatıyor; review-gating, teşvikli yorum, sahte yorum ve toplu/kiosk yorum risklerini açıkça yazıyor. |
| **B10 Digital / SEOYerel / SEOART** | Ajans / yerel SEO rehberi | Genel Google Business Profile yorum yönetimi, yorum yanıtı, doğal yorum akışı ve profil doğrulama rehberleri. Oto servis özelinde değil ama yorum-intent sorgularında görünür. |

### 2.4 Teknik servis CX / anket yazılımı ve akademik kanıt

| Kaynak | Model | Neden önemli |
|--------|-------|--------------|
| **FieldCo** — teknik servis müşteri memnuniyet anketi | Teknik servis yazılımı / anket modülü | İş emri kapandıktan 2 saat sonra SMS/e-posta ile anket; 5 puanlı emoji skalası; düşük puan için yönetici bildirimi. Oto servis dışı teknik servis olsa da "servis sonrası memnuniyet ölçümü" kalıbını doğrular. |
| **DergiPark / JEPS 2025** — "Otomotiv Servis Memnuniyetinde Algılanan Kalite ve Değerin Etkisi" | Akademik araştırma | Türkiye'de yetkili otomobil servisi bağlamında müşteri memnuniyetinde algılanan kalitenin merkezi rol oynadığını yazıyor. Bu, oto servis GEO içeriklerinde kaynaklı akademik dayanak olarak kullanılabilir; sayısal sonuç detayı bu araştırmada ayrıca çekilmediği için rakam uydurulmaz. |
| **Özgüner & Kurtuldu 2015 DOI** | Akademik araştırma | Yetkili servislerde satış sonrası hizmetler ile müşteri memnuniyeti ilişkisini inceliyor; WebSearch kesitinde satış sonrası hizmet alt boyutları ile memnuniyet arasında anlamlı ilişkiler saptandığı belirtiliyor. |

---

## 3) Alt sorular (PAA benzeri + sayfa SSS/H2 tekrarları)

People Also Ask kutusu bu araçta ayrı parse edilmedi. Aşağıdaki sorular SERP'te sıralanan sayfaların H2/SSS ve ürün anlatımlarında tekrar eden niyetlerden derlendi:

1. Oto servis CRM'i, klasik oto servis yönetim programından farklı mı? (Rocketly kendi sayfasında CRM katmanı ile garaj/ERP yönetimini ayırıyor.)
2. Randevu onayı, servis durumu ve araç hazır bildirimi WhatsApp/SMS ile otomatik gönderilebilir mi? (OtoCore, Mekaniq, Livo, Piyzi.)
3. Periyodik bakım hatırlatması km veya tarih eşiğine göre kurulabilir mi? (Rocketly, Piyzi, OtoCore.)
4. Google yorum isteme akışı servis tesliminden sonra nasıl etik kurulmalı? (ADWEBX: teşvik/review-gating yok; Piyzi sayfasındaki "memnun müşteriye Google yorum talebi" dili uyum açısından dikkat ister.)
5. "Yakınımdaki tamirci" aramasında Google Haritalar görünürlüğünü ne etkiler? (Kobimedya: kategori/hizmet etiketi, yorum sayısı, yanıt hızı, NAP tutarlılığı.)
6. Oto servis müşteri memnuniyeti nasıl ölçülür? (FieldCo: iş emri kapanışı sonrası SMS/e-posta anket; DergiPark: algılanan kalite/değer ve memnuniyet.)
7. WhatsApp kişisel hatla mı, resmi WhatsApp Business API ile mi yürütülmeli? (Rocketly/ÖzgürKod/Piyzi resmi veya kurumsal WhatsApp katmanlarını anlatıyor.)
8. Çok şubeli veya filo müşterili servislerde raporlama nasıl yapılır? (Rocketly filo segmenti; Livo/Mekaniq raporlama ve usta performansı.)

---

## 4) Fiyat / özellik şeffaflığı (public kaynakta doğrulanan)

| Rakip | Tip | Public fiyat | Kaynak |
|-------|-----|--------------|--------|
| **Mekaniq** | Servis yönetim yazılımı | Ücretsiz paket; Başlangıç **799 TL/ay**, Profesyonel **1.499 TL/ay**, Premium **2.099 TL/ay**, Kurumsal **3.499 TL/ay**; WhatsApp eklentisi **99 TL/ay**; E-Fatura **299 TL/ay** | [mekaniq.com.tr](https://mekaniq.com.tr/) |
| **OtoCore** | Servis yönetim yazılımı | WebSearch kesitinde: aylık **1.500 TL**, yıllık **15.000 TL**, 2 yıllık **20.000 TL**, KDV hariç; 30 gün ücretsiz deneme | [otocore.tr](https://otocore.tr/) |
| **Rocketly** | CRM / AI agent | Free plan: 100 müşteri + 1 kullanıcı; ücretli plan TL rakamı bu oturumda doğrulanmadı | [gorocketly.com/sektorler/oto-servis](https://gorocketly.com/sektorler/oto-servis) |
| **ÖzgürKod** | CRM / WhatsApp otomasyon | 7 gün ücretsiz deneme; public aylık TL fiyat bu sayfada doğrulanmadı | [ozgurkod.com/cozumler/oto-servis](https://ozgurkod.com/cozumler/oto-servis) |
| **Piyzi** | Randevu / bakım takip | 14 gün ücretsiz deneme; public aylık TL fiyat bu oturumda doğrulanmadı | [piyzi.com/sektorler/oto-servis-randevu-programi](https://piyzi.com/sektorler/oto-servis-randevu-programi) |
| **Livo Yazılım** | Randevu / teknik servis yönetimi | Demo / ücretsiz tanıtım seansı; public aylık TL fiyat doğrulanmadı | [livoyazilim.com/oto-servis-randevu-takip-programi](https://www.livoyazilim.com/oto-servis-randevu-takip-programi/) |
| **Kobimedya / ADWEBX / SEOYerel** | Ajans / yerel SEO | Rehber ve analiz CTA; oto servis özelinde public paket fiyat bu oturumda doğrulanmadı | Kaynak logu |
| **Nefalix** | B2B SaaS / itibar + NPS + mesaj yönetimi | Başlangıç **9.500 TL/ay** + **25.000 TL** kurulum; Profesyonel **14.900 TL/ay** + **50.000 TL** kurulum; Kurumsal **45.000 TL+/ay**; Sentinel **+3.500 TL/ay**, Recall **+2.500 TL/ay** | [nefalix.com/fiyatlar](https://nefalix.com/fiyatlar) |

**Gözlem:** Oto servis programları fiyatı sağlık/otel rakiplerine göre daha açık yazıyor ve düşük giriş fiyatlarıyla rekabet ediyor. Nefalix'in fiyatı bu segmentte daha yukarıda kalır; bu yüzden oto GEO içeriği "ERP yerine geçer" iddiası kurmamalı, Nefalix'i **yorum + NPS + WhatsApp/inbox + kriz erken uyarı katmanı** olarak konumlamalıdır.

---

## 5) nefalix.com'da oto servis yüzeyi

| Yüzey | Durum |
|-------|-------|
| `/sektorler` | Auto servisler yol haritasında; sayfa açıkça "şu anki satış önceliğimiz Sağlık Kurumları'dır" diyor. |
| `/fiyatlar` | Sektör seçici içinde Auto Servis var; fiyat hesaplayıcı aynı paketleri gösteriyor. |
| `/geo` | Bu checkout'taki `geo/*.md` dosyaları sağlık odaklı; oto servis GEO pillar yok. |
| `/blog` | Bu oturumda oto servis özel blog indeksi ayrıca fetch edilmedi; gap notundaki ana eksik sektör bazlı oto GEO/karşılaştırma yüzeyi. |
| `/kaynaklar` | Ağırlık sağlık turizmi; oto servis kaynak hub'ı yok. |

### Eksik / zayıf (oto Faz 4 backlog)

- `oto servis müşteri deneyimi yazılımı nedir?` answer-first GEO.
- `oto servis Google yorum yönetimi nasıl yapılır?` GEO; review-gating ve teşvik yasağı net olmalı.
- `oto servis CRM ile oto servis yönetim programı farkı nedir?` GEO; Rocketly'nin yaptığı CRM/garaj ayrımı SERP'te çalışıyor.
- `periyodik bakım hatırlatma WhatsApp oto servis` GEO; recall ürün dili sağlık kopyası gibi değil, km/tarih ve araç bakım bağlamıyla yazılmalı.
- `oto servis müşteri memnuniyet anketi nasıl ölçülür?` GEO; FieldCo ve DergiPark kaynaklı.
- Karşılaştırma sayfası: `Nefalix vs oto servis programı` veya `yorum/NPS katmanı vs iş emri-stok yazılımı`; fiyat karşılaştırması adil yapılmalı, "yerine geçer" denmemeli.

---

## 6) Nefalix konumlandırma çıkarımı (oto servis)

- Oto servis SERP'i **iş emri/stok/randevu yazılımları** tarafından doldurulmuş; bu oyuncular garaj operasyonunun çekirdeğine talip.
- CRM/WhatsApp katmanında Rocketly ve ÖzgürKod gibi oyuncular, "aracım ne durumda?" mesaj trafiğini ve periyodik bakım hatırlatmasını güçlü anlatıyor.
- Google yorum/itibar tarafında doğrudan oto servis SaaS rakibi zayıf; daha çok yerel SEO ajansları ve genel yorum yönetimi rehberleri var.
- Nefalix'in güvenli alanı: servis programı olmaya çalışmak değil; **servis tamamlandıktan sonra geri bildirim, yorum yanıtı, düşük puan alarmı, WhatsApp inbox ve tekrar bakım hatırlatma** katmanını anlatmak.
- Uyum: Oto servisler için veri sorumlusu servis işletmesi, Nefalix veri işleyen konumunda anlatılmalı. Müşteri yorum davetinde indirim/hediye veya "yalnız memnun müşteriye" seçici davet dili kullanılmamalı.
- Widget: Google yorumlarını müşteri sitesinde yeniden yayınlama anlatılırsa, kaynak doğrulama ve güncel puan/tarih uyarısı eklenmeden yayınlanmamalı.

---

## 7) Director denetimi

**Araştırma parçası:** **Onay.** Gerekçe: Gerçek web/SERP ve kaynak URL'leri kullanıldı; hacim API'si olmadığı açık yazıldı; rakipler servis yönetim yazılımı / CRM-WhatsApp / ajans / teknik servis CX olarak ayrıldı; public olmayan fiyatlar "doğrulanmadı" diye işaretlendi.

**Oto GEO brief'i:** **Onay, koşullu.** Üretilecek oto GEO setinde ilk cevap 1-2 cümlede verilmeli; Nefalix, oto servis ERP/garaj programının yerine geçiyormuş gibi yazılmamalı; Google yorum daveti seçici veya teşvikli gösterilmemeli; veri sorumlusu servis işletmesi, veri işleyen Nefalix ayrımı açık kalmalı.

**Piyzi kaynak dilinden türeyebilecek "memnun müşteriye yorum talebi" kalıbı:** **Red / düzelt.** Bu ifade doğrudan kopyalanırsa review-gating izlenimi doğurur; oto içerikte "servis tamamlanan müşteriye gönüllü ve tarafsız yorum daveti" dili kullanılmalı.

**Widget anlatımı:** **Red / düzelt.** Bu araştırma widget feature'ı önermiyor; ileride yazılırsa Google yorumlarının sitede yeniden yayınlanmasında kaynak doğrulama, güncel tarih ve yanıltıcı vitrin riski uyarısı zorunlu.

---

## 8) Kaynak logu

### Sorgular

- `oto servis müşteri deneyimi yazılımı Türkiye oto servis CRM Google yorum`
- `oto servis CRM programı randevu memnuniyet anketi WhatsApp Türkiye`
- `oto servis Google yorum yönetimi itibar yönetimi Türkiye`
- `yetkili servis müşteri memnuniyet anketi otomotiv satış sonrası Türkiye`
- `oto servis WhatsApp otomasyon randevu hatırlatma müşteri takip programı`

### Fetch / kaynak URL'leri

- [Rocketly — Oto Servis CRM](https://gorocketly.com/sektorler/oto-servis)
- [ÖzgürKod — Oto Servis CRM](https://ozgurkod.com/cozumler/oto-servis)
- [Mekaniq — Oto Servis Yönetim Yazılımı](https://mekaniq.com.tr/)
- [OtoCore — Oto Servis Yönetim Yazılımı](https://otocore.tr/)
- [Piyzi — Oto Servis Randevu Programı](https://piyzi.com/sektorler/oto-servis-randevu-programi)
- [Livo Yazılım — Oto Servis Randevu Takip Programı](https://www.livoyazilim.com/oto-servis-randevu-takip-programi/)
- [Kobimedya — Oto Servis Google Haritalar SEO](https://kobimedya.com/blog/oto-servis-google-haritalar-seo)
- [ADWEBX — Google yorum sayısını artırma etik yöntemler](https://adwebx.com.tr/tr/blog/google-yorum-sayisini-artirma)
- [FieldCo — Teknik servis müşteri memnuniyet anketi](https://www.fieldco.com.tr/tr/blog/teknikservisprogrami/musteri-memnuniyet-anketi-teknik-servis-programi)
- [DergiPark / JEPS — Otomotiv Servis Memnuniyetinde Algılanan Kalite ve Değerin Etkisi](https://dergipark.org.tr/en/pub/jeps/article/1590845)
- [Nefalix sektörler](https://nefalix.com/sektorler)
- [Nefalix fiyatlar](https://nefalix.com/fiyatlar)

---

*Dosya yolu: `research/oto-sektoru-arastirma.md`*
