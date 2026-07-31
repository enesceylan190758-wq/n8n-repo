#!/usr/bin/env bash
# Canlı nefalix.com public smoke: asset + kartvizit QR.
# Guardian / deploy sonrası tek giriş.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BASE="${1:-https://nefalix.com}"
failed=0

python3 "$ROOT/execution/smoke-site-assets.py" --base "$BASE" || failed=1
python3 "$ROOT/execution/smoke-kartvizit.py" --base "$BASE" || failed=1

if [[ "$failed" -ne 0 ]]; then
  echo "FAIL public smoke — directives/kartvizit_qr.md + site_assets.md" >&2
  exit 1
fi
echo "✓ smoke-nefalix-public OK"
