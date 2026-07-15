#!/usr/bin/env bash
# HTML sosyal görsel render — Puppeteer (sistem Chrome kullanır, Chromium indirmez)
set -euo pipefail
DIR="$(cd "$(dirname "$0")/.." && pwd)/.tmp/sosyal_medya_postlar"
mkdir -p "$DIR"
cd "$DIR"
if [[ ! -d node_modules/puppeteer ]]; then
  npm init -y >/dev/null 2>&1 || true
  PUPPETEER_SKIP_DOWNLOAD=true npm install puppeteer --no-save
fi
echo "✓ Puppeteer hazır (Chrome: ${CHROME_PATH:-/usr/local/bin/google-chrome})"
