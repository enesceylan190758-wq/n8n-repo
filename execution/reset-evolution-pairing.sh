#!/usr/bin/env bash
# Eşleştirme kodu ile bağlan (QR alternatifi)
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"
KEY=$(grep '^EVOLUTION_API_KEY=' .env | cut -d= -f2-)
INSTANCE=$(grep '^EVOLUTION_INSTANCE=' .env 2>/dev/null | cut -d= -f2- || echo medident-pilot)
INSTANCE=${INSTANCE:-medident-pilot}
NUMBER=$(grep '^EVOLUTION_WHATSAPP_NUMBER=' .env 2>/dev/null | cut -d= -f2- || true)

if [[ -z "$NUMBER" ]]; then
  echo "❌ .env dosyasına EVOLUTION_WHATSAPP_NUMBER=905XXXXXXXXX ekleyin (+ olmadan)"
  exit 1
fi

API=http://localhost:8080

echo "▶ Instance sıfırlanıyor..."
/usr/bin/curl -s -X DELETE "$API/instance/logout/$INSTANCE" -H "apikey: $KEY" >/dev/null 2>&1 || true
/usr/bin/curl -s -X DELETE "$API/instance/delete/$INSTANCE" -H "apikey: $KEY" >/dev/null 2>&1 || true
sleep 2

echo "▶ Instance oluşturuluyor..."
/usr/bin/curl -s -X POST "$API/instance/create" \
  -H "apikey: $KEY" -H "Content-Type: application/json" \
  -d "{\"instanceName\":\"$INSTANCE\",\"integration\":\"WHATSAPP-BAILEYS\",\"qrcode\":false}" >/dev/null
sleep 2

echo "▶ Eşleştirme kodu isteniyor ($NUMBER)..."
RESP=$(/usr/bin/curl -s "$API/instance/connect/$INSTANCE?number=$NUMBER" -H "apikey: $KEY")
echo "$RESP" | /usr/bin/python3 -m json.tool 2>/dev/null || echo "$RESP"

echo ""
echo "Telefonda: WhatsApp → Bağlı cihazlar → Telefon numarasıyla bağlan"
echo "Yukarıdaki pairingCode değerini girin."
