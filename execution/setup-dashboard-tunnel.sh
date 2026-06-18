#!/usr/bin/env bash
# Dashboard için cloudflared tunnel + Vercel env güncelle
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
CF="${REPO}/.tmp/bin/cloudflared"
LOG="${REPO}/.tmp/dashboard-tunnel.log"
LANDING="${HOME}/nefalix-landing"

if [[ ! -x "$CF" ]]; then
  mkdir -p "${REPO}/.tmp/bin"
  curl -fsSL "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-arm64.tgz" \
    -o /tmp/cloudflared.tgz
  tar -xzf /tmp/cloudflared.tgz -C "${REPO}/.tmp/bin" cloudflared
  chmod +x "$CF"
fi

pkill -f "cloudflared tunnel --url http://localhost:5678" 2>/dev/null || true
sleep 1
nohup "$CF" tunnel --url http://localhost:5678 >"$LOG" 2>&1 &
echo "▶ Tunnel başlatıldı, URL bekleniyor…"
for i in $(seq 1 30); do
  URL=$(grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' "$LOG" | head -1 || true)
  [[ -n "$URL" ]] && break
  sleep 1
done
if [[ -z "$URL" ]]; then
  echo "❌ Tunnel URL alınamadı. Log: $LOG"
  exit 1
fi

API_URL="${URL}/webhook/nefalix/dashboard/data"
echo "✓ Tunnel: $API_URL"

if [[ -d "$LANDING" ]]; then
  cd "$LANDING"
  printf '%s' "$API_URL" | npx vercel env add N8N_DASHBOARD_URL production 2>/dev/null || \
    npx vercel env rm N8N_DASHBOARD_URL production -y 2>/dev/null; \
    printf '%s' "$API_URL" | npx vercel env add N8N_DASHBOARD_URL production
  SEND_URL="${URL}/webhook/nefalix/inbox/send"
  printf '%s' "$SEND_URL" | npx vercel env add N8N_INBOX_SEND_URL production 2>/dev/null || \
    npx vercel env rm N8N_INBOX_SEND_URL production -y 2>/dev/null; \
    printf '%s' "$SEND_URL" | npx vercel env add N8N_INBOX_SEND_URL production
  npx vercel --prod --yes >/dev/null
  echo "✓ Vercel env + deploy güncellendi"
fi

echo ""
echo "Dashboard: https://nefalixai.com/dashboard"
echo "Mac + Docker + Supabase + n8n açık kalsın."
