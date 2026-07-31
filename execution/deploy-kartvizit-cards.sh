#!/usr/bin/env bash
# Kartvizit QR (/k/enes, /k/abdulkadir) → private landing'e sync + Vercel prod.
# Kaynak: bu repodaki nefalix-landing/k/*
# Hedef: ~/nefalix-landing (cloud'da yok — Mac'te çalıştır)
#
# Kullanım:
#   bash execution/deploy-kartvizit-cards.sh
#   bash execution/deploy-kartvizit-cards.sh --dry-run
#   NEFALIX_LANDING_DIR=/path/to/nefalix-landing bash execution/deploy-kartvizit-cards.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=lib/resolve-npx.sh
source "$ROOT/execution/lib/resolve-npx.sh"
NPX="$(resolve_npx)" || exit 1

SRC="$ROOT/nefalix-landing"
LANDING="${NEFALIX_LANDING_DIR:-$HOME/nefalix-landing}"
DRY=0
[[ "${1:-}" == "--dry-run" ]] && DRY=1

if [[ ! -d "$LANDING" ]]; then
  echo "HATA: nefalix-landing bulunamadı: $LANDING" >&2
  echo "  export NEFALIX_LANDING_DIR=/Users/enesceylan/nefalix-landing" >&2
  echo "  Bu cloud ortamında private landing yok — Mac'te çalıştır." >&2
  exit 1
fi

if [[ ! -f "$SRC/k/enes.html" || ! -f "$SRC/k/abdulkadir.html" ]]; then
  echo "HATA: kaynak kartlar yok: $SRC/k/" >&2
  exit 1
fi

echo "→ kaynak:  $SRC/k"
echo "→ landing: $LANDING"

mkdir -p "$LANDING/k" "$LANDING/public"

copy_file() {
  local from="$1" to="$2"
  cp "$from" "$to"
  echo "  ✓ $(basename "$to")"
}

copy_file "$SRC/k/enes.html" "$LANDING/k/enes.html"
copy_file "$SRC/k/abdulkadir.html" "$LANDING/k/abdulkadir.html"
copy_file "$SRC/k/card.css" "$LANDING/k/card.css"
copy_file "$SRC/k/enes.vcf" "$LANDING/k/enes.vcf"
copy_file "$SRC/k/abdulkadir.vcf" "$LANDING/k/abdulkadir.vcf"

if [[ -f "$SRC/public/nefalix-logo-512.png" ]]; then
  copy_file "$SRC/public/nefalix-logo-512.png" "$LANDING/public/nefalix-logo-512.png"
  # bazı deploy'larda public/ kök değil; kök kopya da koy
  copy_file "$SRC/public/nefalix-logo-512.png" "$LANDING/nefalix-logo-512.png"
fi
if [[ -f "$SRC/public/favicon-192.png" ]]; then
  copy_file "$SRC/public/favicon-192.png" "$LANDING/public/favicon-192.png"
  copy_file "$SRC/public/favicon-192.png" "$LANDING/favicon-192.png"
fi

# vercel.json: /k rewrite yoksa ekle (jq yoksa python)
merge_vercel_rewrites() {
  local vf="$LANDING/vercel.json"
  if [[ ! -f "$vf" ]]; then
    cp "$SRC/vercel.json" "$vf"
    echo "  ✓ vercel.json (yeni)"
    return
  fi
  python3 - "$vf" "$SRC/vercel.json" <<'PY'
import json, sys
path, src_path = sys.argv[1], sys.argv[2]
with open(path, encoding="utf-8") as f:
    data = json.load(f)
with open(src_path, encoding="utf-8") as f:
    src = json.load(f)

def ensure(key, items):
    cur = data.get(key) or []
    existing = {json.dumps(x, sort_keys=True) for x in cur}
    for item in items:
        # rewrite match by source
        if key == "rewrites":
            sources = {x.get("source") for x in cur}
            if item.get("source") in sources:
                continue
        elif key == "headers":
            sources = {x.get("source") for x in cur}
            if item.get("source") in sources:
                continue
        cur.append(item)
    data[key] = cur

ensure("rewrites", src.get("rewrites") or [])
ensure("headers", src.get("headers") or [])
# host redirects only if missing entirely
if not data.get("redirects") and src.get("redirects"):
    data["redirects"] = src["redirects"]

with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
    f.write("\n")
print("  ✓ vercel.json (k rewrite merge)")
PY
}

merge_vercel_rewrites

# shellcheck source=lib/assert-landing-preflight.sh
source "$ROOT/execution/lib/assert-landing-preflight.sh"
assert_landing_preflight "$LANDING" || exit 1

if [[ "$DRY" -eq 1 ]]; then
  echo "dry-run: vercel atlandı"
  exit 0
fi

cd "$LANDING"
echo "▶ vercel --prod"
"$NPX" vercel --prod --yes

echo "▶ smoke"
bash "$ROOT/execution/smoke-nefalix-public.sh"
echo "✓ Kartvizit QR canlı — https://nefalix.com/k/enes"
