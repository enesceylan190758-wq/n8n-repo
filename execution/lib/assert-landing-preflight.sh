#!/usr/bin/env bash
# vercel --prod öncesi: kartvizit + kritik asset'ler landing'de olmalı.
# Kaynak: execution/*.sh içinden `source` edilir.
#
# Kullanım (landing cwd veya LANDING set):
#   source "$ROOT/execution/lib/assert-landing-preflight.sh"
#   assert_landing_preflight "$LANDING"
assert_landing_preflight() {
  local landing="${1:-.}"
  local missing=0
  local f

  echo "▶ preflight: $landing"

  for f in \
    shared.css \
    shared.js \
    index.html \
    k/enes.html \
    k/abdulkadir.html \
    k/card.css \
    k/enes.vcf \
    k/abdulkadir.vcf
  do
    if [[ ! -f "$landing/$f" ]]; then
      echo "  ✗ eksik: $f" >&2
      missing=1
    else
      echo "  ✓ $f"
    fi
  done

  # vercel.json içinde /k rewrite
  if [[ -f "$landing/vercel.json" ]]; then
    if ! grep -q '"/k/enes"' "$landing/vercel.json"; then
      echo "  ✗ vercel.json içinde /k/enes rewrite yok" >&2
      missing=1
    else
      echo "  ✓ vercel.json /k rewrite"
    fi
  else
    echo "  ✗ vercel.json yok" >&2
    missing=1
  fi

  if [[ "$missing" -ne 0 ]]; then
    echo "HATA: Deploy iptal — kartvizit/CSS eksik. Silinen dosyaları geri yükle:" >&2
    echo "  bash execution/deploy-kartvizit-cards.sh --dry-run" >&2
    echo "  bash execution/fix-landing-shared-assets.sh --dry-run" >&2
    echo "  directives/kartvizit_qr.md · directives/site_assets.md" >&2
    return 1
  fi
  echo "▶ preflight OK"
  return 0
}
