#!/usr/bin/env bash
# Hasta CRM P0 patch → nefalix-landing pack + Vercel prod (Mac).
# Cloud'da Vercel token yok; Mac'te çalıştır.
#
# Extract zorunlu değil:
#   1) hasta-crm-app/ → landing app overlay
#   2) landing HTML yoksa canlıdan indir
#   3) pack-nefalix-hasta-crm.py
#   4) vercel --prod
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
REPO="${NEFALIX_REPO:-$REPO}"
LANDING="${NEFALIX_LANDING:-$HOME/nefalix-landing}"
EXTRACT="$REPO/.tmp/nefalix-landing-extract"
PATCH="$REPO/hasta-crm-app"
SKIP_VERCEL="${SKIP_VERCEL:-0}"

die() { echo "HATA: $*" >&2; exit 1; }

[[ -d "$PATCH" ]] || die "Patch yok: $PATCH (git pull?)"
[[ -f "$PATCH/store.js" ]] || die "Patch store.js yok: $PATCH/store.js"
[[ -d "$LANDING" ]] || die "Landing yok: $LANDING — NEFALIX_LANDING ayarla"

mkdir -p "$LANDING/nefalix-hasta-crm-app"

# 1) İsteğe bağlı: cloud extract varsa önce onu al (tam app ağacı)
if [[ -f "$EXTRACT/nefalix-hasta-crm.html" && -d "$EXTRACT/nefalix-hasta-crm-app" ]]; then
  echo "→ Extract sync: $EXTRACT → $LANDING"
  rsync -a "$EXTRACT/nefalix-hasta-crm-app/" "$LANDING/nefalix-hasta-crm-app/"
  cp -f "$EXTRACT/nefalix-hasta-crm.html" "$LANDING/nefalix-hasta-crm.html"
else
  echo "→ Extract yok ($EXTRACT) — landing + hasta-crm-app ile devam"
fi

# 2) Landing HTML yoksa canlıdan çek
if [[ ! -f "$LANDING/nefalix-hasta-crm.html" ]]; then
  echo "→ Landing HTML yok — https://nefalix.com/hasta-crm indiriliyor"
  curl -fsSL -o "$LANDING/nefalix-hasta-crm.html" "https://nefalix.com/hasta-crm" \
    || die "Canlı HTML indirilemedi"
fi

# 3) Repo patch overlay (otel/transfer, kasa, not+segment, randevu…)
echo "→ Overlay: $PATCH → $LANDING/nefalix-hasta-crm-app/"
# README hariç DC + store
shopt -s nullglob
for f in "$PATCH"/*.{html,js}; do
  cp -f "$f" "$LANDING/nefalix-hasta-crm-app/"
done
shopt -u nullglob
[[ -f "$LANDING/nefalix-hasta-crm-app/store.js" ]] || die "store.js overlay başarısız"
[[ -f "$LANDING/nefalix-hasta-crm-app/YeniTeklif.dc.html" ]] || die "YeniTeklif overlay başarısız"

# 4) Pack
echo "→ Pack"
NEFALIX_LANDING="$LANDING" python3 "$REPO/execution/pack-nefalix-hasta-crm.py"

# Hızlı doğrulama (otel patch pack'e girdi mi)
if ! python3 - <<PY
import base64, gzip, json, re, sys
from pathlib import Path
html = Path("$LANDING/nefalix-hasta-crm.html").read_text(encoding="utf-8")
man = json.loads(re.search(r'<script type="__bundler/manifest">(.*?)</script>', html, re.S).group(1))
ext = json.loads(re.search(r'<script type="__bundler/ext_resources">(.*?)</script>', html, re.S).group(1))
uid = {e["id"].lstrip("./"): e["uuid"] for e in ext}["YeniTeklif.dc.html"]
raw = base64.b64decode(man[uid]["data"])
if man[uid].get("compressed"):
    raw = gzip.decompress(raw)
text = raw.decode("utf-8", "replace")
ok = "hotel" in text and "transfer" in text
print("YeniTeklif hotel/transfer:", "OK" if ok else "EKSİK")
sys.exit(0 if ok else 1)
PY
then
  die "Pack sonrası YeniTeklif otel/transfer yok — deploy iptal"
fi

# 5) Vercel
if [[ "$SKIP_VERCEL" == "1" ]]; then
  echo "SKIP_VERCEL=1 — pack tamam; vercel atlandı"
  echo "Manuel: cd $LANDING && vercel --prod --yes"
  exit 0
fi

echo "→ Vercel prod: $LANDING"
cd "$LANDING"
vercel --prod --yes

echo
echo "Smoke:"
echo "  1) https://nefalix.com/hasta-crm — Yeni Teklif (otel), Yeni Satış (EUR/yöntem)"
echo "  2) Login sonrası clinic-offers / clinic-payments → 200 (502 ise):"
echo "       bash $REPO/execution/apply-crm-offers-payments-vps.sh"
