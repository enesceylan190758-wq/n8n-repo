#!/usr/bin/env bash
# Chatwoot kurulum + Evolution bağlama (VPS: /opt/nefalix)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

COMPOSE=(docker compose
  -f docker-compose.yml
  -f docker-compose.evolution.yml
  -f docker-compose.prod.yml
  -f docker-compose.chatwoot.yml
)

rand() { openssl rand -hex 24; }

append_env() {
  local k="$1" v="$2"
  if grep -q "^${k}=" .env 2>/dev/null; then
    return 0
  fi
  echo "${k}=${v}" >> .env
  echo "  + ${k}"
}

echo "== Chatwoot env =="
append_env CHATWOOT_PUBLIC_HOST "chat.nefalix.com"
append_env CHATWOOT_POSTGRES_PASSWORD "$(rand)"
append_env CHATWOOT_REDIS_PASSWORD "$(rand)"
append_env CHATWOOT_SECRET_KEY_BASE "$(openssl rand -hex 64)"
append_env CHATWOOT_ADMIN_EMAIL "enes@nefalix.com"
# sabit değilse üret; .env'e yaz
if ! grep -q "^CHATWOOT_ADMIN_PASSWORD=" .env 2>/dev/null; then
  append_env CHATWOOT_ADMIN_PASSWORD "$(printf "Nfx!%s" "$(openssl rand -hex 6)")"
fi

set -a
# shellcheck disable=SC1091
source .env
set +a

echo "== Start Chatwoot containers =="
"${COMPOSE[@]}" up -d chatwoot-postgres chatwoot-redis
sleep 5
"${COMPOSE[@]}" up -d chatwoot-rails chatwoot-sidekiq
"${COMPOSE[@]}" up -d caddy

echo "== Wait rails =="
for i in $(seq 1 40); do
  if docker exec nefalix-chatwoot-rails wget -qO- http://127.0.0.1:3000/ >/dev/null 2>&1; then
    echo "rails up"
    break
  fi
  # DB prepare may be needed first
  sleep 5
done

echo "== DB prepare =="
docker exec nefalix-chatwoot-rails bundle exec rails db:chatwoot_prepare || true

echo "== Admin user =="
docker exec -e ADMIN_EMAIL="$CHATWOOT_ADMIN_EMAIL" -e ADMIN_PASSWORD="$CHATWOOT_ADMIN_PASSWORD" \
  nefalix-chatwoot-rails bundle exec rails runner "
email = ENV['ADMIN_EMAIL']
pass  = ENV['ADMIN_PASSWORD']
u = User.find_by(email: email)
if u.nil?
  u = User.new(name: 'Nefalix Admin', email: email, password: pass, password_confirmation: pass)
  u.skip_confirmation! if u.respond_to?(:skip_confirmation!)
  u.save!
  puts \"created user #{u.id}\"
else
  u.password = pass
  u.password_confirmation = pass
  u.save!
  puts \"updated user #{u.id}\"
end
acc = Account.first || Account.create!(name: 'Nefalix')
au = AccountUser.find_by(account_id: acc.id, user_id: u.id)
if au.nil?
  AccountUser.create!(account_id: acc.id, user_id: u.id, role: :administrator)
end
token = u.access_token&.token
if token.nil? && u.respond_to?(:access_token) && u.access_token.nil?
  # AccessToken may auto-create; force
  at = AccessToken.find_or_create_by!(owner: u)
  token = at.token
end
puts \"ACCOUNT_ID=#{acc.id}\"
puts \"USER_ID=#{u.id}\"
puts \"API_TOKEN=#{token}\"
" | tee /tmp/chatwoot-bootstrap.txt

ACCOUNT_ID=$(grep '^ACCOUNT_ID=' /tmp/chatwoot-bootstrap.txt | cut -d= -f2)
API_TOKEN=$(grep '^API_TOKEN=' /tmp/chatwoot-bootstrap.txt | cut -d= -f2)

if [[ -z "${ACCOUNT_ID}" || -z "${API_TOKEN}" || "${API_TOKEN}" == "" ]]; then
  echo "WARN: API token alınamadı — Chatwoot UI → Profile → Access Token"
  ACCOUNT_ID="${ACCOUNT_ID:-1}"
else
  # persist for Evolution wire
  if grep -q "^CHATWOOT_ACCOUNT_ID=" .env; then
    sed -i "s/^CHATWOOT_ACCOUNT_ID=.*/CHATWOOT_ACCOUNT_ID=${ACCOUNT_ID}/" .env
  else
    echo "CHATWOOT_ACCOUNT_ID=${ACCOUNT_ID}" >> .env
  fi
  if grep -q "^CHATWOOT_API_TOKEN=" .env; then
    sed -i "s/^CHATWOOT_API_TOKEN=.*/CHATWOOT_API_TOKEN=${API_TOKEN}/" .env
  else
    echo "CHATWOOT_API_TOKEN=${API_TOKEN}" >> .env
  fi
fi

CW_URL="https://${CHATWOOT_PUBLIC_HOST:-chat.nefalix.com}"
INSTANCE="${EVOLUTION_INSTANCE:-nefalix-crm}"
EVO_KEY="${EVOLUTION_API_KEY:?EVOLUTION_API_KEY}"
EVO_URL="${EVOLUTION_API_URL:-https://evo.nefalix.com}"

echo "== Evolution ↔ Chatwoot (${INSTANCE}) =="
curl -sS -X POST "${EVO_URL}/chatwoot/set/${INSTANCE}" \
  -H "apikey: ${EVO_KEY}" \
  -H "Content-Type: application/json" \
  -d "{
    \"enabled\": true,
    \"accountId\": \"${ACCOUNT_ID:-1}\",
    \"token\": \"${API_TOKEN}\",
    \"url\": \"${CW_URL}\",
    \"signMsg\": false,
    \"reopenConversation\": true,
    \"conversationPending\": false,
    \"nameInbox\": \"Nefalix CRM WhatsApp\",
    \"mergeBrazilContacts\": false,
    \"importContacts\": true,
    \"importMessages\": true,
    \"daysLimitImportMessages\": 7,
    \"signDelimiter\": \"\\n\",
    \"autoCreate\": true,
    \"organization\": \"Nefalix\",
    \"logo\": \"https://nefalix.com/assets/brand/nefalix-logo.png\"
  }" | tee /tmp/chatwoot-evo-set.json
echo

echo ""
echo "OK — Chatwoot: ${CW_URL}"
echo "Login: ${CHATWOOT_ADMIN_EMAIL} / (CHATWOOT_ADMIN_PASSWORD in .env)"
echo "CRM panel iframe → ${CW_URL}/app"
