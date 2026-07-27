#!/usr/bin/env bash
# Pack'li Hasta CRM HTML'i Mac nefalix-landing'e kopyala + Vercel prod.
# Cloud agent Vercel token olmadığı için Mac'te çalıştırılır.
set -euo pipefail
REPO="${NEFALIX_REPO:-$HOME/n8n-repo}"
LANDING="${NEFALIX_LANDING:-$HOME/nefalix-landing}"
EXTRACT="$REPO/.tmp/nefalix-landing-extract"

if [[ ! -f "$EXTRACT/nefalix-hasta-crm.html" ]]; then
  echo "Extract yok: $EXTRACT — önce cloud pack veya:"
  echo "  cd $REPO && python3 execution/pack-nefalix-hasta-crm.py"
  exit 1
fi

mkdir -p "$LANDING/nefalix-hasta-crm-app"
rsync -a "$EXTRACT/nefalix-hasta-crm-app/" "$LANDING/nefalix-hasta-crm-app/"
cp -f "$EXTRACT/nefalix-hasta-crm.html" "$LANDING/nefalix-hasta-crm.html"
echo "Synced → $LANDING"
cd "$LANDING"
vercel --prod --yes
echo "Smoke: https://nefalix.com/hasta-crm — Yeni Teklif (otel), Yeni Satış (EUR/yöntem)"
