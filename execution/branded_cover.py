"""Nefalix markalı kapak URL — /api/blog?action=cover, gerçek Unsplash
fotoğrafına 302 redirect (v7). SVG-üzeri-metin yok; kategori/başlık
kartın altındaki beyaz alanda gösterilir (Swell mantığı)."""
from __future__ import annotations

import urllib.parse

SITE = "https://nefalix.com"
COVER_VERSION = "7"


def branded_cover_url(*, title: str, tag: str = "Rehber", kind: str = "blog") -> str:
    q = urllib.parse.urlencode(
        {
            "action": "cover",
            "kind": kind,
            "tag": (tag or "Rehber")[:40],
            "t": (title or "Nefalix")[:90],
            "v": COVER_VERSION,
        }
    )
    return f"{SITE}/api/blog?{q}"


def branded_footer_url(*, tag: str = "Rehber") -> str:
    q = urllib.parse.urlencode(
        {
            "action": "cover",
            "kind": "footer",
            "tag": (tag or "Rehber")[:40],
            "t": "Nefalix",
            "v": COVER_VERSION,
        }
    )
    return f"{SITE}/api/blog?{q}"
