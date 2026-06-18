#!/usr/bin/env bash
# Nefalix VPS tam kurulum — Ubuntu 24.04, İstanbul TR
# Mac'ten: bash execution/deploy-to-vps.sh root@VPS_IP
# Sunucuda: cd /opt/nefalix && bash execution/setup-vps.sh
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"

log() { echo "▶ $*"; }
die() { echo "❌ $*" >&2; exit 1; }

[[ -f docker-compose.yml ]] || die "n8n-repo kök dizininde çalıştırın"

# --- .env ---
if [[ ! -f .env ]]; then
  log ".env yok — .env.vps.example kopyalanıyor"
  cp .env.vps.example .env
  gen() { openssl rand -hex "${1:-16}"; }
  sed -i.bak \
    -e "s/CHANGE_ME_STRONG/$(gen 12)/" \
    -e "s/CHANGE_ME_openssl_rand_hex_32/$(gen 32)/" \
    -e "s/CHANGE_ME_openssl_rand_hex_16/$(gen 16)/" \
    -e "s/CHANGE_ME_openssl_rand_hex_12/$(gen 12)/" \
    .env 2>/dev/null || true
  rm -f .env.bak
  die ".env oluşturuldu — N8N_PUBLIC_HOST, ACME_EMAIL, N8N_PASSWORD kontrol edin, tekrar çalıştırın"
fi

set -a
# shellcheck disable=SC1091
source .env
set +a

: "${N8N_ENCRYPTION_KEY:?N8N_ENCRYPTION_KEY .env içinde olmalı}"
: "${N8N_PUBLIC_HOST:?N8N_PUBLIC_HOST gerekli (ör. api.nefalixai.com)}"

# --- bootstrap (root) ---
if [[ "$(id -u)" -eq 0 ]] && ! command -v docker >/dev/null; then
  log "Docker kuruluyor…"
  bash "$REPO/execution/bootstrap-vps.sh"
fi

# --- Node (Supabase CLI) ---
if ! command -v node >/dev/null; then
  log "Node.js 22 kuruluyor…"
  curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
  sudo apt-get install -y -qq nodejs
fi

# --- DNS uyarısı ---
PUBLIC_IP=$(curl -fsSL -4 ifconfig.me 2>/dev/null || curl -fsSL -4 icanhazip.com 2>/dev/null || true)
log "Sunucu IP: ${PUBLIC_IP:-bilinmiyor}"
log "DNS A kayıtları bu IP'ye işaret etmeli:"
echo "   ${N8N_PUBLIC_HOST} → ${PUBLIC_IP}"
echo "   ${EVOLUTION_PUBLIC_HOST:-evo.nefalixai.com} → ${PUBLIC_IP}"

# --- Docker stack ---
log "Docker stack başlatılıyor…"
docker compose \
  -f docker-compose.yml \
  -f docker-compose.evolution.yml \
  -f docker-compose.prod.yml \
  up -d

log "n8n healthy bekleniyor…"
for i in $(seq 1 60); do
  curl -sf http://127.0.0.1:5678/healthz >/dev/null && break
  sleep 2
done
curl -sf http://127.0.0.1:5678/healthz >/dev/null || die "n8n ayağa kalkmadı"

# --- Supabase ---
if ! docker ps --format '{{.Names}}' | grep -q supabase_kong; then
  log "Supabase başlatılıyor (ilk seferde birkaç dakika)…"
  npx supabase start
fi

log "Migration uygulanıyor…"
npx supabase db reset --yes

# Supabase anahtarlarını .env'e yaz
STATUS=$(npx supabase status -o env 2>/dev/null || true)
if [[ -n "$STATUS" ]]; then
  ANON=$(echo "$STATUS" | rg '^ANON_KEY=' | cut -d= -f2- || true)
  SERVICE=$(echo "$STATUS" | rg '^SERVICE_ROLE_KEY=' | cut -d= -f2- || true)
  API_URL=$(echo "$STATUS" | rg '^API_URL=' | cut -d= -f2- || true)
  if [[ -n "$ANON" ]]; then
    grep -q '^SUPABASE_ANON_KEY=' .env && sed -i.bak "s|^SUPABASE_ANON_KEY=.*|SUPABASE_ANON_KEY=$ANON|" .env || echo "SUPABASE_ANON_KEY=$ANON" >>.env
  fi
  if [[ -n "$SERVICE" ]]; then
    grep -q '^SUPABASE_SERVICE_ROLE_KEY=' .env && sed -i.bak "s|^SUPABASE_SERVICE_ROLE_KEY=.*|SUPABASE_SERVICE_ROLE_KEY=$SERVICE|" .env || echo "SUPABASE_SERVICE_ROLE_KEY=$SERVICE" >>.env
  fi
  if [[ -n "$API_URL" ]]; then
    grep -q '^SUPABASE_URL=' .env && sed -i.bak "s|^SUPABASE_URL=.*|SUPABASE_URL=$API_URL|" .env || echo "SUPABASE_URL=$API_URL" >>.env
  fi
  rm -f .env.bak
fi

# --- Workflows ---
log "n8n workflow import…"
export N8N_URL="${N8N_URL:-http://127.0.0.1:5678}"
python3 execution/import-workflows.py

log "Klinik profil senkron…"
SUPABASE_URL="${SUPABASE_URL:-http://127.0.0.1:54321}" \
SUPABASE_SERVICE_ROLE_KEY="$(grep '^SUPABASE_SERVICE_ROLE_KEY=' .env | cut -d= -f2-)" \
  python3 execution/sync-clinic-profile.py || true

# --- Evolution ---
if [[ -x execution/setup-evolution.sh ]]; then
  log "Evolution API (WhatsApp) — QR gerekebilir"
  bash execution/setup-evolution.sh || log "Evolution setup atlandı veya manuel QR gerekir"
fi

echo ""
echo "════════════════════════════════════════════════════════"
echo "✓ VPS stack hazır"
echo ""
echo "  n8n UI (SSH tunnel): ssh -L 5678:127.0.0.1:5678 root@${PUBLIC_IP}"
echo "                       → http://localhost:5678"
echo "  Webhook:             https://${N8N_PUBLIC_HOST}/webhook/..."
echo "  Evolution:           https://${EVOLUTION_PUBLIC_HOST:-evo.nefalixai.com}"
echo "  Supabase Studio:     npx supabase status"
echo ""
echo "Sonraki adım (Mac'te):"
echo "  bash execution/update-vercel-vps-urls.sh"
echo "════════════════════════════════════════════════════════"
