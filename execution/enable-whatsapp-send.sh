#!/usr/bin/env bash
# Giden WhatsApp gönderimini aç (bilinçli onay sonrası)
# Kullanım: bash execution/enable-whatsapp-send.sh [root@vps]
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
TARGET="${1:-}"

if [[ -n "$TARGET" ]]; then
  ssh -o ConnectTimeout=20 "$TARGET" "cd /opt/nefalix && bash execution/enable-whatsapp-send.sh"
  exit 0
fi

cd "$REPO"
[[ -f .env ]] || { echo "❌ .env yok"; exit 1; }

if grep -q '^WHATSAPP_SEND_ENABLED=' .env; then
  sed -i.bak 's|^WHATSAPP_SEND_ENABLED=.*|WHATSAPP_SEND_ENABLED=true|' .env
else
  echo 'WHATSAPP_SEND_ENABLED=true' >>.env
fi
# Poll yalnızca çok yeni tamamlananları yedeklesin (geçmişe gitmesin)
if grep -q '^ESTESOFT_POLL_HOURS=' .env; then
  sed -i.bak 's|^ESTESOFT_POLL_HOURS=.*|ESTESOFT_POLL_HOURS=2|' .env
else
  echo 'ESTESOFT_POLL_HOURS=2' >>.env
fi
rm -f .env.bak

set -a
# shellcheck disable=SC1091
source .env
set +a

docker compose \
  -f docker-compose.yml \
  -f docker-compose.evolution.yml \
  -f docker-compose.prod.yml \
  up -d n8n --force-recreate

echo "✓ WHATSAPP_SEND_ENABLED=true — gateway artık mesaj gönderebilir"
echo "  ESTESOFT_POLL_HOURS=2 — poll yalnızca son 2 saatteki tamamlananları tarar"
echo "  Rate limit: MIN_INTERVAL=${WHATSAPP_MIN_INTERVAL_SEC:-45}s, MAX_HOUR=${WHATSAPP_MAX_PER_HOUR:-20}"
