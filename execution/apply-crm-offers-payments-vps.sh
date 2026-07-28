#!/usr/bin/env bash
# VPS'te crm_offers + crm_payments tablolarını oluştur (clinic-offers/payments 502 düzeltmesi).
# Mac'ten: bash execution/apply-crm-offers-payments-vps.sh
set -euo pipefail
TARGET="${1:-root@93.127.186.45}"
REPO="$(cd "$(dirname "$0")/.." && pwd)"
SQL="$REPO/supabase/migrations/20260727180000_crm_offers_payments_ensure.sql"
REMOTE_SQL="/tmp/crm_offers_payments_ensure.sql"
DB_CTN="${SUPABASE_DB_CONTAINER:-supabase_db_n8n-repo}"

[[ -f "$SQL" ]] || { echo "SQL yok: $SQL"; exit 1; }

echo "→ scp $SQL → $TARGET:$REMOTE_SQL"
scp -o ConnectTimeout=20 "$SQL" "$TARGET:$REMOTE_SQL"
ssh -o ConnectTimeout=20 "$TARGET" bash -s <<EOF
set -euo pipefail
docker cp "$REMOTE_SQL" "$DB_CTN:$REMOTE_SQL"
docker exec "$DB_CTN" psql -U postgres -d postgres -v ON_ERROR_STOP=1 -f "$REMOTE_SQL"
echo "OK: crm_offers / crm_payments"
docker exec "$DB_CTN" psql -U postgres -d postgres -c "\\dt public.crm_offers" -c "\\dt public.crm_payments"
EOF

echo
echo "OK: crm_offers / crm_payments tabloları VPS'te."
echo "Smoke (Mac, login cookie ile):"
echo "  curl -sS -o /dev/null -w '%{http_code}\\n' -b cookies.txt \\"
echo "    'https://nefalix.com/api/blog?action=clinic-offers'"
echo "  → 200 olmalı (401=oturum yok, 502=tablo/proxy hâlâ kırık)"
echo "Sonra UI: bash execution/deploy-hasta-crm-from-extract.sh"
