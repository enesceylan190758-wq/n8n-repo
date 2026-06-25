#!/usr/bin/env bash
# Geçerli OpenAI anahtarını VPS + n8n credential'a yazar
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
TARGET="${1:-}"
KEY="${OPENAI_API_KEY:-}"

if [[ -z "$KEY" && -f "$REPO/.env" ]]; then
  KEY=$(grep '^OPENAI_API_KEY=' "$REPO/.env" | cut -d= -f2- || true)
fi

if [[ -z "$KEY" ]]; then
  echo "❌ OPENAI_API_KEY gerekli"
  echo "   OPENAI_API_KEY=sk-proj-... bash execution/set-openai-key.sh [root@VPS]"
  exit 1
fi

CODE=$(curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: Bearer $KEY" https://api.openai.com/v1/models)
if [[ "$CODE" != "200" ]]; then
  echo "❌ OpenAI anahtarı geçersiz (HTTP $CODE)"
  echo "   https://platform.openai.com/api-keys → Create new secret key"
  exit 1
fi

apply_local() {
  cd "$REPO"
  if grep -q '^OPENAI_API_KEY=' .env 2>/dev/null; then
    sed -i.bak "s|^OPENAI_API_KEY=.*|OPENAI_API_KEY=$KEY|" .env
  else
    echo "OPENAI_API_KEY=$KEY" >>.env
  fi
  rm -f .env.bak
  set -a && source .env && set +a
  python3 execution/setup-n8n-credentials.py
  source <(python3 -c "
import json
d=json.load(open('.tmp/n8n-credential-ids.json'))
print(f'export N8N_OPENAI_CRED_ID={d.get(\"openai\",\"\")}')
")
  export N8N_OPENAI_CRED_ID
  python3 execution/import-workflows.py
  echo "✓ Yerel n8n OpenAI güncellendi"
}

if [[ -n "$TARGET" ]]; then
  ssh "$TARGET" "grep -q '^OPENAI_API_KEY=' /opt/nefalix/.env && sed -i 's|^OPENAI_API_KEY=.*|OPENAI_API_KEY=${KEY}|' /opt/nefalix/.env || echo 'OPENAI_API_KEY=${KEY}' >> /opt/nefalix/.env"
  scp "$REPO/execution/setup-n8n-credentials.py" "$REPO/execution/import-workflows.py" \
    "$REPO/workflows/nefalix-06-inbox-routing.json" \
    "$TARGET:/opt/nefalix/execution/" "$TARGET:/opt/nefalix/workflows/" 2>/dev/null || true
  scp "$REPO/workflows/nefalix-06-inbox-routing.json" "$TARGET:/opt/nefalix/workflows/"
  ssh "$TARGET" "cd /opt/nefalix && set -a && source .env && set +a && python3 execution/setup-n8n-credentials.py && source <(python3 -c \"import json;d=json.load(open('.tmp/n8n-credential-ids.json'));print(f'export N8N_OPENAI_CRED_ID={d[\\\"openai\\\"]}')\") && python3 execution/import-workflows.py | grep -E 'Inbox|OpenAI|skip' || true"
  echo "✓ VPS OpenAI güncellendi ($TARGET)"
else
  apply_local
fi

echo "✓ OpenAI anahtarı geçerli — inbox AI taslak çalışır"
