#!/usr/bin/env bash
# Medident İstanbul pilot — dashboard otomasyonlarını ayağa kaldır
# Yerel/VPS:  bash execution/activate-medident-pilot.sh
# Uzak VPS:   bash execution/activate-medident-pilot.sh root@2.27.101.119
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
TARGET="${1:-}"

run_remote() {
  ssh -o ConnectTimeout=20 "$TARGET" "cd /opt/nefalix && bash execution/activate-medident-pilot.sh"
}

if [[ -n "$TARGET" ]]; then
  echo "▶ Uzak aktivasyon: $TARGET"
  run_remote
  exit 0
fi

cd "$REPO"
log() { echo "▶ $*"; }

[[ -f .env ]] || { echo "❌ .env yok — önce cp .env.vps.example .env"; exit 1; }
set -a
# shellcheck disable=SC1091
source .env
set +a

export N8N_URL="${N8N_URL:-http://127.0.0.1:5678}"
: "${N8N_EMAIL:?N8N_EMAIL .env içinde gerekli}"
: "${N8N_PASSWORD:?N8N_PASSWORD .env içinde gerekli}"
export N8N_SUPABASE_HOST="${N8N_SUPABASE_HOST:-http://host.docker.internal:54321}"

CLINIC_ID="51738ea8-c12e-40ce-a0e2-42869496d76b"

log "Stack kontrolü…"
if ! curl -sf "${N8N_URL}/healthz" >/dev/null 2>&1; then
  log "n8n kapalı — Docker stack başlatılıyor…"
  docker compose \
    -f docker-compose.yml \
    -f docker-compose.evolution.yml \
    -f docker-compose.prod.yml \
    up -d
  for i in $(seq 1 45); do
    curl -sf "${N8N_URL}/healthz" >/dev/null && break
    sleep 2
  done
fi
curl -sf "${N8N_URL}/healthz" >/dev/null || { echo "❌ n8n ayağa kalkmadı"; exit 1; }

if ! docker ps --format '{{.Names}}' | grep -q supabase_kong; then
  log "Supabase başlatılıyor…"
  npx supabase start
fi

# Supabase anahtarlarını .env'e yaz (yoksa)
if [[ -z "${SUPABASE_SERVICE_ROLE_KEY:-}" ]]; then
  STATUS=$(npx supabase status -o env 2>/dev/null || true)
  if [[ -n "$STATUS" ]]; then
    SERVICE=$(echo "$STATUS" | rg '^SERVICE_ROLE_KEY=' | cut -d= -f2- || true)
    ANON=$(echo "$STATUS" | rg '^ANON_KEY=' | cut -d= -f2- || true)
    [[ -n "$SERVICE" ]] && export SUPABASE_SERVICE_ROLE_KEY="$SERVICE"
    [[ -n "$ANON" ]] && export SUPABASE_ANON_KEY="$ANON"
  fi
fi

log "n8n credential'ları (Supabase + OpenAI)…"
python3 execution/setup-n8n-credentials.py
# shellcheck disable=SC1091
source <(python3 -c "
import json
from pathlib import Path
d=json.loads(Path('.tmp/n8n-credential-ids.json').read_text())
print(f'export N8N_SUPABASE_CRED_ID={d[\"supabase\"]}')
if d.get('openai'): print(f'export N8N_OPENAI_CRED_ID={d[\"openai\"]}')
")

log "Workflow import + aktivasyon…"
python3 execution/import-workflows.py

log "Evolution → Inbox webhook…"
if curl -sf "${EVOLUTION_SERVER_URL:-http://127.0.0.1:8080}" \
  -H "apikey: ${EVOLUTION_API_KEY:-}" >/dev/null 2>&1; then
  bash execution/configure-evolution-webhook.sh
else
  echo "⚠ Evolution API yanıt vermiyor — WhatsApp webhook atlandı"
  echo "  Sonra: bash execution/reset-evolution-qr.sh"
fi

log "Medident profil senkronu…"
SUPABASE_URL="${SUPABASE_URL:-http://127.0.0.1:54321}" \
SUPABASE_SERVICE_ROLE_KEY="${SUPABASE_SERVICE_ROLE_KEY}" \
  python3 execution/sync-clinic-profile.py || true

if [[ -n "${GOOGLE_PLACES_API_KEY:-}" ]]; then
  log "Google yorum senkronu (Places API)…"
  SUPABASE_URL="${SUPABASE_URL:-http://127.0.0.1:54321}" \
  SUPABASE_SERVICE_ROLE_KEY="${SUPABASE_SERVICE_ROLE_KEY}" \
    python3 execution/sync-google-reviews.py || echo "⚠ Google yorum senkronu atlandı/başarısız"
else
  echo "⚠ GOOGLE_PLACES_API_KEY yok — Google yorum senkronu atlandı"
fi

log "Smoke test (dashboard modülleri)…"
export N8N_URL
export SUPABASE_SERVICE_ROLE_KEY
WAIT_AI="${WAIT_AI:-12}" bash execution/test-all-workflows.sh || TEST_FAIL=1

echo ""
echo "════════════════════════════════════════════════════════"
echo "Medident pilot — clinic_id: $CLINIC_ID"
echo ""
echo "Dashboard:  https://nefalixai.com/dashboard"
echo "  Manager:  akadirysr@gmail.com"
echo ""
echo "n8n UI (SSH tunnel):"
echo "  ssh -L 5678:127.0.0.1:5678 root@\$(curl -4 -s ifconfig.me)"
echo ""
if [[ "${TEST_FAIL:-0}" -eq 1 ]]; then
  echo "⚠ Bazı testler başarısız — OPENAI_API_KEY ve Evolution QR kontrol edin"
else
  echo "✓ Tüm smoke testler geçti"
fi
echo "════════════════════════════════════════════════════════"
