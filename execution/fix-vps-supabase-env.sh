#!/usr/bin/env bash
# VPS .env içine Supabase anahtarlarını yazar (boş kalmışsa)
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"

STATUS=$(npx supabase status -o env 2>/dev/null || true)
[[ -n "$STATUS" ]] || { echo "❌ supabase status alınamadı"; exit 1; }

ANON=$(echo "$STATUS" | grep '^ANON_KEY=' | cut -d= -f2- | tr -d '"')
SERVICE=$(echo "$STATUS" | grep '^SERVICE_ROLE_KEY=' | cut -d= -f2- | tr -d '"')
API_URL=$(echo "$STATUS" | grep '^API_URL=' | cut -d= -f2- | tr -d '"')

set_kv() {
  local key=$1 val=$2
  if grep -q "^${key}=" .env; then
    sed -i.bak "s|^${key}=.*|${key}=${val}|" .env
  else
    echo "${key}=${val}" >>.env
  fi
}

set_kv SUPABASE_ANON_KEY "$ANON"
set_kv SUPABASE_SERVICE_ROLE_KEY "$SERVICE"
# n8n Docker container — 127.0.0.1 değil host gateway
set_kv SUPABASE_URL "http://host.docker.internal:54321"
set_kv N8N_SUPABASE_HOST "http://host.docker.internal:54321"
rm -f .env.bak

echo "✓ Supabase anahtarları .env'e yazıldı"
