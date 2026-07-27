#!/usr/bin/env python3
"""Günlük blog yazısı üret → Supabase blog_posts → yöneticilere mail.

GEO formatı: answer-first intro + H2 bölümler + SSS.
VPS cron (her gün 09:05 TR) veya manuel:
  python3 execution/publish-daily-blog.py
  python3 execution/publish-daily-blog.py --dry-run
  python3 execution/publish-daily-blog.py --skip-notify
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import subprocess
import sys
import traceback
import unicodedata
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "execution"))

from vertex_gemini import vertex_json  # noqa: E402
from pick_youtube_video import pick_youtube_video  # noqa: E402
from branded_cover import branded_cover_url, branded_footer_url  # noqa: E402

TOPICS = json.loads((ROOT / "execution" / "blog-topics.json").read_text(encoding="utf-8"))

BLOG_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "tag": {"type": "string"},
        "excerpt": {"type": "string"},
        "meta_description": {"type": "string"},
        "intro": {"type": "string"},
        "takeaways": {"type": "array", "items": {"type": "string"}},
        "sections": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "heading": {"type": "string"},
                    "body": {"type": "string"},
                },
                "required": ["heading", "body"],
            },
        },
        "checklist": {"type": "array", "items": {"type": "string"}},
        "faq": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "q": {"type": "string"},
                    "a": {"type": "string"},
                },
                "required": ["q", "a"],
            },
        },
        "cta": {"type": "string"},
    },
    "required": ["title", "excerpt", "meta_description", "intro", "sections", "faq", "takeaways"],
}

DEFAULT_NOTIFY_TO = "enes.ceylan190758@gmail.com,akadirysr@gmail.com"


def sb_base() -> str:
    base = os.environ.get("SUPABASE_URL", "http://127.0.0.1:54321").rstrip("/")
    if "host.docker.internal" in base:
        base = "http://127.0.0.1:54321"
    return base


def sb(method: str, path: str, body: dict | None = None) -> list | dict:
    base = sb_base()
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not key:
        raise SystemExit("SUPABASE_SERVICE_ROLE_KEY eksik")
    url = f"{base}/rest/v1/{path}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Supabase {e.code}: {e.read().decode()[:400]}") from e


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    return text[:80] or "yazi"


def today_key() -> str:
    return datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d")


def recent_slugs(limit: int = 30) -> set[str]:
    rows = sb(
        "GET",
        "blog_posts?select=slug,title,published_at&order=published_at.desc&limit="
        + str(limit),
    )
    if not isinstance(rows, list):
        return set()
    return {r.get("slug", "") for r in rows}


def pick_topic(day_index: int) -> dict:
    return TOPICS[day_index % len(TOPICS)]


def geo_body_to_html(
    intro: str,
    sections: list[dict],
    faq: list[dict],
    cta: str,
    takeaways: list | None = None,
    checklist: list | None = None,
) -> str:
    parts: list[str] = []
    intro = str(intro or "").strip()
    if intro:
        parts.append(f'<p class="blog-lede"><strong>{html.escape(intro)}</strong></p>')
    if takeaways:
        parts.append('<div class="blog-takeaways"><h2>Öne çıkanlar</h2><ul>')
        for item in takeaways[:6]:
            t = str(item or "").strip()
            if t:
                parts.append(f"<li>{html.escape(t)}</li>")
        parts.append("</ul></div>")
    for sec in sections or []:
        heading = str(sec.get("heading") or sec.get("h2") or "").strip()
        body = str(sec.get("body") or sec.get("text") or "").strip()
        if heading:
            parts.append(f"<h2>{html.escape(heading)}</h2>")
        if body:
            # Split long bodies into paragraphs on double newline or ~2 sentences
            chunks = [c.strip() for c in re.split(r"\n+", body) if c.strip()]
            if len(chunks) == 1 and len(body) > 420:
                # soft-split on sentence ends
                sents = re.split(r"(?<=[.!?])\s+", body)
                mid = max(2, len(sents) // 2)
                chunks = [" ".join(sents[:mid]).strip(), " ".join(sents[mid:]).strip()]
                chunks = [c for c in chunks if c]
            for chunk in chunks:
                parts.append(f"<p>{html.escape(chunk)}</p>")
    if checklist:
        parts.append('<div class="blog-checklist"><h2>Uygulama kontrol listesi</h2><ul>')
        for item in checklist[:8]:
            t = str(item or "").strip()
            if t:
                parts.append(f"<li>{html.escape(t)}</li>")
        parts.append("</ul></div>")
    if faq:
        parts.append("<h2>Sık sorulan sorular</h2>")
        for item in faq:
            q = str(item.get("q") or item.get("question") or "").strip()
            a = str(item.get("a") or item.get("answer") or "").strip()
            if not q or not a:
                continue
            parts.append(
                f'<div class="faq-item"><h3>{html.escape(q)}</h3>'
                f"<p>{html.escape(a)}</p></div>"
            )
    cta = str(cta or "").strip()
    if cta:
        parts.append(f'<p class="blog-cta">{html.escape(cta)}</p>')
    return "\n".join(parts)


def build_prompt(topic: dict, attempt: int) -> str:
    compact = attempt >= 4
    section_count = 3 if compact else 5
    faq_count = 4 if compact else 6
    section_words = 160 if compact else 220
    return f"""Bugünün tarihi: {today_key()}
