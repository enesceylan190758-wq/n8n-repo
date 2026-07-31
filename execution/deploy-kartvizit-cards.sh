#!/usr/bin/env bash
# Kartvizit QR (/k/enes, /k/abdulkadir) → private landing'e sync + Vercel prod.
# Kaynak: bu repodaki landing-kit/k/*  (CANLI SITE DEĞİL — directives/vercel_prod_safety.md)
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

SRC="$ROOT/landing-kit"
FRAG="$SRC/vercel.fragments.json"
LANDING="${NEFALIX_LANDING_DIR:-$HOME/nefalix-landing}"
DRY=0
[[ "${1:-}" == "--dry-run" ]] && DRY=1

if [[ ! -d "$LANDING" ]]; then
  echo "HATA: private landing bulunamadı: $LANDING" >&2
  echo "  export NEFALIX_LANDING_DIR=/Users/enesceylan/nefalix-landing" >&2
  echo "  Bu cloud ortamında yok — Mac'te çalıştır. ASLA landing-kit'ten vercel --prod yapma." >&2
  exit 1
fi

# Güvenlik: yanlışlıkla kit dizininden prod basılmasın
if [[ "$(cd "$LANDING" && pwd)" == "$SRC" ]] || [[ "$LANDING" == *"/landing-kit" ]]; then
  echo "HATA: LANDING=landing-kit olamaz — bu patch kit, canlı site değil." >&2
  echo "  directives/vercel_prod_safety.md" >&2
  exit 1
fi

if [[ ! -f "$SRC/k/enes.html" || ! -f "$SRC/k/abdulkadir.html" || ! -f "$SRC/k/medident.html" ]]; then
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
copy_file "$SRC/k/medident.html" "$LANDING/k/medident.html"
copy_file "$SRC/k/card.css" "$LANDING/k/card.css"
copy_file "$SRC/k/enes.vcf" "$LANDING/k/enes.vcf"
copy_file "$SRC/k/abdulkadir.vcf" "$LANDING/k/abdulkadir.vcf"
copy_file "$SRC/k/medident.vcf" "$LANDING/k/medident.vcf"

if [[ -f "$SRC/public/nefalix-logo-512.png" ]]; then
  copy_file "$SRC/public/nefalix-logo-512.png" "$LANDING/public/nefalix-logo-512.png"
  copy_file "$SRC/public/nefalix-logo-512.png" "$LANDING/nefalix-logo-512.png"
fi
if [[ -f "$SRC/public/favicon-192.png" ]]; then
  copy_file "$SRC/public/favicon-192.png" "$LANDING/public/favicon-192.png"
  copy_file "$SRC/public/favicon-192.png" "$LANDING/favicon-192.png"
fi

# Private landing vercel.json'a fragment merge (+ git deploy KAPALI)
merge_vercel_json() {
  local vf="$LANDING/vercel.json"
  if [[ ! -f "$FRAG" ]]; then
    echo "HATA: $FRAG yok" >&2
    exit 1
  fi
  if [[ ! -f "$vf" ]]; then
    # Minimal güvenli iskelet — tam site redirect'leri Mac landing'de olmalı
    python3 - "$vf" "$FRAG" <<'PY'
import json, sys
out, frag_path = sys.argv[1], sys.argv[2]
with open(frag_path, encoding="utf-8") as f:
    data = json.load(f)
data["git"] = {"deploymentEnabled": False}
with open(out, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
    f.write("\n")
print("  ✓ vercel.json (yeni iskelet + fragments)")
PY
    return
  fi
  python3 - "$vf" "$FRAG" <<'PY'
import json, sys
path, frag_path = sys.argv[1], sys.argv[2]
with open(path, encoding="utf-8") as f:
    data = json.load(f)
with open(frag_path, encoding="utf-8") as f:
    frag = json.load(f)

data["git"] = {"deploymentEnabled": False}

def ensure(key, items):
    cur = data.get(key) or []
    sources = {x.get("source") for x in cur}
    for item in items:
        if item.get("source") not in sources:
            cur.append(item)
    data[key] = cur

ensure("rewrites", frag.get("rewrites") or [])
ensure("headers", frag.get("headers") or [])

with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
    f.write("\n")
print("  ✓ vercel.json (fragments + git.deploymentEnabled=false)")
PY
}

merge_vercel_json

# shellcheck source=lib/assert-landing-preflight.sh
source "$ROOT/execution/lib/assert-landing-preflight.sh"
assert_landing_preflight "$LANDING" || exit 1

if [[ "$DRY" -eq 1 ]]; then
  echo "dry-run: vercel atlandı"
  exit 0
fi

cd "$LANDING"
echo "▶ vercel --prod  (CLI — GitHub değil)"
"$NPX" vercel --prod --yes

echo "▶ smoke"
bash "$ROOT/execution/smoke-nefalix-public.sh"
echo "✓ Kartvizit QR canlı — https://nefalix.com/k/enes"
