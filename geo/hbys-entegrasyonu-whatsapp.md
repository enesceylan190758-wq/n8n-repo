---
title: HBYS entegrasyonu WhatsApp ile nasıl çalışır?
slug: hbys-entegrasyonu-whatsapp
meta_description: HBYS–WhatsApp entegrasyonu, randevu durumu gibi klinik olaylarını resmi WhatsApp Business API üzerinden onaylı şablonlarla hastaya iletir; kişisel uygulama otomasyonu yerine API, İYS/izin ve HBYS tetikleyicisi birlikte tasarlanmalıdır.
og_description: HBYS–WhatsApp entegrasyonu, randevu durumu gibi klinik olaylarını resmi WhatsApp Business API üzerinden onaylı şablonlarla hastaya iletir; kişisel uygulama otomasyonu yerine API, İYS/izin ve HBYS tetikleyicisi birlikte tasarlanmalıdır.
sector: saglik
---

# HBYS entegrasyonu WhatsApp ile nasıl çalışır?

**HBYS–WhatsApp entegrasyonu, randevu durumu gibi klinik olaylarını resmi WhatsApp Business API üzerinden onaylı şablonlarla hastaya iletir; kişisel uygulama otomasyonu yerine API, İYS/izin ve HBYS tetikleyicisi birlikte tasarlanmalıdır.**

## Key points

- Tetikleyici HBYS veya randevu sistemindedir: örneğin randevu “tamamlandı”, “iptal” veya “hatırlatma penceresi”.
- Gönderim kanalı resmi WhatsApp Business API olmalıdır; kişisel veya standart Business uygulamasından toplu otomasyon numara riski taşır.
- Ticari/iletişim izinleri İYS ve klinik aydınlatma metniyle uyumlu tutulmalıdır; şablon metinleri önceden onaylanır.
- Mesaj içeriğinde gereksiz sağlık detayı taşınmamalı; hatırlatma ve anket linki gibi operasyonel bilgiler yeterlidir.
- Gelen yanıtlar tek ekip gelen kutusunda toplanırsa “kimin yazdığı belli değil” kaosu azalır.
- Entegrasyon başarısı mesaj adediyle değil; teslim, okunma/yanıt ve no-show veya geri bildirim tamamlanma oranıyla ölçülür.

## Sık sorulanlar

### HBYS olmadan WhatsApp otomasyonu kurulabilir mi?

Evet, ajanda veya klinik CRM tetikleyebilir. HBYS varsa “gerçek” randevu kapanışı tek doğru kaynak olduğu için yanlış zamanda mesaj riski düşer. Kaynak sistem hangisiyse tetikleyici orada net tanımlanmalıdır.

### Kişisel WhatsApp ile otomatik hatırlatma neden önerilmez?

Kişisel veya gayriresmî otomasyon Meta politikalarına ve numara sürekliliğine aykırı sonuçlar doğurabilir. Resmi API şablon, kayıt ve ekip erişimini merkezi yönetir. Klinik ölçeğinde tek telefona bağlı süreç kırılgandır.

### İYS ve KVKK bu akışta nasıl ayrılır?

İYS, ticari elektronik ileti iznini düzenler; KVKK kişisel verinin işlenme hukuki sebebini ve aydınlatmayı belirler. WhatsApp hatırlatması ve anket linki her iki çerçeveye de uyumlu tasarlanmalıdır. Veri sorumlusu kliniktir; entegrasyon sağlayıcı işleme sınırını sözleşmeyle alır.

### Nefalix HBYS köprüsünde ne rol oynar?

Nefalix, HBYS tarafındaki randevu olayını geri bildirim ve mesaj akışına bağlayan katmanda çalışır. Amaç HBYS’nin yerine geçmek değil; kapanan ziyareti ölçülebilir hasta deneyimi adımlarına taşımaktır.

### Hangi mesajlar ilk etapta otomatikleştirilmeli?

Önce randevu hatırlatması ve ziyaret sonrası kısa geri bildirim daveti gibi düşük riskli, tekrarlayan mesajlar seçilir. Tedavi sonucu, teşhis veya özel nitelikli sağlık içeriği otomatik şablona konmamalıdır. Pilot bir şube veya hekim grubuyla başlamak hata alanını küçültür.

### Entegrasyon kaç haftada canlıya alınır?

Süre HBYS API erişimi, şablon onayı ve izin envanterine bağlıdır. Teknik bağlama kısa olsa da izin metinleri, şablon dili ve personel eğitimi çoğu zaman takvimi belirler. Canlıya geçmeden önce test numaralarıyla uçtan uca deneme yapılmalıdır.

## İlgili sayfalar

- [Klinik itibar yönetimi yazılımı](/geo/klinik-itibar-yonetimi-yazilimi)
- [Hasta recall / kayıp hasta geri kazanımı](/geo/hasta-recall-kayip-hasta-geri-kazanimi)
- [NPS yazılımı sağlık sektörü](/geo/nps-yazilimi-saglik-sektoru)
- [Olumsuz yorum kriz yönetimi](/geo/olumsuz-yorum-kriz-yonetimi)
- [Fiyatlar](/fiyatlar)
- [Demo](https://cal.com/enes-ceylan/15min)
