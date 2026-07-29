#!/usr/bin/env python3
"""Stella discovery screenshot — staged crawl orchestrator.

Usage:
  python3 execution/stella-screenshot-stage.py           # next pending
  python3 execution/stella-screenshot-stage.py --stage 1
  python3 execution/stella-screenshot-stage.py --complete 1
  python3 execution/stella-screenshot-stage.py --status
"""
from __future__ import annotations

import argparse
import json
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CRM_ROOT = REPO / ".tmp" / "stella-discovery" / "nefalix-crm"
STATE_PATH = REPO / ".tmp" / "stella-crawl-state.json"
OUT_DIR = REPO / "docs" / "stella_crawl"

# Folder match: NFC-normalized substring (macOS may use NFD)
STAGES: list[dict] = [
    {
        "id": "crm_lead",
        "title": "CRM / Lead / Dinamik arama",
        "folder_substrings": ["crm sekmesi"],
        "include_root_png": True,
        "batch_limit": 25,
    },
    {
        "id": "hasta_karti",
        "title": "Hasta kartı sekmeleri",
        "folder_substrings": ["hasta kart"],
        "include_root_png": False,
        "batch_limit": 25,
    },
    {
        "id": "danisan",
        "title": "Danışan sekmesi",
        "folder_substrings": ["danışan", "danisan sekmesi"],
        "folder_exclude": ["hasta kart"],
        "include_root_png": False,
        "batch_limit": 25,
    },
    {
        "id": "randevu",
        "title": "Randevu",
        "folder_substrings": ["randevu"],
        "include_root_png": False,
        "batch_limit": 25,
    },
    {
        "id": "gelirler",
        "title": "Gelirler / Kasa",
        "folder_substrings": ["gelir"],
        "include_root_png": False,
        "batch_limit": 25,
    },
    {
        "id": "ana_ekran",
        "title": "Ana ekran / ev",
        "folder_substrings": ["ana ekran", "ev i"],
        "include_root_png": False,
        "batch_limit": 25,
    },
    {
        "id": "giderler",
        "title": "Giderler",
        "folder_substrings": ["gider"],
        "include_root_png": False,
        "batch_limit": 25,
    },
    {
        "id": "whatsapp",
        "title": "WhatsApp (Stella)",
        "folder_substrings": ["whatsapp"],
        "include_root_png": False,
        "batch_limit": 25,
    },
    {
        "id": "rapor_a",
        "title": "Rapor (1/2)",
        "folder_substrings": ["rapor"],
        "slice": [0, 43],
        "include_root_png": False,
        "batch_limit": 25,
    },
    {
        "id": "rapor_b",
        "title": "Rapor (2/2)",
        "folder_substrings": ["rapor"],
        "slice": [43, None],
        "include_root_png": False,
        "batch_limit": 25,
    },
    {
        "id": "sistem_a",
        "title": "Sistem (1/3)",
        "folder_substrings": ["sistem"],
        "slice": [0, 40],
        "include_root_png": False,
        "batch_limit": 25,
    },
    {
        "id": "sistem_b",
        "title": "Sistem (2/3)",
        "folder_substrings": ["sistem"],
        "slice": [40, 80],
        "include_root_png": False,
        "batch_limit": 25,
    },
    {
        "id": "sistem_c",
        "title": "Sistem (3/3) + Destek",
        "folder_substrings": ["sistem", "destek"],
        "sistem_slice_from": 80,
        "include_root_png": False,
        "batch_limit": 30,
    },
]


def norm(s: str) -> str:
    return unicodedata.normalize("NFC", s).casefold()


def default_state() -> dict:
    stages = []
    for i, spec in enumerate(STAGES, start=1):
        stages.append(
            {
                "stage": i,
                "id": spec["id"],
                "title": spec["title"],
                "status": "pending",
                "completed_at": None,
                "doc": f"docs/stella_crawl/stage-{i:02d}-{spec['id']}.md",
                "png_count": None,
                "read_count": None,
                "notes": "",
            }
        )
    return {
        "version": 1,
        "updated_at": None,
        "crm_root": str(CRM_ROOT),
        "stages": stages,
        "next_action": "Run: python3 execution/stella-screenshot-stage.py",
    }


def load_state() -> dict:
    if STATE_PATH.is_file():
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    st = default_state()
    save_state(st)
    return st


