#!/usr/bin/env python3
"""Emit Task prompt for the next pending Stella screenshot crawl stage.

Usage:
  python3 execution/emit-stella-worker-brief.py
  python3 execution/emit-stella-worker-brief.py --json   # machine-readable
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
STATE = REPO / ".tmp" / "stella-crawl-state.json"
LOCK = REPO / ".tmp" / "stella-crawl-orchestrator.lock"


def load_state() -> dict:
    if not STATE.is_file():
        raise SystemExit(f"State yok: {STATE} — önce stella-screenshot-stage.py --init")
    return json.loads(STATE.read_text(encoding="utf-8"))


def next_stage(st: dict) -> dict | None:
    for row in st.get("stages") or []:
        if row.get("status") in ("pending", "in_progress"):
            return row
    return None


def ensure_packet(stage_num: int) -> dict:
    proc = subprocess.run(
        [sys.executable, str(REPO / "execution" / "stella-screenshot-stage.py"), "--stage", str(stage_num)],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise SystemExit(proc.stderr or proc.stdout or "stage packet failed")
    # last JSON object in stdout
    text = proc.stdout.strip()
    raw = text[text.rfind("{") :]
    return json.loads(raw)


def build_prompt(packet: dict, row: dict) -> str:
    paths = packet.get("sample_paths") or []
    path_block = "\n".join(f"- `{p}`" for p in paths[:30])
    return f"""You are a WORKER subagent (not coordinator). Do ONLY Stella screenshot crawl stage {packet['stage']} ({packet['id']}).

## Hard rules
- Read the listed PNG samples with the Read tool (vision). Be honest about how many you read.
- Write findings into `{packet['doc']}` (Bulgular + Canlı doğrulama + Gap delta).
- Then run: `python3 execution/stella-screenshot-stage.py --complete {packet['stage']}`
- Update `docs/Stella_Gap_Action_Map.md` with a short stage line if needed.
- Do NOT start stage {packet['stage'] + 1}. Do NOT re-upload the discovery zip. Do NOT commit secrets.
- Repo root: n8n-repo. Assets: `.tmp/stella-discovery/nefalix-crm/`. SOP: `directives/stella_screenshot_crawl.md`.

## Stage
- title: {packet['title']}
- png_total: {packet['png_total']}
- sample_count: {packet['sample_count']}
- doc: {packet['doc']}

## Sample paths
{path_block}

## Done definition
`{packet['doc']}` filled + stage status done in `.tmp/stella-crawl-state.json` + short summary to parent (URLs found, P0 gaps).
"""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-packet", action="store_true", help="use state only, do not re-emit packet")
    args = ap.parse_args()

    st = load_state()
    row = next_stage(st)
    if not row:
        out = {"ok": True, "done": True, "message": "ALL STAGES DONE", "lock": LOCK.exists()}
        print(json.dumps(out, ensure_ascii=False, indent=2) if args.json else out["message"])
        return

    stage_num = int(row["stage"])
    packet = {"stage": stage_num, "id": row["id"], "title": row["title"], "doc": row["doc"],
              "png_total": row.get("png_count"), "sample_count": row.get("read_count"), "sample_paths": []}
    if not args.no_packet:
        packet = ensure_packet(stage_num)

    prompt = build_prompt(packet, row)
    payload = {
        "ok": True,
        "done": False,
        "orchestrator_lock": LOCK.exists(),
        "stage": stage_num,
        "id": packet["id"],
        "title": packet["title"],
        "doc": packet["doc"],
        "task_description": f"Stella crawl stage {stage_num:02d} {packet['id']}",
        "prompt": prompt,
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(prompt)


if __name__ == "__main__":
    main()
