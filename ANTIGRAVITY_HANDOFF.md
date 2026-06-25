# Antigravity Handoff — Nefalix

Bu dosyayı Antigravity IDE / Antigravity 2.0 içine başlangıç bağlamı olarak ver.

## Öncelik

İlk çalışma **read-only** olsun.

Hiçbir dosya değiştirme, komutla deploy etme, migration çalıştırma, git add/commit yapma. Önce projeyi oku, mimariyi anla, riskleri çıkar ve öneri sun.

## Proje

Nefalix, klinik/hizmet işletmeleri için WhatsApp-first hasta deneyimi ve itibar yönetimi platformudur.

Canlı bileşenler:

- VPS: `93.127.186.45`, repo path: `/opt/nefalix`
- Public API: `https://api.nefalixai.com`
- Dashboard: `https://nefalixai.com/dashboard`
- Local workspace: `/Users/enesceylan/n8n-repo`
- Landing/dashboard repo: `/Users/enesceylan/nefalix-landing`
- Pilot klinik: MediDent Kartal
- Pilot `clinic_id`: `51738ea8-c12e-40ce-a0e2-42869496d76b`

## Mimari Kural

Bu repo 3 katmanlı çalışır:

1. `directives/` — SOP / ne yapılacağı
2. AI orchestration — directive oku, doğru scripti seç, hata yönet
3. `execution/` — deterministik scriptler

Yeni iş uydurmadan önce:

- `directives/` oku
- `execution/` içinde mevcut script var mı bak
- Workflow değişikliği gerekiyorsa `workflows/*.json`
- DB değişikliği gerekiyorsa `supabase/migrations`

## Aktif Akışlar

### Estesoft NPS

Randevu `Tamamlandı` olunca:

1. wf-12 Estesoft adapter NPS taslağı oluşturur.
2. Taslak dashboard `Inbox → Estesoft NPS` sekmesine düşer.
3. Yönetici onaylayınca wf-08 WhatsApp ile NPS mesajı gönderir.
4. Hasta 1-10 puan yazar.
5. wf-06 gelen WhatsApp mesajını NPS skoru olarak algılar.
6. wf-01 yanıtı işler:
   - 8-10: Google Maps linki + 5 yıldız ve yorum isteği
   - 7 ve altı: önce hastaya kısa mesaj, sonra yöneticiye WhatsApp alarmı, panelde kriz kaydı

### NPS Kriz Takibi

Dashboard NPS sekmesinde düşük puanlar için:

- Hasta adı/telefon görünür
- Not girilir
- `Tamamlandı` ile `resolution_status=resolved` olur
- Son 30 gün rapor bloğuna yansır

### Dashboard

Dashboard mobil responsive hale getirildi:

- Mobil alt menü
- `Diğer` sheet
- NPS, Recall, eNPS ve Billing sekmeleri
- Son 30 gün KPI:
  - gönderilen anket sayısı
  - ortalama NPS
  - Google Maps yorum sayısı

Recall ve eNPS şimdilik gerçek veri yoksa demo/pilot sonuçlarıyla dolacak şekilde ayarlandı.

### Auth

Mevcut dashboard login sistemi cookie tabanlıdır.

- Eski adminler `DASHBOARD_USERS` env ile çalışır.
- Yeni firma kaydında `dashboard_users` tablosunda pending kullanıcı oluşur.
- Firma e-postasına/adminde görünen linke `/dashboard/setup?token=...` şifre kurulum linki döner.

### Stripe

Stripe Checkout kodu eklendi ama production env değerleri henüz girilmedi.

Gerekli env:

- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `STRIPE_PRICE_STANDARD`
- `STRIPE_PRICE_PROFESSIONAL`

Şimdilik Stripe öncelik dışı.

## Google Cloud / AI

Nefalix ürün içi AI şu anda Vertex AI üzerinden çalışıyor.

- Project: `utility-cumulus-484107-v3`
- Billing account: `My Billing Account`
- Aktif kredi: `Trial credit for GenAI App Builder`
- Kredi bakiyesi: yaklaşık `₺45.899,90`
- Model: `gemini-2.5-flash`
- Region: `europe-west1`
- Service account: `nefalixai@utility-cumulus-484107-v3.iam.gserviceaccount.com`

Vertex smoke test çalıştı.

Ancak Antigravity'nin bu Google Cloud kredisini mi yoksa Google AI Pro / Antigravity kotasını mı kullandığı net değil.

## Antigravity'ye Sorulacak Kritik Soru

Lütfen şu soruyu cevapla:

> Bu Antigravity oturumu `enes.ceylan190758@gmail.com (Google AI Pro)` ile çalışıyor. Kullanılan model ve agent istekleri Google Cloud billing hesabındaki `Trial credit for GenAI App Builder` kredisinden mi düşer, yoksa ayrı Google AI Pro / Antigravity kotasından mı tüketilir? Bunu Antigravity CLI/IDE içinde nasıl doğrularım?

İstenen çıktı:

1. Hangi quota/kredi kullanılıyor?
2. Google Cloud billing credits ekranında düşüş beklenir mi?
3. Antigravity içinde model/usage/quota nereden görülür?
4. Google Cloud kredisiyle çalışması için gerekli ayar var mı?
5. Eğer kredi kullanılmıyorsa en uygun alternatif nedir?

## İlk Prompt

Antigravity'ye şunu ver:

```text
Bu repoyu oku ama hiçbir dosya değiştirme. Önce ANTIGRAVITY_HANDOFF.md dosyasını oku. Nefalix mimarisini, aktif workflowları, Supabase tablolarını, dashboard yapısını ve canlı sistem risklerini özetle.

Sonra özellikle şu soruyu araştır ve cevapla:
Bu Antigravity oturumu Google Cloud billing hesabındaki Trial credit for GenAI App Builder kredisini kullanıyor mu, yoksa Google AI Pro / Antigravity kotasını mı kullanıyor? Bunu nasıl doğrularız?

Hiçbir dosya değiştirme. Sadece rapor ver.
```

## Güvenli Çalışma Kuralları

- İlk turda read-only çalış.
- Dosya yazmadan önce kullanıcıdan izin iste.
- `git status` kontrol etmeden değişiklik yapma.
- `.env`, credential, service account JSON, token, secret dosyalarını okuma veya yazma.
- `git reset`, `git checkout --`, force push, destructive komut kullanma.
- Deploy, migration, production workflow import işlemlerini kullanıcı onayı olmadan yapma.

