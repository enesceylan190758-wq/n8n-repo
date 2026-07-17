"""Konu metnine en yakın @Nefalixai videosunu seç."""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG = json.loads((ROOT / "execution" / "youtube-videos.json").read_text(encoding="utf-8"))


def _norm(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", text.lower()).strip()


def pick_youtube_video(
    *,
    tag: str = "",
    angle: str = "",
    prompt: str = "",
    day_index: int = 0,
) -> dict | None:
    if not CATALOG:
        return None
    haystack = _norm(f"{tag} {angle} {prompt}")
    best = None
    best_score = 0
    for video in CATALOG:
        score = 0
        for t in video.get("tags") or []:
            if _norm(t) in haystack:
                score += 4
        for kw in video.get("keywords") or []:
            nk = _norm(kw)
            if nk and nk in haystack:
                score += 2
        if score > best_score:
            best_score = score
            best = video
    if not best:
        best = CATALOG[day_index % len(CATALOG)]
    return {
        "youtube_video_id": best["id"],
        "youtube_title": best["title"],
    }
