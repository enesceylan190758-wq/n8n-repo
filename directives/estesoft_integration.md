# Estesoft (Este Soft) → Nefalix Entegrasyonu

## Hedef
Medident randevusu **tamamlandı** olunca → AI **NPS taslak** üretilir → yönetici dashboard'dan onaylayınca WhatsApp gider.

**Otomatik gönderim:** Dashboard onayından sonra wf-08 → gateway. `WHATSAPP_SEND_ENABLED=true` iken gönderilir.

**Geçmiş randevular:** `python3 execution/seed-estesoft-completed-dedup.py` — mevcut Tamamlandı kayıtlarını dedup işaretler (mesaj/taslak yok).

**Estesoft webhook (Nefalix):**
```
POST https://api.nefalixai.com/webhook/nefalix/estesoft/webhook
```

**NPS hedef (dahili / test):**
```
POST https://api.nefalixai.com/webhook/nefalix/hbys/appointment-completed
```

## Estesoft tarafında ne var?
[Estesoft Geliştirici Araçları](https://estesoft.com.tr/tr/entegrasyonlar/gelistirici-araclari) sayfasına göre:
- REST API (200+ endpoint, Swagger/OpenAPI)
- JWT + API Key kimlik doğrulama
- Olay bazlı webhook (appointment.created, appointment.cancelled, appointment.reminder vb.)
- Multi-tenant (kiracı) mimari

> **Not:** “Randevu tamamlandı” için tam event adı Swagger’da doğrulanmalı — muhtemelen `appointment.updated` + durum alanı veya özel `appointment.completed`.

## Estesoft Stella API — hangi endpoint?

Swagger'da **randevu için değil**, webhook bölümünü kullan:

| Endpoint | Ne için | Nefalix için? |
|----------|---------|----------------|
| **`POST /api/WebhooksApi/Subscribe`** | Nefalix URL'yi kaydet | **EVET — bunu** |
| **`GET /api/WebhooksApi/GetInformation`** | Hangi olaylar var, mevcut abonelikler | Önce bunu aç |
| `POST /api/WebhooksApi/Unsubscribe` | Aboneliği kaldır | Gerekirse |
| `POST /api/AppointmentApi/ChangeAppointmentStatus` | Sen Estesoft'ta statü **değiştirirsin** | Hayır (giden API) |
| `GET /api/AppointmentApi/List` | Randevu listesi (polling yedek) | İleride cron |
| `POST /api/WebsiteIntegration/NewForm` | Web formu lead | Hayır |
| `POST /api/AuthApi/GetToken` | JWT al | Subscribe öncesi |

**API base (Medident Stella):** `https://medidentistanbul.stellamedi.com`  
Swagger: `https://medidentistanbul.stellamedi.com/swagger/index.html?apiKey=...`

### Swagger'da adım adım (Try it out)

1. **`AuthApi` → `POST /api/AuthApi/GetToken`**
   - Header: `apikey` = API anahtarın
   - Body: paneldeki **Api Talimatları** örneği (username + password/apiKey)
   - Dönen `token` / `accessToken` kopyala

2. **`WebhooksApi` → `GET /api/WebhooksApi/GetInformation`**
   - Header: `apikey` + `Authorization: Bearer {token}`
   - Hangi **event** isimleri var gör (randevu tamamlandı / status changed vb.)

3. **`WebhooksApi` → `POST /api/WebhooksApi/Subscribe`**
   - Aynı header'lar
   - Body'de Nefalix URL:
   ```
   https://api.nefalixai.com/webhook/nefalix/estesoft/webhook
   ```
   - Event alanı: GetInformation'da gördüğün **randevu tamamlandı** olayı

### Otomatik kayıt (token çalışınca)

```bash
export ESTESOFT_STELLA_API_BASE=https://stellapi.estesoftbulut.com  # Swagger host'un
python3 execution/register-estesoft-webhook.py
```

GetToken panelden farklıysa Swagger'daki çalışan JSON'u `.env`'e:
`ESTESOFT_SUBSCRIBE_BODY_JSON={"url":"https://api.nefalixai.com/webhook/nefalix/estesoft/webhook",...}`

## Estesoft panelinde webhook (yapılacak — 5 dk)

Nefalix tarafı **hazır ve test edildi** (adapter → NPS workflow `success`).

### Adımlar

1. **Estesoft** klinik paneli → **Geliştirici Araçları / API** (API anahtarının olduğu ekran)
2. **Webhook** veya **Abonelik (subscribe)** bölümü
3. **Yeni webhook** → URL:

```
https://api.nefalixai.com/webhook/nefalix/estesoft/webhook
```

4. **POST**, `Content-Type: application/json`
5. **Olaylar** — mümkün olanlar:
   - `appointment.completed` (tercih)
   - `appointment.updated` (status tamamlandı olduğunda)
6. **Kaydet**

### Doğrula (Mac veya VPS)

```bash
bash execution/configure-estesoft-webhook.sh
# veya sadece test:
bash execution/test-estesoft-nps.sh 905XXXXXXXXX
```

n8n Executions’ta sırayla **success** görülmeli:
- `Nefalix - Estesoft HBYS Adapter`
- `Nefalix - Feedback & Reviews Loop`

### Estesoft anket çakışması

Estesoft’un kendi “randevu sonrası memnuniyet anketi” açıksa Nefalix NPS ile **çift mesaj** gider. Medident’te:
- Ya Estesoft anketini kapat
- Ya Nefalix’i kullan — tek kanal

### Swagger ile API kaydı (opsiyonel)

Panelde **Swagger Görüntüle** linkini kopyala → `ESTESOFT_BASE_URL` olarak `.env`’e yaz. Webhook subscribe endpoint bulunursa `execution/register-estesoft-webhook.py` eklenebilir.

## Medident’ten istenecek bilgiler (checklist)

### Zorunlu (bağlantı için)
| # | Bilgi | Neden |
|---|--------|--------|
| 1 | **Estesoft API Key** | REST çağrıları |
| 2 | **JWT alma yöntemi** (endpoint + örnek) | Token yenileme |
| 3 | **Tenant / klinik ID** (Estesoft içinde Medident) | Multi-tenant izolasyon |
| 4 | **Swagger veya API dokümantasyonu URL** | Alan adlarını eşlemek |
| 5 | **Test ortamı** var mı? (sandbox URL) | Canlı hastaya mesaj gitmesin |

### Webhook yolu (tercih edilen)
| # | Bilgi | Neden |
|---|--------|--------|
| 6 | Randevu **“tamamlandı”** statüsünde hangi **webhook event** tetikleniyor? | Doğru abonelik |
| 7 | Örnek **webhook JSON** (gerçek veya anonimleştirilmiş) | n8n mapping |
| 8 | Webhook’u Estesoft panelinden **kendiniz ekleyebiliyor musunuz?** | Yoksa Estesoft destek |
| 9 | Webhook **imza / secret** var mı? (HMAC header) | Güvenlik doğrulama |

### Hasta verisi (NPS için)
| # | Bilgi | Neden |
|---|--------|--------|
| 10 | Hasta **telefon** alanı API/webhook’ta nasıl geliyor? | WhatsApp gönderimi |
| 11 | **İYS / ticari ileti izni** alanı var mı? | KVKK + İYS filtresi |
| 12 | Randevu ID, hasta adı, doktor, tedavi/hizmet alanları | Kişiselleştirilmiş NPS |

### Opsiyonel (API polling yedek plan)
Webhook yoksa veya gecikmeli ise: n8n cron → `GET /appointments?status=completed&since=...` → Nefalix webhook’a ilet.

## Nefalix’in beklediği minimum JSON

Estesoft farklı formatta gönderirse ara **adapter** workflow yazılır; hedef alanlar:

```json
{
  "clinic_id": "51738ea8-c12e-40ce-a0e2-42869496d76b",
  "patientName": "Ayşe Yılmaz",
  "patientPhone": "+905551234567",
  "clinicName": "Medident İstanbul",
  "doctorName": "Dr. X",
  "treatment": "implant kontrol",
  "googleReviewUrl": "https://www.google.com/maps/...",
  "complaintFormUrl": "https://www.sikayetvar.com/...",
  "appointmentId": "estesoft-1842"
}
```

`googleReviewUrl` ve `complaintFormUrl` Estesoft’ta yoksa Nefalix Supabase `clinics` tablosundan otomatik doldurulur (adapter’da).

## İki entegrasyon modeli

```
[A] Estesoft Webhook ──POST──► wf-12 adapter ──► NPS WhatsApp
         (hızlı; Stella'da abonelik aktif ama status değişiminde POST gelmeyebilir)

[B] n8n wf-13 Cron (10 dk) ──GET AppointmentApi/List──► Tamamlandı ──► wf-12 adapter
         (webhook gecikmezse / POST gelmezse — Medident pilot için AKTİF)
```

### Stella API (doğrulanmış — Haz 2026)

| Endpoint | Method | Not |
|----------|--------|-----|
| `/api/AuthApi/GetToken` | POST | Body: `{username, password}` + header `apikey` |
| `/api/WebhooksApi/GetInformation` | GET | `destinationUrl`, `isActive` |
| `/api/WebhooksApi/Subscribe` | POST | Body: Nefalix webhook URL (string) |
| `/api/AppointmentApi/List` | **GET** | POST değil; `resultCount` + `data[]` |
| `/api/AppointmentApi/Get?id=` | GET | Tek randevu detayı |

**Stella List örnek alanları** (`statusName: "Tamamlandı"`):
```json
{
  "id": "6aafd87b-3c6e-f111-9045-80efda3655cc",
  "customerName": "enes ceylan",
  "phone": "+905359288250",
  "statusName": "Tamamlandı",
  "statusState": "+",
  "staffName": "Enes Ceylan",
  "serviceName": "İMPLANT NEODENT STRAUMAN"
}
```

**API çağrıları:** Browser `User-Agent` header kullan (Stella WAF).

### n8n workflow'ları

| WF | Dosya | Rol |
|----|-------|-----|
| **12** | `nefalix-12-estesoft-adapter.json` | Webhook normalize → AI NPS taslak → inbox (`estesoft_nps`) |
| **13** | `nefalix-13-estesoft-poll.json` | Her 1 dk poll + manuel `POST /webhook/nefalix/estesoft/poll` |

**Dedup:** `automation_events` — `event_type=estesoft_nps_triggered`

**Dashboard:** Inbox → sekme **Estesoft NPS** (gelen mesajlardan ayrı). Onay → wf-08 → gateway.

**NPS yanıt (hasta puan yazınca):** wf-06 skor algılar → wf-01 `nps/response` — **8+** Google link, **7−** yönetici alarm (otomatik WhatsApp).

### VPS deploy

```bash
# Mac'ten
rsync -az --exclude '.git' --exclude '.tmp' --exclude '.env' \
  /path/n8n-repo/ root@93.127.186.45:/opt/nefalix/

# Estesoft env (şifre dahil)
ESTESOFT_API_USERNAME=... ESTESOFT_API_KEY=... ESTESOFT_API_PASSWORD=... \
  bash execution/setup-estesoft-env.sh root@93.127.186.45

# n8n env yenile + import
ssh root@93.127.186.45 'cd /opt/nefalix && docker compose -f docker-compose.yml -f docker-compose.evolution.yml -f docker-compose.prod.yml up -d n8n && python3 execution/import-workflows.py'
```

### Manuel test (enes ceylan randevusu)

```bash
# Stella formatında doğrudan adapter
curl -s -X POST https://api.nefalixai.com/webhook/nefalix/estesoft/webhook \
  -H 'Content-Type: application/json' \
  -d '{"statusName":"Tamamlandı","statusState":"+","id":"6aafd87b-3c6e-f111-9045-80efda3655cc","customerName":"enes ceylan","phone":"+905359288250","staffName":"Enes Ceylan","serviceName":"İMPLANT NEODENT STRAUMAN"}'

# veya poll workflow (tüm Tamamlandı randevuları)
curl -s -X POST https://api.nefalixai.com/webhook/nefalix/estesoft/poll
```

n8n Executions: **Estesoft HBYS Adapter** + **Feedback & Reviews Loop** = success.

## Medident’e gönderilecek kısa mesaj

> Estesoft webhook panelinde şu URL’yi ekleyin: `https://api.nefalixai.com/webhook/nefalix/estesoft/webhook`  
> Olay: randevu tamamlandı (`appointment.completed` veya eşdeğeri).  
> Estesoft’un kendi sonrası anketini kapatın (Nefalix NPS kullanılacaksa).

## NPS akışı (iş kuralı)

```
Randevu Tamamlandı (Estesoft)
  → AI NPS taslağı (dashboard / Estesoft NPS sekmesi)
  → Yönetici onaylar → WhatsApp anket (1–10 puan iste)

Hasta puan yazar:
  8–10  → Google Maps linki + 5 yıldız ve yorum iste (otomatik)
  7 ve altı → Kısa teşekkür/özür mesajı hastaya (otomatik)
            → Yönetici WhatsApp alarmı
            → Panel NPS sekmesinde hasta adı + telefon (ara)
```

**wf-01** `nps/response` · **wf-06** WhatsApp puan algılama · **wf-12** taslak · **wf-08** onaylı gönderim.

Düşük puan hasta mesajı **önce**, yönetici alarmı **sonra** gider (`patch-wf-01-nps-flow.py`).

**Panel kriz notu:** NPS sekmesinde not + Tamamlandı → `nps_responses.resolution_status=resolved`; son 30 gün aylık rapor bloğu.

## Edge cases
| Durum | Çözüm |
|-------|--------|
| Telefon yok | Resepsiyondan zorunlu alan; mesaj atlanır, log |
| İYS izni yok | Mesaj gönderilmez (deterministik filtre) |
| Aynı randevu 2 kez webhook | `appointmentId` ile Supabase `automation_events` dedup (wf-12 + wf-13) |
| Webhook abonelik aktif ama POST gelmiyor | Stella bilinen sorun — **wf-13 poll** devreye alındı (10 dk) |
| İlk poll tüm geçmiş randevuları tetikler | `historical_seed` dedup + `ESTESOFT_POLL_HOURS=2` |
| Poll `too_old` (randevu saati eski) | `modified/created` öncelikli — `patch-wf-estesoft-freshness.py` |
| `historical_seed` yeni tamamlamayı engeller | Dedup yalnızca `adapter_draft` / `adapter` kaynaklarında |
| WhatsApp ban | Tüm gönderim **wf-00 gateway** — `directives/security.md` |
| `AppointmentApi/List` 405 | POST değil **GET** kullan |
| API 403 / boş yanıt | `User-Agent: Mozilla/5.0 ...` header ekle |
| Estesoft kendi memnuniyet anketi var | Çakışma — hangi kanal öncelikli netleştir |
