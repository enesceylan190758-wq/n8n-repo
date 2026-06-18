#!/usr/bin/env bash
# Instance sıfırla + taze QR oluştur
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"
KEY=$(grep '^EVOLUTION_API_KEY=' .env | cut -d= -f2-)
INSTANCE=$(grep '^EVOLUTION_INSTANCE=' .env 2>/dev/null | cut -d= -f2- || echo medident-pilot)
INSTANCE=${INSTANCE:-medident-pilot}
API=http://localhost:8080
QR_HTML="$REPO/.tmp/evolution-qr.html"
mkdir -p "$REPO/.tmp"

echo "▶ Eski instance siliniyor: $INSTANCE"
/usr/bin/curl -s -X DELETE "$API/instance/logout/$INSTANCE" -H "apikey: $KEY" >/dev/null 2>&1 || true
/usr/bin/curl -s -X DELETE "$API/instance/delete/$INSTANCE" -H "apikey: $KEY" >/dev/null 2>&1 || true
sleep 2

echo "▶ Yeni instance oluşturuluyor..."
/usr/bin/curl -s -X POST "$API/instance/create" \
  -H "apikey: $KEY" -H "Content-Type: application/json" \
  -d "{\"instanceName\":\"$INSTANCE\",\"integration\":\"WHATSAPP-BAILEYS\",\"qrcode\":true}" >/dev/null
sleep 3

echo "▶ QR alınıyor..."
RESP=$(/usr/bin/curl -s "$API/instance/connect/$INSTANCE" -H "apikey: $KEY")
B64=$(echo "$RESP" | /usr/bin/python3 -c "import json,sys; print(json.load(sys.stdin).get('base64',''))")

if [[ -z "$B64" || "$B64" == "None" ]]; then
  echo "❌ QR alınamadı. Log: docker logs nefalix-evolution-api --tail 30"
  exit 1
fi

cat > "$QR_HTML" <<EOF
<!DOCTYPE html><html><head><meta charset="utf-8"><title>Nefalix WhatsApp QR</title>
<style>body{font-family:system-ui;text-align:center;padding:2rem;background:#0a1128;color:#fff}
img{width:320px;border:12px solid #fff;border-radius:12px}p{color:#94a3b8;max-width:420px;margin:1rem auto}</style></head>
<body><h1>WhatsApp QR — $INSTANCE</h1>
<p>Telefonda: WhatsApp → Ayarlar → Bağlı cihazlar → Cihaz bağla → QR okut</p>
<img src="$B64" alt="QR"/>
<p>QR 60 sn geçerli. Bağlanmazsa bu sayfayı yenile (F5).</p></body></html>
EOF

echo ""
echo "✓ QR hazır — tarayıcıda aç:"
echo "  file://$QR_HTML"
echo ""
open "$QR_HTML" 2>/dev/null || true

STATE=$(/usr/bin/curl -s "$API/instance/connectionState/$INSTANCE" -H "apikey: $KEY")
echo "Durum: $STATE"
