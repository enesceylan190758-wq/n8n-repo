# Nefalix AI — MVP Yol Haritası Raporu

> Hazırlanma: Haziran 2026 | Kaynak: Cursor AI sohbet geçmişi + codebase analizi

---

## BÖLÜM 1: BUGÜNE KADAR NELER YAPTIK VE NELERİ TECRÜBE ETTİK?

### Neler Yapıldı ve Başarıldı?

Nefalix'i sıfırdan çalışan bir SaaS prototipi haline getirdik. Üretimde yayında olan parçalar şunlar:

**Otomasyon Altyapısı (n8n, 19 adet iş akışı):**
- Hasta NPS akışı uçtan uca çalışıyor: Estesoft kliniği bağlandı, hasta randevu bitişinde otomatik WhatsApp mesajı gidiyor, puan 8-10 ise Google yorum linki iletiliyor, 7 ve altı ise şikayet formu açılıp yöneticiye WhatsApp alarmı gönderiliyor.
- Google yorum senkronu: Google Places API'den yorumlar çekiliyor, Gemini AI ile yanıt taslağı oluşturuluyor, klinik yöneticisi onaylayıp yayınlıyor.
- İtibar izleme (Sentinel): Şikayetvar ve web'den klinik hakkında yazılanlar taranıyor, kritik olanlar anında WhatsApp'a iletiyor.
- Çalışan Memnuniyeti (eNPS) ve Kayıp Hasta Geri Çağırma modülleri çalışıyor.
- Gelen mesaj kutusuna WhatsApp mesajları düşüyor, ekip içi yönlendirme aktif.

**Veri Katmanı (Supabase):**
- 13 tablo, 20 migration — hastalar, randevular, yorumlar, NPS cevapları, şikayet izleme, faturalama hepsi tek veritabanında.
- Pilot klinik (MediDent Kartal) canlı veriyle test edildi.

**Web Sitesi ve Dashboard:**
- `nefalixai.com` canlıda, tam mobil uyumlu, video bölümü, fiyatlandırma ve demo akışı var.
- Yönetici dashboard'u (KPI'lar, gelen kutusu, NPS kriz takibi, faturalama) Vercel'de yayında.
- PayTR ödeme entegrasyonu kod olarak hazır, canlı test bekleniyor.

---

### Neleri Öğrendik ve Tecrübe Ettik?

