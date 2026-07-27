#!/usr/bin/env python3
"""Unpack nefalix-landing/nefalix-crm.html → nefalix-crm-app/"""
from __future__ import annotations

import base64
import gzip
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LANDING = Path("/Users/enesceylan/nefalix-landing")
SRC = LANDING / "nefalix-crm.html"
OUT = LANDING / "nefalix-crm-app"


def main() -> None:
    text = SRC.read_text(encoding="utf-8")
    man = json.loads(re.search(r'<script type="__bundler/manifest">(.*?)</script>', text, re.S).group(1))
    tmpl = json.loads(re.search(r'<script type="__bundler/template">(.*?)</script>', text, re.S).group(1))
    ext = json.loads(re.search(r'<script type="__bundler/ext_resources">(.*?)</script>', text, re.S).group(1))
    uuid_to_path = {e["uuid"]: e["id"].lstrip("./") for e in ext}

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    for uid, meta in man.items():
        raw = base64.b64decode(meta["data"])
        try:
            body = gzip.decompress(raw)
        except Exception:
            body = raw
        rel = uuid_to_path.get(uid)
        mime = meta.get("mime", "")
        if not rel:
            extn = ".js" if "javascript" in mime else (".html" if "html" in mime else ".bin")
            rel = f"_assets/{uid}{extn}"
        if rel.startswith("http"):
            continue
        dest = OUT / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if any(x in mime for x in ("javascript", "html", "css", "json", "svg")):
            dest.write_text(body.decode("utf-8"), encoding="utf-8")
        else:
            dest.write_bytes(body)

    store_src = OUT / "_assets" / "2152ddf7-a6e4-4fca-ac2c-a20b92b711dd.js"
    if store_src.exists():
        (OUT / "store.js").write_text(store_src.read_text(encoding="utf-8"), encoding="utf-8")
    if isinstance(tmpl, str):
        (OUT / "index.html").write_text(tmpl, encoding="utf-8")
    print(f"OK → {OUT} ({sum(1 for _ in OUT.rglob('*') if _.is_file())} files)")


if __name__ == "__main__":
    main()
