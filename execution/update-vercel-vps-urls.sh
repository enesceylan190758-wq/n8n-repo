#!/usr/bin/env bash
# Vercel'i VPS sabit URL'lerine bağla (tunnel kalkar)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO"

# shellcheck source=lib/resolve-npx.sh
source "$SCRIPT_DIR/lib/resolve-npx.sh"
NPX="$(resolve_npx)" || exit 1

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

HOST="${N8N_PUBLIC_HOST:-api.nefalixai.com}"
DASH_URL="https://${HOST}/webhook/nefalix/dashboard/data"
SEND_URL="https://${HOST}/webhook/nefalix/inbox/send"
CLEAR_URL="https://${HOST}/webhook/nefalix/inbox/clear"
REVIEW_URL="https://${HOST}/webhook/nefalix/google/review-approve"
# Web chat — import-web-chatbot.py çıktısından veya n8n UI
CHAT_URL="${N8N_CHAT_WEBHOOK_URL:-https://${HOST}/webhook/CHAT_WEBHOOK_ID/chat}"

LANDING="${HOME}/nefalix-landing"
if [[ ! -d "$LANDING" ]]; then
  echo "❌ $LANDING bulunamadı"
  exit 1
fi

echo "▶ Dashboard URL: $DASH_URL"
echo "▶ Inbox send:    $SEND_URL"
echo "▶ Inbox clear:   $CLEAR_URL"
echo "▶ Review approve: $REVIEW_URL"
echo "▶ Site chat:     $CHAT_URL"

cd "$LANDING"
"$NPX" vercel env rm N8N_DASHBOARD_URL production -y 2>/dev/null || true
printf '%s' "$DASH_URL" | "$NPX" vercel env add N8N_DASHBOARD_URL production
"$NPX" vercel env rm N8N_INBOX_SEND_URL production -y 2>/dev/null || true
printf '%s' "$SEND_URL" | "$NPX" vercel env add N8N_INBOX_SEND_URL production
"$NPX" vercel env rm N8N_INBOX_CLEAR_URL production -y 2>/dev/null || true
printf '%s' "$CLEAR_URL" | "$NPX" vercel env add N8N_INBOX_CLEAR_URL production
"$NPX" vercel env rm N8N_GOOGLE_REVIEW_APPROVE_URL production -y 2>/dev/null || true
printf '%s' "$REVIEW_URL" | "$NPX" vercel env add N8N_GOOGLE_REVIEW_APPROVE_URL production

# nefalix-chat.js sabit webhook URL
if [[ -f nefalix-chat.js ]] && [[ "$CHAT_URL" != *"CHAT_WEBHOOK_ID"* ]]; then
  perl -pi -e "s|const WEBHOOK_URL =\\s*'[^']*'|const WEBHOOK_URL = '${CHAT_URL}'|" nefalix-chat.js
  echo "▶ nefalix-chat.js güncellendi"
fi
"$NPX" vercel --prod --yes

echo "✓ Vercel güncellendi — https://nefalixai.com/dashboard"