Konu etiketi: {topic['tag']}
Açı: {topic['angle']}

Nefalix için Türkçe, Swell CX Resources seviyesinde KALLAVİ bir playbook yazısı yaz.
Hedef okuyucu: klinik sahibi, operasyon müdürü, hasta deneyimi sorumlusu.
Nefalix: klinik/otel/auto için WhatsApp, NPS, Google yorumları, HBYS entegrasyonu platformu.

Ton: uzman, net, operasyonel. Boş slogan yok. Somut adım, metrik, örnek mesaj kalıbı ver.
Okuyucu yazıyı bitirince yarın klinikte uygulayabilmeli.

JSON alanları:
- title: max 85 karakter, vaat + net sonuç (clickbait yok)
- excerpt: max 200 karakter, neden okumalı
- meta_description: max 155 karakter
- intro: 80-110 kelime, doğrudan cevap + bağlam
- takeaways: 5 maddelik öne çıkanlar (kısa, aksiyon)
- sections: tam {section_count} madde; heading soru veya net başlık; body ~{section_words} kelime (2 paragraf; \\n ile ayır)
- checklist: 6 uygulama maddesi (sırayla yapılabilir)
- faq: tam {faq_count} madde; pratik cevap (40-70 kelime)
- cta: 1-2 cümle, hafif Nefalix çağrısı (garanti yok)
- tag: "{topic['tag']}"

