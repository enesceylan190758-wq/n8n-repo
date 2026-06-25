#!/usr/bin/env bash
# Estesoft API kimlik bilgilerini VPS .env'e yazar (commit edilmez).
set -euo pipefail

TARGET="${1:-root@93.127.186.45}"
REMOTE_ENV="${2:-/opt/nefalix/.env}"

if [[ -f "$(dirname "$0")/../.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$(dirname "$0")/../.env"
  set +a
fi

: "${ESTESOFT_API_USERNAME:?ESTESOFT_API_USERNAME gerekli}"
: "${ESTESOFT_API_KEY:?ESTESOFT_API_KEY gerekli}"

TENANT="${ESTESOFT_TENANT_ID:-${ESTESOFT_API_USERNAME#*@}}"
BASE="${ESTESOFT_STELLA_API_BASE:-${ESTESOFT_BASE_URL:-https://medidentistanbul.stellamedi.com}}"
PASSWORD="${ESTESOFT_API_PASSWORD:-}"

ssh "$TARGET" "grep -q '^ESTESOFT_API_USERNAME=' '$REMOTE_ENV' 2>/dev/null && sed -i 's|^ESTESOFT_API_USERNAME=.*|ESTESOFT_API_USERNAME=${ESTESOFT_API_USERNAME}|' '$REMOTE_ENV' || echo 'ESTESOFT_API_USERNAME=${ESTESOFT_API_USERNAME}' >> '$REMOTE_ENV'"
ssh "$TARGET" "grep -q '^ESTESOFT_API_KEY=' '$REMOTE_ENV' 2>/dev/null && sed -i 's|^ESTESOFT_API_KEY=.*|ESTESOFT_API_KEY=${ESTESOFT_API_KEY}|' '$REMOTE_ENV' || echo 'ESTESOFT_API_KEY=${ESTESOFT_API_KEY}' >> '$REMOTE_ENV'"
ssh "$TARGET" "grep -q '^ESTESOFT_TENANT_ID=' '$REMOTE_ENV' 2>/dev/null && sed -i 's|^ESTESOFT_TENANT_ID=.*|ESTESOFT_TENANT_ID=${TENANT}|' '$REMOTE_ENV' || echo 'ESTESOFT_TENANT_ID=${TENANT}' >> '$REMOTE_ENV'"
ssh "$TARGET" "grep -q '^ESTESOFT_STELLA_API_BASE=' '$REMOTE_ENV' 2>/dev/null && sed -i 's|^ESTESOFT_STELLA_API_BASE=.*|ESTESOFT_STELLA_API_BASE=${BASE}|' '$REMOTE_ENV' || echo 'ESTESOFT_STELLA_API_BASE=${BASE}' >> '$REMOTE_ENV'"

if [[ -n "$PASSWORD" ]]; then
  ssh "$TARGET" "grep -q '^ESTESOFT_API_PASSWORD=' '$REMOTE_ENV' 2>/dev/null && sed -i 's|^ESTESOFT_API_PASSWORD=.*|ESTESOFT_API_PASSWORD=${PASSWORD}|' '$REMOTE_ENV' || echo 'ESTESOFT_API_PASSWORD=${PASSWORD}' >> '$REMOTE_ENV'"
fi

if [[ -n "${ESTESOFT_BASE_URL:-}" ]]; then
  ssh "$TARGET" "grep -q '^ESTESOFT_BASE_URL=' '$REMOTE_ENV' 2>/dev/null && sed -i 's|^ESTESOFT_BASE_URL=.*|ESTESOFT_BASE_URL=${ESTESOFT_BASE_URL}|' '$REMOTE_ENV' || echo 'ESTESOFT_BASE_URL=${ESTESOFT_BASE_URL}' >> '$REMOTE_ENV'"
fi

echo "✓ Estesoft env yazıldı ($TARGET)"
echo "  Estesoft webhook: https://api.nefalixai.com/webhook/nefalix/estesoft/webhook"
