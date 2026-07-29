#!/usr/bin/env bash
# Mac: SERP patch → nefalix-landing → Vercel prod
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ "$(uname)" == "Darwin" && -d "/Users/enesceylan/nefalix-landing" ]]; then
  export NEFALIX_LANDING_DIR="/Users/enesceylan/nefalix-landing"
fi
LANDING="${NEFALIX_LANDING_DIR:-$HOME/nefalix-landing}"

echo "=== 1/3 SERP patch uygula ==="
python3 execution/apply-serp-patches.py "$LANDING"

echo ""
echo "=== 2/3 Vercel prod deploy ==="
cd "$LANDING"
if command -v vercel >/dev/null 2>&1; then
  vercel --prod --yes
else
  npx vercel --prod --yes
fi

echo ""
echo "=== 3/3 Smoke ==="
cd "$ROOT"
sleep 5
python3 execution/smoke-serp-public.py --check-redirects || true

echo ""
echo "Bitti. GSC: sitemap yeniden gönder + site:nefalix.com kontrol."