Kurallar:
- Metin içinde çift tırnak (") kullanma; gerekirse tek tırnak veya tire kullan
- Markdown kullanma
- Tıbbi tedavi iddiası veya garanti verme
- Genel gevezelik yok; her bölümde klinik operasyon örneği olsun
- En az bir bölümde örnek WhatsApp/SMS mesaj kalıbı veya skor eşiği (ör. NPS <7) olsun
"""


def generate_post(topic: dict, used_slugs: set[str], attempt: int = 1) -> dict:
    prompt = build_prompt(topic, attempt)
    temperature = max(0.25, 0.55 - (attempt - 1) * 0.08)
    try:
        out = vertex_json(
            prompt,
            system=(
                "Sen Nefalix kıdemli içerik editörüsün. "
                "Swell CX tarzı derin playbook yazarsın. "
                "Yalnızca şemaya uygun geçerli JSON döndür. "
                "String değerlerinde çift tırnak kullanma."
            ),
            temperature=temperature,
            response_schema=BLOG_RESPONSE_SCHEMA,
            max_output_tokens=8192,
        )
    except (json.JSONDecodeError, RuntimeError):
        if attempt < 5:
            return generate_post(topic, used_slugs, attempt + 1)
        raise
    title = str(out.get("title", "")).strip()
    if not title:
        raise RuntimeError("AI başlık üretemedi")

    base_slug = slugify(title)
    slug = base_slug
    n = 2
    while slug in used_slugs:
        slug = f"{base_slug}-{n}"
        n += 1

    sections = out.get("sections") or []
    faq = out.get("faq") or []
    intro = str(out.get("intro") or "").strip()
    if not intro and out.get("paragraphs"):
        paras = out["paragraphs"]
        if isinstance(paras, list) and paras:
            intro = str(paras[0])
            sections = [
                {"heading": f"{topic['tag']} hakkında", "body": str(p)}
                for p in paras[1:]
            ]

    tag = str(out.get("tag") or topic["tag"]).strip() or topic["tag"]
    cover = branded_cover_url(title=title, tag=tag, kind="blog")
    footer = branded_footer_url(tag=tag)
    body_html = geo_body_to_html(
        intro,
        sections,
        faq,
        str(out.get("cta") or ""),
        takeaways=out.get("takeaways") or [],
        checklist=out.get("checklist") or [],
    )

    yt = pick_youtube_video(
        tag=tag,
        angle=topic.get("angle", ""),
        prompt=title,
        day_index=datetime.now().toordinal(),
    )

    post = {
        "slug": slug,
        "title": title,
        "tag": tag,
        "excerpt": str(out.get("excerpt", "")).strip()[:280],
        "meta_description": str(out.get("meta_description") or out.get("excerpt", "")).strip()[:160],
        "body_html": body_html,
        "cover_image_url": cover,
        "footer_image_url": footer,
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
    }
    if yt:
        post["youtube_video_id"] = yt["youtube_video_id"]
        post["youtube_title"] = yt["youtube_title"]
    return post


def notify_managers(title: str, url: str, to: str) -> dict:
    posts_json = json.dumps(
        [{"title": title, "url": url, "publish_label": "Yayında"}],
        ensure_ascii=False,
    )
    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / "execution" / "send-blog-notification.py"),
            "--posts-json",
            posts_json,
            "--to",
            to,
        ],
        capture_output=True,
        text=True,
        timeout=90,
    )
    out = (proc.stdout or "").strip() or (proc.stderr or "").strip()
    if proc.returncode != 0:
        return {"ok": False, "detail": out[:500]}
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return {"ok": True, "raw": out[:300]}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-notify", action="store_true")
    parser.add_argument(
        "--topic-index",
        type=int,
        default=None,
        help="Konu indeksi (mod len(TOPICS)); yoksa bugünün ordinali",
    )
    parser.add_argument(
        "--to",
        default=os.environ.get("BLOG_NOTIFY_TO", DEFAULT_NOTIFY_TO),
        help="Virgülle ayrılmış yönetici e-postaları",
    )
    args = parser.parse_args()

    try:
        used = recent_slugs()
        day_index = (
            args.topic_index
            if args.topic_index is not None
            else datetime.now().toordinal()
        )
        topic = pick_topic(day_index)
        post = generate_post(topic, used)

        if args.dry_run:
            print(json.dumps({"ok": True, "dry_run": True, "post": post}, ensure_ascii=False, indent=2))
            return

        rows = sb("POST", "blog_posts", post)
        row = rows[0] if isinstance(rows, list) and rows else post
        url = f"https://nefalix.com/blog/{row.get('slug', post['slug'])}"
        title = row.get("title", post["title"])
        result = {
            "ok": True,
            "slug": row.get("slug", post["slug"]),
            "title": title,
            "url": url,
            "published_at": row.get("published_at", post["published_at"]),
        }

        if not args.skip_notify:
            result["notify"] = notify_managers(title, url, args.to)

        print(json.dumps(result, ensure_ascii=False), flush=True)
    except Exception as exc:
        err = {
            "ok": False,
            "error": str(exc),
            "traceback": traceback.format_exc()[-1500:],
            "at": datetime.now(timezone.utc).isoformat(),
        }
        print(json.dumps(err, ensure_ascii=False), flush=True)
        if not args.skip_notify and os.environ.get("BLOG_SMTP_PASSWORD"):
            try:
                notify_managers(
                    f"[HATA] Günlük blog üretilemedi: {exc}",
                    "https://nefalix.com/blog",
                    args.to,
                )
            except Exception:
                pass
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
