#!/usr/bin/env bash
# NefalixAI v2 statik site deploy'u.
# Dikkat: execution/deploy-to-vps.sh tüm stack kurulumunu tetikler ve Supabase reset riski taşır.
# Bu script sadece statik site dosyalarını + Caddy configini kopyalar ve Caddy servisini yeniler.
set -euo pipefail

TARGET="${1:?Kullanım: bash execution/deploy-v2-site.sh root@VPS_IP}"
REPO="$(cd "$(dirname "$0")/.." && pwd)"
REMOTE_DIR="/opt/nefalix"

cd "$REPO"

[[ -d nefalix-site-v2 ]] || {
  echo "nefalix-site-v2 klasörü bulunamadı" >&2
  exit 1
}

echo "▶ v2 site dosyaları kopyalanıyor: $TARGET:$REMOTE_DIR"
rsync -az --delete "$REPO/nefalix-site-v2/" "$TARGET:$REMOTE_DIR/nefalix-site-v2/"
rsync -az "$REPO/config/Caddyfile" "$TARGET:$REMOTE_DIR/config/Caddyfile"
rsync -az "$REPO/docker-compose.prod.yml" "$TARGET:$REMOTE_DIR/docker-compose.prod.yml"

echo "▶ Caddy yenileniyor"
ssh "$TARGET" "cd $REMOTE_DIR && docker compose -f docker-compose.yml -f docker-compose.evolution.yml -f docker-compose.prod.yml up -d caddy"

echo "✓ Deploy tamamlandı. DNS A kaydı gerekli: v2.nefalixai.com → VPS IP"
