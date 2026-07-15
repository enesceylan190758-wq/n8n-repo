#!/usr/bin/env bash
# MANUS_API_KEY'i yerel .env'den VPS /opt/nefalix/.env'e yazar (değer loglanmaz).
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
TARGET="${1:-root@93.127.186.45}"
REMOTE_ENV="${2:-/opt/nefalix/.env}"
LOCAL_ENV="$REPO/.env"

if [[ ! -f "$LOCAL_ENV" ]]; then
  echo "❌ $LOCAL_ENV bulunamadı"
  exit 1
fi

KEY="$(grep '^MANUS_API_KEY=' "$LOCAL_ENV" | cut -d= -f2- || true)"
if [[ -z "$KEY" ]]; then
  echo "❌ MANUS_API_KEY yerel .env'de boş veya yok"
  exit 1
fi

ssh "$TARGET" "grep -q '^MANUS_API_KEY=' '$REMOTE_ENV' 2>/dev/null && sed -i 's|^MANUS_API_KEY=.*|MANUS_API_KEY=${KEY}|' '$REMOTE_ENV' || echo 'MANUS_API_KEY=${KEY}' >> '$REMOTE_ENV'"
echo "✓ MANUS_API_KEY VPS'e yazıldı ($TARGET)"
