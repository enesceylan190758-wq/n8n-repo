#!/usr/bin/env bash
# Estesoft webhook → Nefalix NPS zinciri smoke test
set -euo pipefail

HOST="${N8N_PUBLIC_HOST:-api.nefalixai.com}"
URL="https://${HOST}/webhook/nefalix/estesoft/webhook"
TEST_ID="manual-test-$(date +%s)"
PHONE="${1:-905359288250}"

echo "▶ Estesoft adapter: $URL"
echo "▶ Test appointmentId: $TEST_ID"
echo "▶ Test phone: $PHONE (WhatsApp NPS gidebilir — dikkat)"

RESP=$(curl -s -X POST "$URL" \
  -H "Content-Type: application/json" \
  -d "{\"statusName\":\"Tamamlandı\",\"statusState\":\"+\",\"id\":\"$TEST_ID\",\"customerName\":\"Estesoft Test\",\"phone\":\"$PHONE\",\"staffName\":\"Dr. Test\",\"serviceName\":\"kontrol\"}")

echo "← $RESP"

if echo "$RESP" | grep -q "Workflow was started"; then
  echo "✓ Adapter webhook kabul etti"
else
  echo "✗ Beklenmeyen yanıt"
  exit 1
fi

echo "  n8n → Executions: Estesoft HBYS Adapter = success"
echo "  Dashboard → Inbox → Estesoft NPS sekmesinde taslak görünmeli (otomatik gönderim yok)"
