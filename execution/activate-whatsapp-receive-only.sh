#!/usr/bin/env bash
# WhatsApp: alım + inbox AÇIK, giden mesaj KAPALI (WHATSAPP_SEND_ENABLED=false)
# Yerel/VPS:  bash execution/activate-whatsapp-receive-only.sh
# Uzak VPS:   bash execution/activate-whatsapp-receive-only.sh root@93.127.186.45
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
TARGET="${1:-}"
CLINIC_ID="51738ea8-c12e-40ce-a0e2-42869496d76b"

if [[ -n "$TARGET" ]]; then
  echo "▶ Uzak: $TARGET"
  ssh -o ConnectTimeout=20 "$TARGET" "cd /opt/nefalix && bash execution/activate-whatsapp-receive-only.sh"
  exit 0
fi

cd "$REPO"
log() { echo "▶ $*"; }

[[ -f .env ]] || { echo "❌ .env yok"; exit 1; }

set_kv() {
  local key=$1 val=$2
  if grep -q "^${key}=" .env; then
    sed -i.bak "s|^${key}=.*|${key}=${val}|" .env
  else
    echo "${key}=${val}" >>.env
  fi
}

log "Giden mesaj kilidi: WHATSAPP_SEND_ENABLED=false"
set_kv WHATSAPP_SEND_ENABLED false
rm -f .env.bak

set -a
# shellcheck disable=SC1091
source .env
set +a

export N8N_URL="${N8N_URL:-http://127.0.0.1:5678}"
: "${N8N_EMAIL:?N8N_EMAIL gerekli}"
: "${N8N_PASSWORD:?N8N_PASSWORD gerekli}"

log "Docker stack (n8n + Evolution)…"
docker compose \
  -f docker-compose.yml \
  -f docker-compose.evolution.yml \
  -f docker-compose.prod.yml \
  up -d n8n evolution-api

for i in $(seq 1 30); do
  curl -sf "${N8N_URL}/healthz" >/dev/null && break
  sleep 2
done
curl -sf "${N8N_URL}/healthz" >/dev/null || { echo "❌ n8n hazır değil"; exit 1; }

log "Workflow import (NPS/Estesoft otomatik KAPALI kalır)…"
python3 execution/import-workflows.py

log "Evolution → Inbox webhook…"
if curl -sf "${EVOLUTION_API_URL:-http://127.0.0.1:8080}" \
  -H "apikey: ${EVOLUTION_API_KEY:-}" >/dev/null 2>&1; then
  bash execution/configure-evolution-webhook.sh
  STATE=$(curl -s "${EVOLUTION_API_URL:-http://127.0.0.1:8080}/instance/connectionState/${EVOLUTION_INSTANCE:-medident-pilot}" \
    -H "apikey: ${EVOLUTION_API_KEY}" || true)
  echo "  Evolution: $STATE"
else
  echo "⚠ Evolution yanıt vermiyor — QR: Dashboard → WhatsApp Bağla"
fi

log "n8n yeniden başlat (env güncellemesi)…"
docker compose \
  -f docker-compose.yml \
  -f docker-compose.evolution.yml \
  -f docker-compose.prod.yml \
  up -d n8n --force-recreate

log "Klinik: evolution_connected işaretle…"
if [[ -n "${SUPABASE_SERVICE_ROLE_KEY:-}" ]]; then
  SB="${SUPABASE_URL:-http://127.0.0.1:54321}"
  CFG=$(curl -s "${SB}/rest/v1/clinics?id=eq.${CLINIC_ID}&select=integration_config&limit=1" \
    -H "apikey: ${SUPABASE_SERVICE_ROLE_KEY}" \
    -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}")
  MERGED=$(python3 -c "
import json,sys
rows=json.loads(sys.argv[1])
cfg=rows[0].get('integration_config') or {} if rows else {}
if isinstance(cfg,str): cfg=json.loads(cfg) if cfg else {}
cfg['evolution_connected']=True
print(json.dumps(cfg))
" "$CFG" 2>/dev/null || echo '{"evolution_connected":true}')
  curl -s -X PATCH "${SB}/rest/v1/clinics?id=eq.${CLINIC_ID}" \
    -H "apikey: ${SUPABASE_SERVICE_ROLE_KEY}" \
    -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
    -H "Content-Type: application/json" \
    -H "Prefer: return=minimal" \
    -d "{\"integration_config\":${MERGED}}" >/dev/null || true
fi

echo ""
echo "════════════════════════════════════════════════════════"
echo "✓ WhatsApp ALIM modu aktif"
echo "  • Gelen mesaj → Inbox (wf-06) + AI taslak"
echo "  • QR bağlantı: Dashboard → WhatsApp Bağla"
echo "  • GİDEN mesaj: KAPALI (WHATSAPP_SEND_ENABLED=false)"
echo "  • NPS / Estesoft otomatik: KAPALI (import koruması)"
echo ""
echo "Gönderimi açmak için (siz onayladıktan sonra):"
echo "  WHATSAPP_SEND_ENABLED=true bash execution/enable-whatsapp-send.sh"
echo "════════════════════════════════════════════════════════"
