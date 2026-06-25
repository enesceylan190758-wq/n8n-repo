#!/usr/bin/env bash
# VPS güvenlik sıkılaştırma — Docker portları UFW'yi bypass eder; DOCKER-USER + bind düzeltmesi
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$SCRIPT_DIR/.." && pwd)"

TARGET="${1:-root@93.127.186.45}"
REMOTE_DIR="${REMOTE_DIR:-/opt/nefalix}"

echo "▶ Güvenlik script'i VPS'e kopyalanıyor: $TARGET"
rsync -az "$REPO/execution/security-harden-vps-remote.sh" \
  "$REPO/docker-compose.prod.yml" \
  "$REPO/config/Caddyfile" \
  "$TARGET:$REMOTE_DIR/"

echo "▶ Uzak sıkılaştırma çalıştırılıyor..."
ssh -o ConnectTimeout=20 "$TARGET" "bash $REMOTE_DIR/security-harden-vps-remote.sh"

echo "✓ Tamamlandı — directives/security.md içindeki rotasyon listesini uygulayın"
