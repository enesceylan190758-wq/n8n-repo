#!/usr/bin/env bash
# Evolution → n8n Inbox webhook bağlantısı
# EVOLUTION_INSTANCE yoksa medident-pilot kullanılır (grep fail → set -u exit önlenir)
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"
source_env() { grep "^$1=" .env 2>/dev/null | cut -d= -f2- || true; }

KEY=$(grep '^EVOLUTION_API_KEY=' .env | cut -d= -f2-)
INSTANCE=$(grep '^EVOLUTION_INSTANCE=' .env 2>/dev/null | cut -d= -f2- || true)
INSTANCE=${INSTANCE:-medident-pilot}
API_URL=${EVOLUTION_API_URL:-http://localhost:8080}

# n8n container içinden erişilebilir URL
WEBHOOK_URL="http://n8n:5678/webhook/nefalix/inbox/incoming"

echo "Instance: $INSTANCE"
echo "Webhook → $WEBHOOK_URL"

/usr/bin/curl -s -X POST "$API_URL/webhook/set/$INSTANCE" \
  -H "apikey: $KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"webhook\": {
      \"enabled\": true,
      \"url\": \"$WEBHOOK_URL\",
      \"webhookByEvents\": false,
      \"webhookBase64\": false,
      \"events\": [\"MESSAGES_UPSERT\"]
    }
  }" | /usr/bin/python3 -m json.tool 2>/dev/null || true

echo ""
echo "✓ Inbox webhook ayarlandı (Evolution → n8n)"
