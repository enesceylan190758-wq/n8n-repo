#!/usr/bin/env bash
# subagentStop → if orchestrator lock + pending Stella crawl stage, ask parent to spawn next worker.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
LOCK="$ROOT/.tmp/stella-crawl-orchestrator.lock"
STATE="$ROOT/.tmp/stella-crawl-state.json"

# Consume stdin (hook payload) — keep for future filtering
cat >/dev/null

if [[ ! -f "$LOCK" ]]; then
  echo '{}'
  exit 0
fi

if [[ ! -f "$STATE" ]]; then
  echo '{}'
  exit 0
fi

OUT="$(python3 "$ROOT/execution/emit-stella-worker-brief.py" --json --no-packet 2>/dev/null || true)"
if [[ -z "$OUT" ]]; then
  echo '{}'
  exit 0
fi

DONE="$(python3 -c 'import json,sys; d=json.loads(sys.argv[1]); print("1" if d.get("done") else "0")' "$OUT")"
if [[ "$DONE" == "1" ]]; then
  rm -f "$LOCK"
  python3 -c 'import json; print(json.dumps({"followup_message":"Stella crawl: tüm aşamalar bitti. Lock kaldırıldı. docs/stella_crawl/ + Stella_Gap_Action_Map.md birleştirme özeti ver."}))'
  exit 0
fi

STAGE="$(python3 -c 'import json,sys; d=json.loads(sys.argv[1]); print(d.get("stage",""))' "$OUT")"
SID="$(python3 -c 'import json,sys; d=json.loads(sys.argv[1]); print(d.get("id",""))' "$OUT")"

MSG="Stella crawl orchestrator: sıradaki işçi stage ${STAGE} (${SID}). Şimdi çalıştır: python3 execution/emit-stella-worker-brief.py — çıkan prompt ile Task(generalPurpose, background) başlat. Lock duruyor; kullanıcı 'dur' derse rm .tmp/stella-crawl-orchestrator.lock"

python3 -c 'import json,sys; print(json.dumps({"followup_message": sys.argv[1]}))' "$MSG"
exit 0
