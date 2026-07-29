#!/usr/bin/env bash
# SERP patch'lerini private nefalix-landing repo'ya kopyalar.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LANDING="${NEFALIX_LANDING_DIR:-$HOME/nefalix-landing}"

if [[ ! -d "$LANDING" ]]; then
  echo "HATA: nefalix-landing bulunamadı: $LANDING"
  echo "  export NEFALIX_LANDING_DIR=/path/to/nefalix-landing"
  exit 1
fi

echo "→ $LANDING"

cp "$ROOT/nefalix-landing/vercel.json" "$LANDING/vercel.json"
mkdir -p "$LANDING/api"
cp "$ROOT/nefalix-landing/api/geo-sitemap.js" "$LANDING/api/geo-sitemap.js"
cp "$ROOT/nefalix-site-v2/klinik-itibar-yonetimi.html" "$LANDING/klinik-itibar-yonetimi.html"

echo ""
echo "Manuel (diff ile uygula):"
echo "  patches/index-seo-head.html  → index.html nefalix-seo bloğu + title"
echo "  patches/urunler-seo-head.html → urunler.html SEO + H1"
echo ""
echo "Deploy: cd $LANDING && npx vercel --prod"
