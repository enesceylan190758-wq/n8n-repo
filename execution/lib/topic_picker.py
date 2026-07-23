"""Konu seçimi: son N gün tekrar etme + bucket dengesi."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Callable


def _iso_days_ago(days: int) -> str:
    dt = datetime.now(timezone.utc) - timedelta(days=days)
    return dt.strftime("%Y-%m-%d")


def recent_geo_prompts(sb_get: Callable[[str], Any], *, days: int = 21) -> set[str]:
    since = _iso_days_ago(days)
    rows = sb_get(
        f"geo_daily_runs?select=prompt,bucket,run_date&run_date=gte.{since}&order=run_date.desc"
    )
    if not isinstance(rows, list):
        return set()
    return {str(r.get("prompt") or "").strip() for r in rows if r.get("prompt")}


def recent_geo_buckets(sb_get: Callable[[str], Any], *, days: int = 7) -> list[str]:
    since = _iso_days_ago(days)
    rows = sb_get(
        f"geo_daily_runs?select=bucket,run_date&run_date=gte.{since}&order=run_date.desc"
    )
    if not isinstance(rows, list):
        return []
    return [str(r.get("bucket") or "").lower() for r in rows]


def recent_blog_tags(sb_get: Callable[[str], Any], *, days: int = 21) -> set[str]:
    since = _iso_days_ago(days) + "T00:00:00"
    rows = sb_get(
        "blog_posts?select=tag,published_at&status=eq.published"
        f"&published_at=gte.{since}&order=published_at.desc"
    )
    if not isinstance(rows, list):
        return set()
    return {str(r.get("tag") or "").strip() for r in rows if r.get("tag")}


def pick_geo_topic(
    topics: list[dict[str, Any]],
    day_index: int,
    *,
    recent_prompts: set[str] | None = None,
    recent_buckets: list[str] | None = None,
) -> dict[str, Any]:
    """Son prompt'ları atla; aynı haftada aynı bucket'ı 3× aşma."""
    if not topics:
        raise RuntimeError("geo-topics boş")
    recent_prompts = recent_prompts or set()
    recent_buckets = [b.lower() for b in (recent_buckets or [])]
    bucket_counts: dict[str, int] = {}
    for b in recent_buckets:
        bucket_counts[b] = bucket_counts.get(b, 0) + 1

    n = len(topics)
    for offset in range(n):
        topic = topics[(day_index + offset) % n]
        prompt = str(topic.get("prompt") or "").strip()
        bucket = str(topic.get("bucket") or "").lower()
        if prompt and prompt in recent_prompts:
            continue
        if bucket and bucket_counts.get(bucket, 0) >= 3:
            continue
        return topic
    # fallback: sadece prompt çeşitliliği
    for offset in range(n):
        topic = topics[(day_index + offset) % n]
        prompt = str(topic.get("prompt") or "").strip()
        if prompt not in recent_prompts:
            return topic
    return topics[day_index % n]


def pick_blog_topic(
    topics: list[dict[str, Any]],
    day_index: int,
    *,
    recent_tags: set[str] | None = None,
) -> dict[str, Any]:
    if not topics:
        raise RuntimeError("blog-topics boş")
    recent_tags = {t.lower() for t in (recent_tags or set())}
    n = len(topics)
    for offset in range(n):
        topic = topics[(day_index + offset) % n]
        tag = str(topic.get("tag") or "").strip().lower()
        if tag and tag in recent_tags:
            continue
        return topic
    return topics[day_index % n]


def find_related_blog_slug(
    sb_get: Callable[[str], Any],
    *,
    tag_hint: str = "",
    keyword: str = "",
) -> str | None:
    """GEO paketinden blog hub linki için son yayınlanmış slug bul."""
    q = "blog_posts?select=slug,tag,title&status=eq.published&order=published_at.desc&limit=40"
    rows = sb_get(q)
    if not isinstance(rows, list):
        return None
    tag_hint_l = tag_hint.lower().strip()
    keyword_l = keyword.lower().strip()
    for r in rows:
        slug = str(r.get("slug") or "").strip()
        if not slug:
            continue
        tag = str(r.get("tag") or "").lower()
        title = str(r.get("title") or "").lower()
        if tag_hint_l and tag_hint_l in tag:
            return slug
        if keyword_l and (keyword_l in title or keyword_l in tag):
            return slug
    return None
