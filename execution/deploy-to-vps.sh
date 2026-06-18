#!/usr/bin/env bash
# Mac'ten VPS'e repoyu kopyala ve kurulumu başlat
# Kullanım: bash execution/deploy-to-vps.sh root@203.0.113.10
set -euo pipefail

TARGET="${1:?Kullanım: bash execution/deploy-to-vps.sh root@VPS_IP}"
REPO="$(cd "$(dirname "$0")/.." && pwd)"
REMOTE_DIR="/opt/nefalix"

echo "▶ Hedef: $TARGET:$REMOTE_DIR"

ssh "$TARGET" "mkdir -p $REMOTE_DIR"

rsync -az --delete \
  --exclude '.git' \
  --exclude '.tmp' \
  --exclude 'node_modules' \
  --exclude '.env' \
  "$REPO/" "$TARGET:$REMOTE_DIR/"

ssh -t "$TARGET" "cd $REMOTE_DIR && chmod +x execution/*.sh && bash execution/setup-vps.sh"
