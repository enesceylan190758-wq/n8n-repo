#!/usr/bin/env bash
# Acil: nefalix.com stil kırığı — /shared.css + /shared.js Vercel'de 404.
# Kaynak: private ~/nefalix-landing (bu cloud ortamında yok). Mac'te çalıştır.
#
# Kullanım:
#   bash execution/fix-landing-shared-assets.sh
#   bash execution/fix-landing-shared-assets.sh --dry-run
#   NEFALIX_LANDING_DIR=/path/to/nefalix-landing bash execution/fix-landing-shared-assets.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=lib/resolve-npx.sh
source "$ROOT/execution/lib/resolve-npx.sh"
NPX="$(resolve_npx)" || exit 1

LANDING="${NEFALIX_LANDING_DIR:-$HOME/nefalix-landing}"
DRY=0
[[ "${1:-}" == "--dry-run" ]] && DRY=1

if [[ ! -d "$LANDING" ]]; then
  echo "HATA: nefalix-landing bulunamadı: $LANDING" >&2
  echo "  export NEFALIX_LANDING_DIR=/Users/enesceylan/nefalix-landing" >&2
  exit 1
fi

cd "$LANDING"
echo "→ landing: $LANDING"

restore_if_missing() {
  local f="$1"
  if [[ -f "$f" ]]; then
    echo "  ✓ $f ($(wc -c <"$f" | tr -d ' ') bytes)"
    return 0
  fi
  echo "  ! $f eksik — git'ten geri yükleniyor"
  if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    git checkout HEAD -- "$f" 2>/dev/null \
      || git log --all --pretty=format:'%H' -- "$f" | head -1 | xargs -I{} git checkout {} -- "$f"
  fi
  if [[ ! -f "$f" ]]; then
    echo "HATA: $f kurtarılamadı. Mac'te: git log -- shared.css && git checkout <commit> -- shared.css" >&2
    exit 1
  fi
  echo "  ✓ $f geri yüklendi ($(wc -c <"$f" | tr -d ' ') bytes)"
}

restore_if_missing shared.css
restore_if_missing shared.js

# HTML çoğu sayfada shared.css istiyor; site-v2 kopyası yetersiz (home-refresh yok).
# Yanlışlıkla site-v2 ile ezildiyse uyar.
if ! grep -q 'home-refresh\|refresh-hero\|liquid-sapphire\|logo-lockup\|\-\-purple-deep' shared.css; then
  echo "UYARI: shared.css içinde home-refresh / purple token yok — dosya eksik veya yanlış kopya olabilir." >&2
  echo "  git log --oneline -- shared.css | head" >&2
  echo "  git checkout <iyi-commit> -- shared.css shared.js" >&2
fi

# Kartvizit silinmesin — CSS hotfix bile /k/* korur
if [[ ! -f k/enes.html || ! -f k/abdulkadir.html || ! -f k/medident.html ]]; then
  echo "  ! /k kartları eksik — landing-kit sync"
  mkdir -p k public
  if [[ -d "$ROOT/landing-kit/k" ]]; then
    cp -R "$ROOT/landing-kit/k/." k/
    [[ -f "$ROOT/landing-kit/public/nefalix-logo-512.png" ]] \
      && cp "$ROOT/landing-kit/public/nefalix-logo-512.png" public/ \
      && cp "$ROOT/landing-kit/public/nefalix-logo-512.png" ./nefalix-logo-512.png
  fi
fi

# shellcheck source=lib/assert-landing-preflight.sh
source "$ROOT/execution/lib/assert-landing-preflight.sh"
assert_landing_preflight "$LANDING" || exit 1

if [[ "$DRY" -eq 1 ]]; then
  echo "dry-run: vercel atlandı"
  exit 0
fi

echo "▶ vercel --prod"
"$NPX" vercel --prod --yes

echo "▶ smoke"
bash "$ROOT/execution/smoke-nefalix-public.sh"
echo "✓ Bitti — https://nefalix.com hard refresh (cache temizle)"
