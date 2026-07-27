# Nefalix CRM — Kurum / Klinik Sürümü · Kullanım & Bağlantı Kılavuzu

Bu dosya, **`Nefalix CRM.html`** (kurum/klinik B2B sürümü) tek dosyalık sistemin ne olduğunu, hangi modülün ne işe yaradığını, nasıl kullanılacağını ve gerçek sisteme nasıl bağlanacağını anlatır.

> **Fark:** Bu sürümde "hasta" yerine **kurum/klinik** (müşterilerimiz) yönetilir. Nefalix sahada kliniklerle görüşür, görüşmeleri kaydeder, teklif → sözleşme → aktif müşteri sürecini takip eder.

---

## 1. Sistem nedir, nasıl açılır?

- **Tek dosya:** Tüm sistem (sayfalar + örnek kurum verisi) tek `.html` içinde gömülü, **çevrimdışı** çalışır.
- **Açma:** Çift tıkla → tarayıcıda açılır. Kurulum/internet/sunucu gerekmez.
- **Sunucuya koymak:** Dosyayı statik hosting'e koy, link üzerinden herkes açar.
- **Giriş:**
  | Kullanıcı | Şifre | Rol |
  |-----------|-------|-----|
  | admin | 1234 | Yönetici |
  | enes | 1234 | Saha Satış Temsilcisi |
  | demo | demo | Temsilci |

---

## 2. Veri nerede saklanıyor? (ÖNEMLİ)

- Açılışta **örnek 30 kurum** + görüşme, sözleşme, tahsilat verisi yüklenir.
- Eklediğin/değiştirdiğin her şey (görüşme, yeni kurum, not, aşama…) **o tarayıcının hafızasında (localStorage)** saklanır → sadece o bilgisayarda kalır.
- Ortak/çok kullanıcılı veri için → **Bölüm 6 (gerçek veritabanı bağlantısı)**.
- "Ayarlar → sıfırla" ile örnek veriye dönülür.

---

## 3. Menü yapısı — neyin nerede olduğu

| Menü | İçindekiler | Ne işe yarar |
|------|-------------|--------------|
| **🏠 (Ana)** | Göstergeler | Kurum/pipeline özet grafikleri |
| **CRM** | Yeni Lead, Lead Listesi, Salesline, Dinamik Arama | Potansiyel kurum (lead) yönetimi |
| **KURUM** | Yeni Kurum, Kurum Listesi, Teklifler, Notlar & Görevler | Müşteri klinik/kurum kayıtları |
| **DEMO / TOPLANTI** | Yeni Toplantı, Takvim, Toplantı Listesi | Demo & toplantı planlama |
| **GELİRLER** | Kasa, Satış, Bakiye, Faturalar | Abonelik geliri / tahsilat |
| **GİDERLER** | Gider Kaydet, Firma, Giderler | Masraf takibi |
| **WHATSAPP** | Yönetim Paneli | Mesajlaşma |
| **RAPOR** | Tüm Raporlar | Kurum bazlı analiz |
| **SİSTEM** | Yetki, Ayarlar, Personel, Hizmet, Paket, Ürün | Tanımlar (CRM paketleri vb.) |
| **DESTEK** | Kayıtlarım, Yeni Destek | Teknik destek |

---

## 4. Pipeline (satış hattı) — süreç

Kurumlar şu aşamalardan geçer (Salesline sütunları da budur):

**Yeni Lead → İlk Görüşme → Demo → Teklif → Sözleşme → Aktif Müşteri**

- "Aktif Müşteri" = sözleşmesi başlamış, abonelik ödeyen klinik.
- Aşamayı değiştirmenin 2 yolu: **Kurum Kartı → Düzenle → Aşama**, ya da **Kurum Kartı → Notlar → Segment (kaydederken güncelle)**.

---

## 5. Modüller — ne yapar, nasıl kullanılır?

