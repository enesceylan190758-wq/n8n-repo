#!/usr/bin/env bash
# Evolution API ilk kurulum — .env doldurur ve container'ları başlatır
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$REPO/.env"
EXAMPLE="$REPO/.env.example"

cd "$REPO"

append_env() {
  local key=$1 val=$2
  if ! grep -q "^${key}=" "$ENV_FILE" 2>/dev/null; then
    echo "${key}=${val}" >> "$ENV_FILE"
    echo "  + ${key}"
  fi
}

if [[ ! -f "$ENV_FILE" ]]; then
  cp "$EXAMPLE" "$ENV_FILE"
  echo "✓ .env oluşturuldu (.env.example'dan)"
fi

# Evolution secrets
if ! grep -q "^EVOLUTION_API_KEY=" "$ENV_FILE" 2>/dev/null; then
  KEY=$(openssl rand -hex 16)
  append_env "EVOLUTION_API_KEY" "$KEY"
fi

if ! grep -q "^EVOLUTION_POSTGRES_PASSWORD=" "$ENV_FILE" 2>/dev/null; then
  PG_PASS=$(openssl rand -hex 12)
  append_env "EVOLUTION_POSTGRES_PASSWORD" "$PG_PASS"
fi

append_env "EVOLUTION_PORT" "8080"
append_env "EVOLUTION_MANAGER_PORT" "8090"
append_env "EVOLUTION_SERVER_URL" "http://localhost:8080"

echo ""
echo "▶ Evolution container'ları başlatılıyor..."
docker compose -f docker-compose.yml -f docker-compose.evolution.yml up -d \
  evolution-postgres evolution-redis evolution-api

echo ""
echo "▶ Durum:"
docker compose -f docker-compose.yml -f docker-compose.evolution.yml ps \
  evolution-postgres evolution-redis evolution-api

echo ""
echo "════════════════════════════════════════════"
echo "✓ Evolution API hazır"
echo ""
echo "  Manager UI:  http://localhost:8080/manager"
echo "  API:         http://localhost:8080"
echo "  API Key:     $(grep '^EVOLUTION_API_KEY=' "$ENV_FILE" | cut -d= -f2-)"
echo ""
echo "  Sonraki adım: QR ile WhatsApp bağla (directives/evolution_setup.md)"
echo "  n8n entegrasyonu: sen onayladıktan sonra"
echo "════════════════════════════════════════════"
