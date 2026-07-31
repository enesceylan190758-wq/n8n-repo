#!/usr/bin/env bash
# Ofis dışı acil kurtarma: Vercel'deki son sağlam production deploy'u promote et,
# MediDent kartını ekle, CLI ile prod bas, smoke et.
#
# Gereksinim: `npx vercel login` (veya VERCEL_TOKEN)
#
# Kullanım:
#   bash execution/restore-nefalix-prod-from-vercel.sh
#   bash execution/restore-nefalix-prod-from-vercel.sh --promote-only dpl_XXXX
#   bash execution/restore-nefalix-prod-from-vercel.sh --dry-run
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=lib/resolve-npx.sh
source "$ROOT/execution/lib/resolve-npx.sh"
NPX="$(resolve_npx)" || exit 1

PROJECT="nefalix-landing"
WORK="$ROOT/.tmp/nefalix-landing-restored"
DRY=0
PROMOTE_ONLY=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY=1; shift ;;
    --promote-only) PROMOTE_ONLY="${2:?}"; shift 2 ;;
    *) echo "Bilinmeyen arg: $1" >&2; exit 2 ;;
  esac
done

if ! "$NPX" vercel whoami >/dev/null 2>&1; then
  echo "HATA: Vercel oturumu yok. Önce: npx vercel login" >&2
  echo "  (veya export VERCEL_TOKEN=...)" >&2
  exit 1
fi

AUTH_JSON="${HOME}/.local/share/com.vercel.cli/auth.json"
if [[ ! -f "$AUTH_JSON" && -z "${VERCEL_TOKEN:-}" ]]; then
  echo "HATA: auth.json / VERCEL_TOKEN yok" >&2
  exit 1
fi

TOKEN="${VERCEL_TOKEN:-}"
if [[ -z "$TOKEN" ]]; then
  TOKEN="$(python3 -c "import json; print(json.load(open('$AUTH_JSON'))['token'])")"
fi

api() {
  local method="$1" url="$2"
  shift 2
  curl -sS -X "$method" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" "$@" "$url"
}

echo "▶ Git auto-build kilidi (Ignored Build Step = exit 0)"
api PATCH "https://api.vercel.com/v9/projects/$PROJECT" \
  -d '{"commandForIgnoringBuildStep":"exit 0"}' >/dev/null || true

if [[ -n "$PROMOTE_ONLY" ]]; then
  echo "▶ promote $PROMOTE_ONLY"
  [[ "$DRY" -eq 1 ]] && exit 0
  "$NPX" vercel promote "$PROMOTE_ONLY" --yes
  bash "$ROOT/execution/smoke-nefalix-public.sh"
  exit 0
fi

# En son ≥200 dosyalı READY production deploy (eksik kit'ler genelde file list 404 / küçük)
echo "▶ sağlam production deploy aranıyor"
GOOD="$(python3 - "$TOKEN" "$PROJECT" <<'PY'
import json, sys, urllib.request
token, project = sys.argv[1], sys.argv[2]

def get(url):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)

proj = get(f"https://api.vercel.com/v9/projects/{project}")
pid = proj["id"]
deps = get(f"https://api.vercel.com/v6/deployments?projectId={pid}&target=production&limit=30")
for d in deps.get("deployments") or []:
    if d.get("state") != "READY" and d.get("readyState") != "READY":
        continue
    uid = d.get("uid") or d.get("id")
    try:
        files = get(f"https://api.vercel.com/v6/deployments/{uid}/files")
    except Exception:
        continue
    def walk(node, n=0):
        if node.get("type") == "file":
            return 1
        return sum(walk(c) for c in (node.get("children") or []))
    total = 0
    if isinstance(files, list):
        total = sum(walk(x) for x in files)
    elif isinstance(files, dict):
        total = walk(files)
    # Tam site ~230+; boş kit çok az veya 404
    if total >= 200:
        print(uid)
        print(f"files={total} url={d.get('url')}", file=sys.stderr)
        sys.exit(0)
print("NONE", file=sys.stderr)
sys.exit(1)
PY
)" || {
  echo "HATA: ≥200 dosyalı production deploy bulunamadı — Mac ~/nefalix-landing gerekir." >&2
  exit 1
}

echo "▶ promote $GOOD"
if [[ "$DRY" -eq 1 ]]; then
  echo "dry-run: promote + patch atlandı"
  exit 0
fi
"$NPX" vercel promote "$GOOD" --yes

echo "▶ deploy dosyaları indiriliyor → $WORK"
rm -rf "$WORK"
mkdir -p "$WORK"
python3 - "$TOKEN" "$GOOD" "$WORK" <<'PY'
import json, sys, urllib.request, base64, pathlib
token, uid, out = sys.argv[1], sys.argv[2], pathlib.Path(sys.argv[3])

def get_json(url):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)

def get_bytes(url):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()

files = get_json(f"https://api.vercel.com/v6/deployments/{uid}/files")
pairs = []