def save_state(st: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    st["updated_at"] = datetime.now(timezone.utc).isoformat()
    STATE_PATH.write_text(json.dumps(st, ensure_ascii=False, indent=2), encoding="utf-8")


def list_dirs() -> list[Path]:
    if not CRM_ROOT.is_dir():
        raise SystemExit(f"CRM root yok: {CRM_ROOT} — önce discovery unzip")
    return [p for p in CRM_ROOT.iterdir() if p.is_dir()]


def match_folders(substrings: list[str], exclude: list[str] | None = None) -> list[Path]:
    exclude = exclude or []
    out = []
    for d in list_dirs():
        n = norm(d.name)
        if any(norm(ex) in n for ex in exclude):
            continue
        if any(norm(s) in n for s in substrings):
            out.append(d)
    return sorted(out, key=lambda p: norm(p.name))


def collect_pngs(spec: dict) -> list[Path]:
    files: list[Path] = []
    if spec.get("include_root_png"):
        files.extend(sorted(CRM_ROOT.glob("*.png")))

    folders = match_folders(spec["folder_substrings"], spec.get("folder_exclude"))
    # sistem_c: sistem from offset + all destek
    if spec["id"] == "sistem_c":
        sistem = match_folders(["sistem"])
        destek = match_folders(["destek"])
        sistem_pngs: list[Path] = []
        for d in sistem:
            sistem_pngs.extend(sorted(d.rglob("*.png")))
        sistem_pngs = sistem_pngs[spec.get("sistem_slice_from", 80) :]
        files.extend(sistem_pngs)
        for d in destek:
            files.extend(sorted(d.rglob("*.png")))
        return files

    for d in folders:
        files.extend(sorted(d.rglob("*.png")))

    sl = spec.get("slice")
    if sl:
        start, end = sl[0], sl[1]
        files = files[start:end]

    return files


def emit_stage_packet(stage_num: int) -> dict:
    spec = STAGES[stage_num - 1]
    pngs = collect_pngs(spec)
    limit = int(spec.get("batch_limit") or 25)
    # Prefer evenly spaced sample if over limit
    if len(pngs) > limit:
        step = len(pngs) / limit
        sample = [pngs[int(i * step)] for i in range(limit)]
    else:
        sample = pngs

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    doc = OUT_DIR / f"stage-{stage_num:02d}-{spec['id']}.md"
    if not doc.exists():
        doc.write_text(
            f"# Stage {stage_num:02d} — {spec['title']}\n\n"
            f"**Status:** in_progress  \n"
            f"**PNG total:** {len(pngs)}  \n"
            f"**Sample to read:** {len(sample)}  \n\n"
            f"## Dosya listesi (örnek)\n\n"
            + "\n".join(f"- `{p.relative_to(CRM_ROOT)}`" for p in sample)
            + "\n\n## Bulgular\n\n_(agent dolduracak)_\n\n"
            "## Canlı doğrulama (Stella UI)\n\n_(tıkla → ne oldu)_\n\n"
            "## Gap delta (Stella_Gap_Action_Map)\n\n- \n",
            encoding="utf-8",
        )

    st = load_state()
    for row in st["stages"]:
        if row["stage"] == stage_num and row["status"] == "pending":
            row["status"] = "in_progress"
            row["png_count"] = len(pngs)
            row["read_count"] = len(sample)
    st["next_action"] = (
        f"Read {len(sample)} PNGs for stage {stage_num} ({spec['id']}), "
        f"fill {doc.relative_to(REPO)}, then: "
        f"python3 execution/stella-screenshot-stage.py --complete {stage_num}"
    )
    save_state(st)

    packet = {
        "stage": stage_num,
        "id": spec["id"],
        "title": spec["title"],
        "png_total": len(pngs),
        "sample_count": len(sample),
        "doc": str(doc.relative_to(REPO)),
        "folders": [str(p.relative_to(CRM_ROOT)) for p in match_folders(spec["folder_substrings"], spec.get("folder_exclude"))],
        "sample_paths": [str(p) for p in sample],
        "state": str(STATE_PATH.relative_to(REPO)),
    }
    print(json.dumps(packet, ensure_ascii=False, indent=2))
    return packet


def complete_stage(stage_num: int, notes: str = "") -> None:
    st = load_state()
    for row in st["stages"]:
        if row["stage"] == stage_num:
            row["status"] = "done"
            row["completed_at"] = datetime.now(timezone.utc).isoformat()
            if notes:
                row["notes"] = notes
            doc = REPO / row["doc"]
            if doc.is_file():
                text = doc.read_text(encoding="utf-8")
                text = text.replace("**Status:** in_progress", "**Status:** done", 1)
                doc.write_text(text, encoding="utf-8")
    pending = [r for r in st["stages"] if r["status"] != "done"]
    if pending:
        n = pending[0]["stage"]
        st["next_action"] = f"python3 execution/stella-screenshot-stage.py --stage {n}"
    else:
        st["next_action"] = "ALL STAGES DONE — merge docs/stella_crawl/* into Stella_Gap_Action_Map.md"
    save_state(st)
    print(json.dumps({"completed": stage_num, "next_action": st["next_action"]}, ensure_ascii=False, indent=2))


def print_status() -> None:
    st = load_state()
    rows = []
    for r in st["stages"]:
        rows.append(f"{r['stage']:02d} {r['status']:12} {r['id']:12} png={r.get('png_count')} → {r['doc']}")
    print("\n".join(rows))
    print("next:", st.get("next_action"))


def next_pending() -> int | None:
    st = load_state()
    for r in st["stages"]:
        if r["status"] in ("pending", "in_progress"):
            return int(r["stage"])
    return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", type=int)
    ap.add_argument("--complete", type=int)
    ap.add_argument("--notes", default="")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--init", action="store_true")
    args = ap.parse_args()

    if args.init or not STATE_PATH.exists():
        save_state(default_state())
        print(f"initialized {STATE_PATH}")

    if args.status:
        print_status()
        return
    if args.complete:
        complete_stage(args.complete, args.notes)
        return

    stage = args.stage or next_pending()
    if stage is None:
        print(json.dumps({"ok": True, "message": "all stages done"}, ensure_ascii=False))
        return
    emit_stage_packet(stage)


if __name__ == "__main__":
    main()
