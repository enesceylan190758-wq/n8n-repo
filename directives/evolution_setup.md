# Evolution API Kurulum (WhatsApp Pilot)

## Uyarı
Evolution API **resmi WhatsApp Business API değildir**. WhatsApp Web protokolü kullanır.
Pilot/test içindir; ban riski ve İYS/KVKK sorumluluğu sizde kalır.

## Kurulum

```bash
cd ~/n8n-repo
bash execution/setup-evolution.sh
```

## İlk bağlantı (QR)

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

## Durdur

```bash
docker compose -f docker-compose.yml -f docker-compose.evolution.yml stop evolution-api
```