### Kurum Listesi (KURUM → Kurum Listesi)
- Tüm müşteri kurumlar; **arama + aşama filtresi + kurum tipi filtresi**, Excel/PDF. İsimlere tıkla → **Kurum Kartı**.

### Kurum Kartı (isimlere tıklayınca açılır) — en önemli ekran
Sol menü sekmeleri:
- **Detaylar:** Kurum bilgileri (yetkili, ünvan, telefon, web, vergi no, hekim sayısı), adres, CRM bilgileri + hızlı not.
- **Düzenle:** Tüm alanları güncelle (aşama dahil).
- **İlgili Kişiler:** Yetkili + görüşülen kişiler.
- **Görüşmeler / Ziyaretler:** 🔑 Saha görüşmesi kaydı. **Tip** (telefon/yüz yüze/online demo/saha ziyareti), **görüşülen kişi**, **konu**, **sonuç** (ilgilendi / teklif istendi / demo planlandı …), **sonraki adım tarihi**. Kaydet → görüşme geçmişine düşer.
- **Teklifler:** Kuruma verilen CRM paketleri teklifleri.
- **Sözleşme / Abonelik:** Plan (Başlangıç/Profesyonel/Kurumsal), aylık ücret, başlangıç, durum.
- **Notlar:** Not + **Segment (kaydederken güncelle)** ile aşamayı değiştir.
- **Dosyalar, Aktivite Geçmişi, Tahsilat / Ödemeler.**

### Dinamik Arama (CRM → Dinamik Arama)
- **Amaç:** Sırayla **aranacak/takip edilecek kurum** listesi ("bugün aranacaklar").
- **Nasıl:** İsme tıkla → kurum kartı; görüşme sonrası not + sonuç + "X gün sonra tekrar ara".

### Salesline (CRM → Salesline)
- Kurumların **hangi aşamada** olduğunu gösteren kanban.

### Demo / Toplantı Takvimi
- Aylık takvim; demo ve toplantıların durumları renklerle.

### Gelirler / Giderler / Raporlar
- Gelir = **abonelik tahsilatı** (kurum adına). Giderler = ofis, reklam, saha, yazılım, maaş. Raporlar kurum bazlı (aşama/temsilci/referans dağılımı, finansal özet).

---

## 6. Gerçek sisteme bağlama (Enes için — entegrasyon noktaları)

Şu an her şey **demo/örnek veri** ile çalışır. Canlı için:

| Ne | Şu an | Gerçekte nereye bağlanır |
|----|-------|--------------------------|
| **Veri (kurum, görüşme, sözleşme…)** | Tarayıcı hafızası + gömülü JSON | **Veritabanı/API** (Supabase, Firebase, kendi sunucun). Kodda **`store.js`** içindeki `getKurum / addGorusme / updateKurum / getSozlesme …` fonksiyonları API çağrısına çevrilir. |
| **Kullanıcı girişi** | `store.js`'te sabit kullanıcılar | Gerçek kullanıcı/kimlik servisi |
| **WhatsApp** | Panel demo | **Meta WhatsApp Business API** |
| **SMS** | — | Netgsm / İleti Merkezi |
| **E-posta** | — | SMTP / SendGrid |

> Özet: **Tek değişecek dosya `store.js`.** Arayüz aynı kalır; sadece veri okuma/yazma gerçek API'ye yönlenir.

---

## 7. Saha akışı (pratik kullanım — Enes)

1. Sahada klinikle konuş → **Kurum Kartı → Görüşmeler**'e görüşmeyi kaydet (sonuç + sonraki adım).
2. İlgilendiyse → aşamayı **Demo/Teklif**'e taşı (Notlar → Segment).
3. Teklif ver → **Teklifler**.
4. Anlaşınca → **Sözleşme** + aşama **Aktif Müşteri**; abonelik geliri **Gelirler**'e işlenir.
5. Aranacakları **Dinamik Arama**'dan takip et.

---
*Nefalix CRM · Kurum/Klinik Sürümü · Bu kılavuz `Nefalix CRM.html` içindir.*
