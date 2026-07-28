#!/usr/bin/env bash
# Saha CRM (crm.html) → nefalix.com/saha prod deploy
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEPLOY_DIR="${DEPLOY_DIR:-$ROOT/.tmp/nefalix-landing-deploy}"
PATCH_CRM="$ROOT/patches/nefalix-landing/crm.html"
VERCEL="${VERCEL:-vercel}"

if [[ ! -f "$PATCH_CRM" ]]; then
  echo "Patch crm.html bulunamadı: $PATCH_CRM" >&2
  exit 1
fi

mkdir -p "$DEPLOY_DIR"
cp "$PATCH_CRM" "$DEPLOY_DIR/crm.html"
echo "crm.html güncellendi ($(wc -c < "$DEPLOY_DIR/crm.html") byte)"

cd "$DEPLOY_DIR"
$VERCEL whoami
$VERCEL --prod --yes

echo "Deploy tamam. Kontrol: https://nefalix.com/saha"
