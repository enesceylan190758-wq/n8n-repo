# Evolution API Kurulum (WhatsApp Pilot)

## Uyarı
Evolution API **resmi WhatsApp Business API değildir**. WhatsApp Web protokolü kullanır.
Pilot/test içindir; ban riski ve İYS/KVKK sorumluluğu sizde kalır.

## Ürün yüzeyi (sağlam kurulum)

CRM WhatsApp = **Chatwoot** (hazır inbox) — Evolution’a bağlı.

| Ne | URL |
|----|-----|
| Chatwoot | https://evo.nefalix.com:8443/app |
| CRM panel | https://nefalix.com/nefalix-crm#WhatsappPanel |
| SOP | `directives/chatwoot_setup.md` |
| Manager (admin) | https://evo.nefalix.com/manager/ |

- Instance: `nefalix-crm` → Chatwoot inbox **Nefalix CRM WhatsApp**
- Evolution `CHATWOOT_ENABLED=true`, internal URL `http://chatwoot-rails:3000`

## Kurulum

```bash
cd ~/n8n-repo
bash execution/setup-evolution.sh
```

## İlk bağlantı (QR)

### Nefalix CRM (önerilen)

1. https://nefalix.com/nefalix-crm → `enes` / `kader` / `abdulkadir`
2. **WhatsApp** menüsü → Evolution Manager sohbet (SSO ile)
3. Bağlı değilse QR; bağlıysa sohbet listesi + mesaj

### Dashboard (klinik)

1. [Dashboard](https://nefalixai.com/dashboard) → **Firmalar** → firma düzenle
2. **Evolution instance adı** girin (ör. `medident-pilot`)
3. **Kaydet** → **QR oluştur**
4. Telefonda **WhatsApp → Bağlı cihazlar → Cihaz bağla** ile okutun

Vercel ortam değişkenleri: `EVOLUTION_API_KEY`, `EVOLUTION_API_URL` (varsayılan `https://evo.nefalix.com`).

**Supabase Vercel'de yok** — DB VPS'te kapalı portta. Dashboard API'leri VPS n8n proxy üzerinden gider:
- `N8N_WHATSAPP_CONNECT_URL` → wf-15
- `N8N_SUPABASE_PROXY_URL` + `NEFALIX_INTERNAL_KEY` → wf-16 (firma kaydı vb.)

API: `POST /api/whatsapp/connect` — `action: start | refresh | status`, `clinicId`, opsiyonel `instanceName`.
CRM: `POST /api/blog?action=crm-whatsapp` — `manager-sso | start | status | chats | messages | send`.

## İsim / numara görünmüyorsa

Evolution bazen `Chat`/`Contact` tablolarını boş bırakır; Manager JID gösterir.
Düzeltme (VPS):

```bash
cd /opt/nefalix
set -a && . ./.env && set +a
EVOLUTION_API_URL=https://evo.nefalix.com \
EVOLUTION_INSTANCE=nefalix-crm \
EVOLUTION_INSTANCE_ID=<uuid> \
python3 execution/backfill-evolution-names.py
```

Script: grup `subject` → `Chat.name`, mesaj `pushName` + `participantAlt` → `Contact`.
Sonra CRM’de WhatsApp → Yenile giriş.

### Yerel script (alternatif)

**Önerilen yol — tarayıcıda QR sayfası:**

```bash
bash execution/reset-evolution-qr.sh
```

Bu script instance'ı sıfırlar, taze QR üretir ve `.tmp/evolution-qr.html` dosyasını açar.

**Telefonda doğru adımlar (kamera uygulamasıyla değil):**

1. WhatsApp uygulamasını aç
2. **Ayarlar → Bağlı cihazlar → Cihaz bağla**
3. QR'ı okut (60 sn içinde; süre dolunca script'i tekrar çalıştır)
4. VPN kapalı olsun; telefon ve Mac aynı ağda olsun

**Durum kontrol:**

```bash
curl -s http://localhost:8080/instance/connectionState/medident-pilot \
  -H "apikey: $(grep EVOLUTION_API_KEY .env | cut -d= -f2)"
```

`state: "open"` olunca hazır.

## QR bağlanmıyorsa — eşleştirme kodu (alternatif)

Telefon numaranızı `.env`'e ekleyin (başında `+` olmadan, örn. `905321234567`):

```
EVOLUTION_WHATSAPP_NUMBER=905XXXXXXXXX
```

Sonra:

```bash
bash execution/reset-evolution-pairing.sh
```

WhatsApp → Bağlı cihazlar → **Telefon numarasıyla bağlan** → gelen 8 haneli kodu girin.

## Sorun giderme

| Belirti | Çözüm |
|---------|--------|
| QR okunuyor ama bağlanmıyor | `reset-evolution-qr.sh` tekrar çalıştır; WhatsApp içinden okut |
| "Bağlanılamadı" hatası | VPN kapat; farklı Wi‑Fi dene; Evolution'ı yeniden başlat |
| Birden fazla instance | Sadece `medident-pilot` kalsın; diğerlerini manager'dan sil |
| Oturum düşüyor | Mac uyku moduna girmesin; VPS'e taşı |

Evolution yeniden başlatma:

```bash
docker compose -f docker-compose.yml -f docker-compose.evolution.yml up -d evolution-api --force-recreate
bash execution/configure-evolution-webhook.sh
bash execution/reset-evolution-qr.sh
```

## Doğrula

```bash
curl -s http://localhost:8080 \
  -H "apikey: $(grep EVOLUTION_API_KEY .env | cut -d= -f2)"
```

## n8n bağlantısı

- Stub node'lar → Evolution `Send Text` (uygulandı)
- Gelen mesaj → Evolution webhook → Inbox workflow
- n8n içinden API: `http://evolution-api:8080` (Docker network)

## Mac kapanınca

WhatsApp oturumu kopar → QR tekrar gerekir (VPS'te 7/24 çözülür).

## Alım modu (gönderim kapalı)

Pilot güvenlik kilidi — gelen mesajlar işlenir, **kimseye otomatik veya manuel WA gitmez**:

```bash
bash execution/activate-whatsapp-receive-only.sh root@VPS_IP
```

- `WHATSAPP_SEND_ENABLED=false` (gateway tüm giden mesajları reddeder / loglar)
- wf-01 NPS, wf-12/13 Estesoft import sonrası **kapalı** kalır
- wf-06 Inbox, wf-00 Gateway, Evolution webhook **açık**

Gönderimi bilinçli açmak (siz «aç» deyince):

```bash
bash execution/enable-whatsapp-send.sh root@VPS_IP
```

## Durdur

```bash
docker compose -f docker-compose.yml -f docker-compose.evolution.yml stop evolution-api
```
