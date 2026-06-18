#!/usr/bin/env bash
# Vercel'i VPS sabit URL'lerine bağla (tunnel kalkar)
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

HOST="${N8N_PUBLIC_HOST:-api.nefalixai.com}"
DASH_URL="https://${HOST}/webhook/nefalix/dashboard/data"
SEND_URL="https://${HOST}/webhook/nefalix/inbox/send"

LANDING="${HOME}/nefalix-landing"
if [[ ! -d "$LANDING" ]]; then
  echo "❌ $LANDING bulunamadı"
  exit 1
fi

echo "▶ Dashboard URL: $DASH_URL"
echo "▶ Inbox send:    $SEND_URL"

cd "$LANDING"
npx vercel env rm N8N_DASHBOARD_URL production -y 2>/dev/null || true
printf '%s' "$DASH_URL" | npx vercel env add N8N_DASHBOARD_URL production
npx vercel env rm N8N_INBOX_SEND_URL production -y 2>/dev/null || true
printf '%s' "$SEND_URL" | npx vercel env add N8N_INBOX_SEND_URL production
npx vercel --prod --yes

echo "✓ Vercel güncellendi — https://nefalixai.com/dashboard"
