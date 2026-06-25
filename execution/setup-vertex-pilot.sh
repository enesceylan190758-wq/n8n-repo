#!/usr/bin/env bash
# Vertex AI pilot kurulumu — VPS veya local /opt/nefalix
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

KEY_PATH="${GOOGLE_APPLICATION_CREDENTIALS:-$ROOT/.tmp/gcp-service-account.json}"
ENV_FILE="$ROOT/.env"

red() { echo "❌ $*" >&2; }
green() { echo "✓ $*"; }
step() { echo ""; echo "▶ $*"; }

if [[ ! -f "$KEY_PATH" ]]; then
  red "GCP service account JSON yok: $KEY_PATH"
  echo ""
  echo "Google Cloud Console adımları:"
  echo "  1. https://console.cloud.google.com/iam-admin/serviceaccounts?project=utility-cumulus-484107-v3"
  echo "  2. + CREATE SERVICE ACCOUNT → ad: nefalix-vertex"
  echo "  3. Rol: Vertex AI User"
  echo "  4. Keys → Add key → JSON → indir"
  echo "  5. VPS'e yükle:"
  echo "     scp ~/Downloads/project-*.json root@93.127.186.45:/opt/nefalix/.tmp/gcp-service-account.json"
  echo "  6. Tekrar çalıştır: bash execution/setup-vertex-pilot.sh"
  exit 1
fi

step "PyJWT kontrolü"
if ! python3 -c "import jwt" 2>/dev/null; then
  pip3 install --user PyJWT >/dev/null 2>&1 || pip3 install PyJWT
fi
green "PyJWT hazır"

step ".env GCP değişkenleri"
touch "$ENV_FILE"
upsert_env() {
  local k="$1" v="$2"
  if grep -q "^${k}=" "$ENV_FILE" 2>/dev/null; then
    sed -i.bak "s|^${k}=.*|${k}=${v}|" "$ENV_FILE"
  else
    echo "${k}=${v}" >> "$ENV_FILE"
  fi
}
upsert_env GCP_PROJECT_ID "${GCP_PROJECT_ID:-utility-cumulus-484107-v3}"
upsert_env GCP_REGION "${GCP_REGION:-europe-west1}"
upsert_env VERTEX_GEMINI_MODEL "${VERTEX_GEMINI_MODEL:-gemini-1.5-flash}"
upsert_env GOOGLE_APPLICATION_CREDENTIALS "$KEY_PATH"
green ".env güncellendi"

step "GCP access token"
set -a
# shellcheck disable=SC1090
source "$ENV_FILE" 2>/dev/null || true
set +a
export GOOGLE_APPLICATION_CREDENTIALS="$KEY_PATH"
WRITE_GCP_TOKEN_TO_ENV=1 python3 execution/refresh-gcp-access-token.py >/dev/null
set -a
source "$ENV_FILE"
set +a
green "GCP_ACCESS_TOKEN yazıldı"

step "n8n Vertex credential"
python3 execution/setup-n8n-credentials.py
# shellcheck disable=SC1090
source <(python3 -c "import json;d=json.load(open('.tmp/n8n-credential-ids.json'));print(f'export N8N_VERTEX_CRED_ID={d.get(\"vertex\",\"\")}');print(f'export N8N_SUPABASE_CRED_ID={d.get(\"supabase\",\"\")}')")
green "N8N_VERTEX_CRED_ID=${N8N_VERTEX_CRED_ID:-?}"

step "Docker n8n yeniden başlat"
docker compose up -d n8n
sleep 5

step "Workflow import (Vertex)"
python3 execution/import-workflows.py

step "Vertex test çağrısı"
python3 -c "
import sys
sys.path.insert(0, 'execution')
from vertex_gemini import vertex_generate
print(vertex_generate('Merhaba, tek kelimeyle yanıt ver: tamam', system='Kısa yanıt ver.'))
" && green "Vertex API çalışıyor" || red "Vertex test başarısız — API enable / rol kontrol"

step "Saatlik token cron"
CRON_LINE="0 * * * * cd $ROOT && WRITE_GCP_TOKEN_TO_ENV=1 python3 execution/refresh-gcp-access-token.py && docker compose up -d n8n"
if crontab -l 2>/dev/null | grep -qF "refresh-gcp-access-token.py"; then
  green "Cron zaten var"
else
  (crontab -l 2>/dev/null; echo "$CRON_LINE") | crontab -
  green "Cron eklendi"
fi

echo ""
green "Vertex pilot kurulumu tamamlandı."
echo "  Model: ${VERTEX_GEMINI_MODEL:-gemini-1.5-flash}"
echo "  Proje: ${GCP_PROJECT_ID:-utility-cumulus-484107-v3}"
