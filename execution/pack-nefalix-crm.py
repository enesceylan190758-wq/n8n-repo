#!/usr/bin/env python3
"""Pack nefalix-crm-app changes back into nefalix-crm.html (gzip+base64 manifest)."""
from __future__ import annotations

import base64
import gzip
import json
import re
from pathlib import Path

LANDING = Path("/Users/enesceylan/nefalix-landing")
HTML = LANDING / "nefalix-crm.html"
APP = LANDING / "nefalix-crm-app"

# Files we edit → uuid in original bundle
PATCH_MAP = {
    "store.js": "2152ddf7-a6e4-4fca-ac2c-a20b92b711dd",
    "WhatsappPanel.dc.html": "ee0b494d-8d3f-4c8a-9f2e-0b1c2d3e4f5a",  # placeholder — filled below
}


def load_uuid_map(html: str) -> dict[str, str]:
    ext = json.loads(re.search(r'<script type="__bundler/ext_resources">(.*?)</script>', html, re.S).group(1))
    out = {e["id"].lstrip("./"): e["uuid"] for e in ext}
    out["store.js"] = "2152ddf7-a6e4-4fca-ac2c-a20b92b711dd"
    return out


def main() -> None:
    html = HTML.read_text(encoding="utf-8")
    man = json.loads(re.search(r'<script type="__bundler/manifest">(.*?)</script>', html, re.S).group(1))
    uuid_map = load_uuid_map(html)

    files = [
        "store.js",
        "WhatsappPanel.dc.html",
        "YeniRandevu.dc.html",
        "RandevuTakvim.dc.html",
        "Login.dc.html",
        "KurumKarti.dc.html",
        "NavHeader.dc.html",
        "index.html",
    ]
    updated = []
    for name in files:
        path = APP / name
        if not path.exists():
            print("skip missing", name)
            continue
        if name == "index.html":
            # Ana shell __bundler/template içinde (ayrı uuid yok).
            # HTML <script> içinde </script> kırılmasın diye slash'i escape et.
            raw = path.read_text(encoding="utf-8")
            dumped = json.dumps(raw, ensure_ascii=False)
            dumped = dumped.replace("</", "<\\u002F")
            new_tpl = "\n" + dumped
            html2, n = re.subn(
                r'(<script type="__bundler/template">)(.*?)(</script>)',
                lambda m: m.group(1) + new_tpl + m.group(3),
                html,
                count=1,
                flags=re.S,
            )
            if n != 1:
                raise SystemExit("template (index) replace failed")
            html = html2
            updated.append(f"index.html → __bundler/template ({len(raw)} bytes)")
            continue
        uid = uuid_map.get(name)
        if not uid or uid not in man:
            print("skip no uuid", name, uid)
            continue
        raw = path.read_bytes()
        # store.js lives as both store.js and asset copy — sync asset too
        if name == "store.js":
            asset = APP / "_assets" / f"{uid}.js"
            asset.write_bytes(raw)
        compressed = gzip.compress(raw, compresslevel=9)
        b64 = base64.b64encode(compressed).decode("ascii")
        man[uid]["data"] = b64
        man[uid]["compressed"] = True
        updated.append(f"{name} → {uid[:8]} ({len(raw)} bytes)")

    new_man = json.dumps(man, separators=(",", ":"), ensure_ascii=False)
    html2, n = re.subn(
        r'(<script type="__bundler/manifest">)(.*?)(</script>)',
        lambda m: m.group(1) + new_man + m.group(3),
        html,
        count=1,
        flags=re.S,
    )
    if n != 1:
        raise SystemExit("manifest replace failed")
    HTML.write_text(html2, encoding="utf-8")
    print("Packed", HTML)
    for line in updated:
        print(" ", line)


if __name__ == "__main__":
    main()