def walk(node, path=""):
    name = node.get("name", "")
    p = f"{path}/{name}".replace("//", "/")
    typ = node.get("type")
    if typ == "file":
        pairs.append((p, node["uid"]))
    for c in node.get("children") or []:
        walk(c, p if typ == "directory" else path)

for n in files if isinstance(files, list) else [files]:
    walk(n)

for path, fid in pairs:
    rel = path
    if rel.startswith("/src/"):
        rel = rel[len("/src/"):]
    elif rel.startswith("src/"):
        rel = rel[len("src/"):]
    rel = rel.lstrip("/")
    dest = out / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    raw = get_bytes(f"https://api.vercel.com/v7/deployments/{uid}/files/{fid}")
    try:
        data = json.loads(raw)
        content = base64.b64decode(data["data"]) if isinstance(data, dict) and "data" in data else raw
    except Exception:
        content = raw
    dest.write_bytes(content)
print(f"downloaded {len(pairs)}")
PY

echo "▶ MediDent + kart asset sync"
mkdir -p "$WORK/k" "$WORK/public"
cp "$ROOT/landing-kit/k/medident.html" "$WORK/k/medident.html"
cp "$ROOT/landing-kit/k/medident.vcf" "$WORK/k/medident.vcf"
cp "$ROOT/landing-kit/k/card.css" "$WORK/k/card.css"
cp "$ROOT/landing-kit/k/enes.vcf" "$WORK/k/enes.vcf"
cp "$ROOT/landing-kit/k/abdulkadir.vcf" "$WORK/k/abdulkadir.vcf"
if [[ -f "$WORK/assets/brand/nefalix-logo-512.png" ]]; then
  cp "$WORK/assets/brand/nefalix-logo-512.png" "$WORK/nefalix-logo-512.png"
  cp "$WORK/assets/brand/nefalix-logo-512.png" "$WORK/public/nefalix-logo-512.png"
fi
if [[ -f "$WORK/assets/brand/favicon-192.png" ]]; then
  cp "$WORK/assets/brand/favicon-192.png" "$WORK/favicon-192.png"
  cp "$WORK/assets/brand/favicon-192.png" "$WORK/public/favicon-192.png"
fi

python3 - "$WORK/vercel.json" <<'PY'
import json, sys
from pathlib import Path
p = Path(sys.argv[1])
data = json.loads(p.read_text())
data["git"] = {"deploymentEnabled": False}
rewrites = data.get("rewrites") or []
wanted = {
    "/k/medident": "/k/medident.html",
    "/k/enes": "/k/enes-ceylan.html",
    "/k/abdulkadir": "/k/abdulkadir-yasar.html",
}
by = {r.get("source"): r for r in rewrites}
for src, dst in wanted.items():
    if src in by:
        by[src]["destination"] = dst
    else:
        rewrites.insert(0, {"source": src, "destination": dst})
data["rewrites"] = rewrites
headers = data.get("headers") or []
if not any(h.get("source") == "/k/(.*).vcf" for h in headers):
    headers.append({
        "source": "/k/(.*).vcf",
        "headers": [
            {"key": "Content-Type", "value": "text/vcard; charset=utf-8"},
            {"key": "Content-Disposition", "value": "attachment"},
        ],
    })
data["headers"] = headers
p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
print("vercel.json patched")
PY

# shellcheck source=lib/assert-landing-preflight.sh
source "$ROOT/execution/lib/assert-landing-preflight.sh"
# Preflight bekler: k/enes.html — restored'da enes-ceylan.html var; kısa alias kopyala
[[ -f "$WORK/k/enes.html" ]] || cp "$WORK/k/enes-ceylan.html" "$WORK/k/enes.html"
[[ -f "$WORK/k/abdulkadir.html" ]] || cp "$WORK/k/abdulkadir-yasar.html" "$WORK/k/abdulkadir.html"
assert_landing_preflight "$WORK" || exit 1

# Project link
mkdir -p "$WORK/.vercel"
python3 - "$TOKEN" "$WORK/.vercel/project.json" <<'PY'
import json, sys, urllib.request
token, out = sys.argv[1], sys.argv[2]
req = urllib.request.Request(
    "https://api.vercel.com/v9/projects/nefalix-landing",
    headers={"Authorization": f"Bearer {token}"},
)
with urllib.request.urlopen(req) as r:
    proj = json.load(r)
open(out, "w").write(json.dumps({
    "projectId": proj["id"],
    "orgId": proj["accountId"],
    "projectName": "nefalix-landing",
}, indent=2) + "\n")
PY

echo "▶ vercel --prod"
cd "$WORK"
"$NPX" vercel --prod --yes --archive=tgz

bash "$ROOT/execution/smoke-nefalix-public.sh"
echo "✓ nefalix.com restore OK — /k/enes /k/abdulkadir /k/medident"
echo "  Kalıcı: Vercel Git Disconnect veya Ignored Build Step=exit 0 (bu script ayarladı)"