**n8n ile prototip geliştirme:**
- n8n'in drag-and-drop yapısı mantığı hızla kurmamızı sağladı ama her iş akışı birbirinden bağımsız. Biri ayağa kalkmadan diğeri test edilemiyor. Yerel ortamda çalıştırdığımız smoke testlerde 7 iş akışının tamamı başarısız döndü — sebebi n8n'in Supabase credential bağlantısını her ortamda ayrı yapılandırması gerekliliği. Yani "kuruldu" ile "güvenilir çalışıyor" arasında ciddi bir fark var.
- Docker networking (n8n konteynerinden Supabase'e `host.docker.internal` ile bağlanmak zorunlu, `localhost` çalışmıyor) birkaç oturumu bitirdi; şimdi direktif olarak yazılı.
- VPS'te bazı güvenlik duvarı kuralları sunucu yeniden başlatıldığında sıfırlanıyor — üretim için ciddi bir risk.

**Yapay Zeka ile Kodlama (Cursor) Deneyimi:**
- Yeni bir iş akışı fikrinden çalışan koda 15-30 dakikada ulaşabildik. Bu inanılmaz bir hız.
- Ancak Cursor her oturumda bağlamı sıfırdan yükliyor. Bu yüzden handoff dosyaları, direktifler ve migration geçmişi tutmak zorunda kaldık — küçük bir "kurumsal hafıza" sistemi kurduk.
- Üretimde ne olduğunu doğrulayan smoke testler, Cursor'ın çıktısına güvenmek yerine bizim koyduğumuz en önemli kalite güvencesi oldu.

---

### Yapay Zeka Kodlamasının Sınırı — "Artık Yazılımcı Şart" Dediğimiz Kırılma Noktaları

| Konu | Şu Anki Durum | Neden Yazılımcı Şart? |
|------|---------------|----------------------|
| **Güvenlik (KVKK)** | Hasta verileri veritabanında anonim erişime açık — anon key ile SELECT çalışıyor | Cursor bu mimariyi kurdu ama production'da kapatmak için sistematik RLS revizyonu ve hukuki sorumluluk testi gerekiyor |
| **Gerçek Kullanıcı Auth** | Cookie tabanlı oturum — tek klinik için yeterli, çok kiracılı için tehlikeli | JWT, oturum süresi, şifre sıfırlama, e-posta doğrulama — bunlar güvenlik protokolü; "çalışıyor gibi görünüyor" yetmez |
| **Ödeme Entegrasyonu** | PayTR kodu hazır ama canlı teste girilmedi | Para geçen akışlarda Cursor'ın yazdığı her satır hem BDDK uyumu hem idempotency (ödeme iki kez kesilmesin) açısından insan gözüyle test edilmeli |
| **WhatsApp Üretimi** | Evolution API (resmi olmayan) ile pilot yürütüyoruz | Üretim için Meta'nın resmi WABA API'si gerekiyor — Evolution ile ciddi kullanımda hesap yasaklanma riski var |
| **Sistem Stabilitesi** | n8n iş akışları çöktüğünde sessizce başarısız olabiliyor | Dead-letter queue, retry mekanizması, alarm — bunlar yazılımcılık mimarisi; Cursor bunları planladı ama uygulamak ve test etmek ayrı mesele |
| **Ölçeklenme** | Tek n8n instance, tek VPS | İkinci klinik eklendiğinde veritabanı sorguları, webhook çakışmaları, rate-limit yönetimi elle kontrol edilemiyor |

---

## BÖLÜM 2: EXCEL FORMATINDA MVP YOL HARİTASI

Aşağıdaki tabloyu seçip Excel'e yapıştırabilirsiniz. Her satır yazılımcı için bağımsız bir iş kalemi.

| Aşama / Sprint | Yazılımcının Yapacağı İş | Bu İş Ne İşe Yarıyor? (Teknik Olmayan Açıklama) | Teknik Altyapı / Kullanılacak Araç | Zorluk Derecesi |
|---|---|---|---|---|
| **Sprint 1 — Güvenlik Temizliği** | Supabase RLS politikalarını düzelt: anon key ile hasta, NPS, inbox tablolarına erişimi kapat | Şu an herkes doğru URL'yi bilse hasta verilerini okuyabilir; bu KVKK ihlali | Supabase SQL, `supabase/migrations/`, Row Level Security | Orta |
| **Sprint 1 — Güvenlik Temizliği** | n8n webhook'larına kimlik doğrulama ekle (shared secret header) | Dışarıdan biri webhook URL'ini bilirse NPS tetikleyebilir ya da sistemi karıştırabilir | n8n HTTP Header Auth, `.env` secret | Kolay |
| **Sprint 1 — Güvenlik Temizliği** | VPS güvenlik duvarı kurallarını kalıcı hale getir (reboot'ta sıfırlanmasın) | Sunucu yeniden başladığında veritabanı portu internete açılıyor | `netfilter-persistent` veya `cron @reboot iptables-restore` | Kolay |
| **Sprint 1 — Güvenlik Temizliği** | Evolution API erişim bilgilerini döndür, sohbet geçmişinde görünen eski credential'ları geçersiz kıl | Eski şifre bir Cursor transcript'ine kaydolmuş; kötü niyetli biri sisteme girebilir | VPS `.env`, n8n UI Settings, Evolution API | Kolay |
| **Sprint 2 — Gerçek Auth Katmanı** | `dashboard_users` tablosu üzerine JWT tabanlı oturum sistemi kur | Şu anki cookie auth geçici; birden fazla klinik geldiğinde herkes birbirinin verisini görebilir | Supabase Auth veya custom JWT (jose/jsonwebtoken), Next.js API routes | Orta |
| **Sprint 2 — Gerçek Auth Katmanı** | Rol yönetimi: klinik yöneticisi sadece kendi kliniğinin datasını görsün | SaaS'ta her müşteri bağımsız bir "kiracı"; veriler karışmamalı | Supabase RLS `clinic_id = auth.uid()` policy | Orta |
| **Sprint 2 — Gerçek Auth Katmanı** | Şifre sıfırlama, e-posta doğrulama akışı | Müşteri kendi şifresini değiştiremezse destek talebine boğulunur | Supabase Auth email templates veya Resend/SendGrid | Kolay |
| **Sprint 3 — Ödeme Sistemi** | PayTR webhook'unu production'da test et ve idempotent hale getir | Ödeme onayı iki kez gelirse abonelik iki kez açılmamalı; banka ödemeyi onaylamadan abonelik başlamamalı | PayTR IPN, `stripe_webhook_events` tablosu (mevcut), HMAC doğrulama | Zor |
| **Sprint 3 — Ödeme Sistemi** | Abonelik plan limitleri: Free/Growth/Pro katmanlarına göre klinik başına kota uygula | Ücretsiz plan 100 NPS, ücretli plan sınırsız gibi kurallar olmadan SaaS çalışmaz | n8n workflow içinde kota kontrolü + Supabase `clinics.plan` kolonu | Orta |
| **Sprint 3 — Ödeme Sistemi** | Fatura sayfası: müşteri mevcut planını görsün, yükseltme yapabilsin | Dashboard'daki billing sekmesi şu an statik; gerçek ödeme durumu yansıtılmıyor | PayTR API + Supabase `clinics` tablosu | Orta |
| **Sprint 4 — WhatsApp Üretim Geçişi** | Evolution API (pilot) yerine Meta resmi WABA API entegrasyonu | Evolution ile 1000'den fazla mesaj atılırsa hesap yasaklanma riski var; gerçek müşteri onboarding'i için resmi API şart | Meta Business API, mevcut `nefalix-00-whatsapp-gateway.json` workflow'u revize | Zor |
| **Sprint 4 — WhatsApp Üretim Geçişi** | İYS uyumluluğu: mesaj göndermeden önce izin kontrolü | Türk mevzuatı: izinsiz ticari mesaj ceza gerektirir; `iys_consent` kolonu mevcut ama kontrol mekanizması yok | Supabase `patients.iys_consent` + n8n'de filtre node'u | Orta |
| **Sprint 5 — Dashboard Modernizasyonu** | HTML/CSS/JS dashboard'u React + Next.js'e taşı | Mevcut dashboard düz HTML; yeni özellik eklemek giderek zorlaşıyor, test edilemiyor | Next.js, Tailwind CSS, Supabase JS client — mevcut `nefalix-16-supabase-proxy.json` kaldırılabilir | Zor |
| **Sprint 5 — Dashboard Modernizasyonu** | Supabase Realtime ile canlı veri akışı | Yeni bir NPS cevabı geldiğinde sayfayı yenilemeden ekranda görünsün | Supabase Realtime subscription, React state | Orta |
| **Sprint 5 — Dashboard Modernizasyonu** | Yeni klinik onboarding sihirbazı (wizard) | Yazılımcıya ihtiyaç duymadan yeni müşteri eklenebilsin; şu an SQL migration ile ekleniyor | Multi-step form, `clinics` INSERT + `dashboard_users` INSERT, setup token akışı | Orta |
| **Sprint 6 — n8n Stabilite ve İzleme** | Başarısız workflow'lar için retry ve dead-letter mekanizması | Supabase geçici çöktüğünde NPS cevabı kaybolmasın; yeniden denenmesi için kuyruk şart | n8n Error Workflow + `automation_events` tablosu | Orta |
| **Sprint 6 — n8n Stabilite ve İzleme** | Workflow execution izleme dashboard'u | Kaç NPS gönderildi, kaçı başarısız — şu an smoke test elle çalıştırılıyor | n8n Execution logs API + Supabase `automation_events` | Kolay |
| **Sprint 6 — n8n Stabilite ve İzleme** | n8n'i worker modunda çalıştır (ölçeklenme) | Aynı anda 10 klinikten NPS geldiğinde tek instance tıkayabilir | n8n Queue Mode, Redis, VPS'de docker-compose güncellemesi | Zor |
| **Sprint 7 — Çoklu Entegrasyon** | Medicasimple ve diğer klinik yazılımları için CRM adaptör şablonu | Her yeni klinik entegrasyonu sıfırdan yazılmasın; Estesoft adaptörü şablon alınarak genişletilsin | Mevcut `nefalix-12-estesoft-adapter.json` + `nefalix-13-estesoft-poll.json` şablon olarak | Orta |
| **Sprint 7 — Çoklu Entegrasyon** | Google Yorum Yanıtlama otomasyonunu production'da aktif et | AI tarafından hazırlanan yorum yanıtları şu an onay bekliyor ama tek tık onay arayüzü yok | `nefalix-11-google-review-approve.json` + dashboard UI butonu | Kolay |
| **Sprint 8 — Raporlama ve Analitik** | Klinik bazlı haftalık e-posta raporu | Yönetici her Pazartesi "geçen hafta 23 NPS, 4 olumsuz yorum" mailini otomatik alsın | n8n Schedule Trigger + SendGrid/Resend + Supabase aggregation sorgusu | Orta |
| **Sprint 8 — Raporlama ve Analitik** | Excel/PDF export (NPS, Google yorum skoru) | Kliniklerin muhasebe veya raporlama toplantılarında veri çıktısı alabilmesi | n8n → CSV node → e-posta eki veya Vercel Edge Function | Kolay |
| **Gelecek Faz — Otel & Diğer Sektörler** | Cloudbeds PMS entegrasyonu (otel sektörü) | Checkout sonrası misafir otomatik NPS alsın — klinik yerine otel | `directives/integrations_hotels.md` SOP mevcut, kod yazılmadı | Orta |
| **Gelecek Faz — Otel & Diğer Sektörler** | Sector-agnostic çok kiracılı mimari (klinik/otel/oto) | Aynı platform farklı sektöre hizmet verebilsin — `clinics.sector` kolonu mevcut | Supabase `sector` enum + sector-aware workflow routing | Zor |
| **Gelecek Faz — GEO / AEO (Pazarlama Vizyonu)** | AI Arama Motoru Optimizasyonu (GEO/AEO) katmanı | Yapay Zeka araçları (ChatGPT, Perplexity) kliniği kaynak olarak göstersin — şimdilik web sitesinde gelecek vizyon olarak sunuluyor, kurulmayacak | Structured data, MCP Server, embedding tabanlı içerik | Zor |
| **Gelecek Faz — GEO / AEO (Pazarlama Vizyonu)** | Nefalix MCP Server (klinik verisi için AI ağ geçidi) | Yapay Zeka asistanları doğrudan klinik datasına bağlanabilsin — gelecek vizyon, MVP kapsamı dışı | Model Context Protocol, klinik API, OAuth | Zor |

---

**Öncelik Sırası Özeti:**

- **Sprint 1-2 (Güvenlik + Auth):** Yazılımcıyla ilk haftada ele alınmalı — bunlar olmadan ticari müşteriye açılamazsın.
- **Sprint 3-4 (Ödeme + WhatsApp):** İlk gelir için zorunlu iki kilit adım.
- **Sprint 5-6 (Dashboard + Stabilite):** Büyüme öncesi teknik borcu kapatır.
- **Sprint 7-8 (Entegrasyon + Raporlama):** Müşteri tutma ve yeni sektör açılımı.
- **Gelecek Fazlar:** Pazarlama dokümanlarında referans verilecek vizyon — şimdi geliştirme yok.
