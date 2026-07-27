# Onat Sk. — Ses notu transkripti

**Kaynak:** `.tmp/stella-discovery/Onat-Sk.m4a` (~172 sn)  
**Yöntem:** Whisper `small`, dil=`tr` (2026-07-27)  
**Amaç:** Stella → Nefalix Hasta CRM kesim öncelikleri (saha dili)

## Ham metin

Şimdi bu sistemin genel çalışma mantığında ana sayfada bütün verilerin böyle paneldeki gösterimleri oluyor. Bildirimler, duyurular, döviz kurları ne bileyim işte. Dataların performansı. Zaten başlıkları belli ana sayfadaki. Onun görselini yollamıştım. Sisteme geldiğinde işte yeni lead listesi dediğimizde mesela bağlantısı olan Facebook meta reklamlarındaki otomasyon bağlantılarının gelen reklamlar lead listesine düşüyor. Sonra biz girip oradan lead listesinden seçim yapıp kişi ataması yapıyoruz ve danışan dönüşmüş oluyor bu. Dinamik Arama modülünde görüştüğümüz en son hastanın notlarını yazdıktan sonra ilgili bir sekme seçip o sekmelerin hepsinin gün atamaları var. Kaç gün sonra döneceğinin. Onun da zaten farklı sistem ayarlardaki raporlar şeyinde görmüştük atamasını. Ona göre görüşme yaptıktan sonra notlarını yazıp sekmeyi seçince iki gün sonra ise dinamik aramada iki gün sonra önümüze düşmüş oluyor. Araması gereken kişiler oranın mantığı bu şekilde. Yeni danışan danışanın listesi bunlar mevcuttaki indirdiğin bazı listeler var. Detayları zaten yazıyor. Teklif verdiğimizde yeni teklif, teklifleri toplu görme. Randevu tarafındaki kişilerin rengine göre olumlu olumsuz geldi, gelmedi gibi bütün ayarlamaları yapılabiliyor. Gelir giderleri yine aynı şekilde girdiğimiz listelediğimiz, görüntülediğimiz oluyor. WhatsApp rapor kısımlarıyla alakalı bağlantılar raporlar oluyor. Burada en önemlisi bizim için danışan dinamik arama, gelir gider ve rapor bölümündeki özellikle CRM tarafındaki olan. İşte CRM tren güncel temsili segment dağılım, temsili segment değerlenmesi, referans kaynağı temsili değerlenmesi gibi raporlamalar gibi bütün raporlama sistemleri. Yani bütün sistemin çalışır bir hâlde mantığını ben sana bu şekilde bir özet anlatmış oldum. Bunu biz canlıya alabilecek ve maksimum seviyede artık tamamen profesyonel bağlantıları çalışır bir şekilde. Artı bir komut vermeden birbiriyle bağlantılı bir CRM programı hâlinde olacak şekilde sana son yüklediğim Excel’leri de listeleri hazırlarken, şablonları mimariye çizerken onları da tamamen veri olarak yükleyip kullanıp ve bütün her şeyi tamamen çalışır bir şekilde olsun. Tıklanabilir, girilebilir, veri girilebilir, not yazılabilir, kaydedilebilir bir tarzda olsun. Tek tek uğraşmayayım istiyorum tekrar bir daha. Bütün verileri girip şablonun zaten bütün sekmelerini, iç görünümlerini hepsini ben sana fotoğraflarını paylaştım. Birbir sistemi mimarisini yapıp, sonrasında sana yüklediğim Excel’leri, hastaları tamamen içerisine gömüp girip, ben bu ay sonu bu programa para vermeyeceğim ve canlıya alıp senin programından kullanmaya devam edeceğim. O şekilde hazır bir sistem hâle gelmesini istiyorum.

## Aksiyon özeti (P0 / P1)

| # | Onat’ın istediği | Nefalix karşılık | Öncelik |
|---|------------------|------------------|---------|
| 1 | FB/Meta lead → Lead listesi otomasyonu | `clinic-lead-intake` + Meta webhook | P1 (kesim sonrası) |
| 2 | Lead’den kişi ataması → danışan | `clinic-assign` → `stage=danisan` | P0 VAR |
| 3 | Dinamik: not + segment → `gun_offset` sonra liste | `clinic-note-save` + `crm_segments.gun_offset` | P0 VAR |
| 4 | Yeni danışan + liste (Excel yükle) | Import + `/hasta-crm` formlar | P0 |
| 5 | Yeni teklif + teklifler toplu | `clinic-offers` + YeniTeklif/Teklifler | P0 (otel/transfer UI bu tur) |
| 6 | Randevu renk / geldi-gelmedi | `clinic-appointments` durumları | P0 |
| 7 | Gelir–gider gir / listele | `clinic-payments` + Kasa/YeniSatış | P0 (kur/yöntem parity bu tur) |
| 8 | CRM raporları (temsilci×segment, referans) | `clinic-reports` genişlet | P1 |
| 9 | Ana sayfa paneller (bildirim, kur, performans) | Dashboard | P1 |
| 10 | WhatsApp rapor | Evolution/Chatwoot — Stella paneli kopyalanmaz | P1 |
| 11 | Tıklanabilir / kaydedilebilir tam akış; ay sonu Stella kes | Paralel koşu → `stella_migration` go | P0 hedef |

## Kesim sinyali

> “Bu ay sonu bu programa para vermeyeceğim… senin programından kullanmaya devam edeceğim.”

→ MediDent Stella lisans kesimi, paralel koşu bitince; go kriterleri: [directives/stella_migration.md](directives/stella_migration.md).
