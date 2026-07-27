#!/usr/bin/env python3
"""Pack nefalix-hasta-crm-app changes back into nefalix-hasta-crm.html."""
from __future__ import annotations

import base64
import gzip
import json
import re
from pathlib import Path

LANDING = Path("/Users/enesceylan/nefalix-landing")
HTML = LANDING / "nefalix-hasta-crm.html"
APP = LANDING / "nefalix-hasta-crm-app"
STORE_UUID = "a90a0ed2-5e97-4f96-9a33-f09210399e03"


def main() -> None:
    html = HTML.read_text(encoding="utf-8")
    man = json.loads(re.search(r'<script type="__bundler/manifest">(.*?)</script>', html, re.S).group(1))
    files = ["store.js", "Login.dc.html", "index.html"]
    updated = []
    for name in files:
        path = APP / name
        if not path.exists():
            print("skip missing", name)
            continue
        if name == "index.html":
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
                raise SystemExit("template replace failed")
            html = html2
            updated.append(f"index.html → __bundler/template ({len(raw)} bytes)")
            continue
        uid = STORE_UUID if name == "store.js" else None
        if name == "store.js":
            raw = path.read_bytes()
            (APP / "_assets" / f"{uid}.js").write_bytes(raw)
            compressed = gzip.compress(raw, compresslevel=9)
            man[uid]["data"] = base64.b64encode(compressed).decode("ascii")
            man[uid]["compressed"] = True
            updated.append(f"{name} → {uid[:8]} ({len(raw)} bytes)")
            continue
        # Login.dc.html — ext resources uuid lookup
        ext = json.loads(re.search(r'<script type="__bundler/ext_resources">(.*?)</script>', html, re.S).group(1))
        uuid_map = {e["id"].lstrip("./"): e["uuid"] for e in ext}
        uid = uuid_map.get(name)
        if not uid or uid not in man:
            print("skip no uuid", name)
            continue
        raw = path.read_bytes()
        compressed = gzip.compress(raw, compresslevel=9)
        man[uid]["data"] = base64.b64encode(compressed).decode("ascii")
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
