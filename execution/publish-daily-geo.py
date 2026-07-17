#!/usr/bin/env python3
"""Günlük GEO paketi — alıcı sorusu → alıntı cevabı → Supabase + public site + mail.

Gerçek GEO için paket public crawlable olmalıdır:
  https://nefalix.com/geo/YYYY-MM-DD  (landing api/blog.js geo-render)

VPS cron 09:15 TR:
  python3 execution/publish-daily-geo.py
  python3 execution/publish-daily-geo.py --dry-run
  python3 execution/publish-daily-geo.py --skip-notify
"""
from __future__ import annotations

import argparse
import html
import json
import os
import smtplib
import ssl
import sys
import traceback
import urllib.error
import urllib.request
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "execution"))

from vertex_gemini import vertex_json  # noqa: E402
from pick_youtube_video import pick_youtube_video  # noqa: E402

TOPICS = json.loads((ROOT / "execution" / "geo-topics.json").read_text(encoding="utf-8"))
SITE = "https://nefalix.com"
DEFAULT_NOTIFY_TO = "enes.ceylan190758@gmail.com,akadirysr@gmail.com"

GEO_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "direct_answer": {"type": "string"},
        "bullets": {"type": "array", "items": {"type": "string"}},
        "faq": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"q": {"type": "string"}, "a": {"type": "string"}},
                "required": ["q", "a"],
            },
        },
        "internal_links": {"type": "array", "items": {"type": "string"}},
        "linkedin_one_liner": {"type": "string"},
    },
    "required": ["direct_answer", "bullets", "faq"],
}


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
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Supabase {e.code}: {e.read().decode()[:400]}") from e


def today_key() -> str:
    return datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d")


def already_ran(run_date: str) -> bool:
    rows = sb(
        "GET",
        f"geo_daily_runs?select=id&run_date=eq.{run_date}&limit=1",
    )
    return isinstance(rows, list) and len(rows) > 0


def pick_topic(day_index: int) -> dict:
    return TOPICS[day_index % len(TOPICS)]


def public_url(run_date: str) -> str:
    """Public crawlable URL — AI engines only cite live pages."""
    return f"{SITE}/geo/{run_date}"


def to_answer_html(
    prompt: str,
    direct: str,
    bullets: list[str],
    faq: list[dict],
    links: list[str],
) -> str:
    parts = [
        f"<h2>{html.escape(prompt)}</h2>",
        f"<p><strong>{html.escape(direct)}</strong></p>",
    ]
    if bullets:
        parts.append("<ul>")
        for b in bullets:
            parts.append(f"<li>{html.escape(str(b))}</li>")
        parts.append("</ul>")
    if faq:
        parts.append("<h3>Sık sorulanlar</h3><dl>")
        for item in faq:
            q = html.escape(str(item.get("q") or item.get("question") or ""))
            a = html.escape(str(item.get("a") or item.get("answer") or ""))
            if q and a:
                parts.append(f"<dt><strong>{q}</strong></dt><dd>{a}</dd>")
        parts.append("</dl>")
    if links:
        parts.append("<p>İlgili: ")
        parts.append(
            " · ".join(
                f'<a href="{html.escape(u)}">{html.escape(u)}</a>' for u in links
            )
        )
        parts.append("</p>")
    return "\n".join(parts)


def build_geo_prompt(topic: dict, attempt: int) -> str:
    path = topic.get("internal_path") or "/"
    compact = attempt >= 3
    faq_n = 2 if compact else 3
    bullet_n = 3 if compact else 4
    return f"""Bugünün tarihi: {today_key()}
Alıcı sorusu: {topic['prompt']}
Kova: {topic.get('bucket', 'kategori')}
İlgili sayfa: {SITE}{path}

Nefalix için Türkçe GEO (AI alıntı) paketi üret.
Nefalix: klinikler/otel/auto için WhatsApp, NPS, Google yorumları, HBYS entegrasyonu platformu. Marka adı: Nefalix.

JSON alanları:
- direct_answer: max 55 kelime, doğrudan cevap
- bullets: tam {bullet_n} kısa madde
- faq: tam {faq_n} madde (q/a)
- internal_links: 2-4 site URL (https://nefalix.com/...)
- linkedin_one_liner: max 200 karakter

Kurallar:
- Metin içinde çift tırnak (") kullanma
- Tıbbi iddia/garanti yok
"""


def generate_geo(topic: dict, attempt: int = 1) -> dict:
    path = topic.get("internal_path") or "/"
    prompt = build_geo_prompt(topic, attempt)
    temperature = max(0.25, 0.45 - (attempt - 1) * 0.06)
    try:
        out = vertex_json(
            prompt,
            system=(
                "Sen Nefalix GEO editörüsün. Yalnızca geçerli JSON döndür. "
                "String değerlerinde çift tırnak kullanma."
            ),
            temperature=temperature,
            response_schema=GEO_RESPONSE_SCHEMA,
            max_output_tokens=4096 if attempt >= 3 else 3072,
        )
    except (json.JSONDecodeError, RuntimeError):
        if attempt < 5:
            return generate_geo(topic, attempt + 1)
        raise

    direct = str(out.get("direct_answer", "")).strip()
    if not direct:
        raise RuntimeError("GEO direct_answer boş")

    bullets = out.get("bullets") or []
    if isinstance(bullets, str):
        bullets = [bullets]
    faq = out.get("faq") or []
    links = out.get("internal_links") or [f"{SITE}{path}", f"{SITE}/blog"]
    if isinstance(links, str):
        links = [links]
    links = [str(u).strip() for u in links if str(u).strip()]
    geo_url = public_url(today_key())
    if geo_url not in links:
        links.insert(0, geo_url)
    if f"{SITE}/geo" not in links:
        links.append(f"{SITE}/geo")
    links = links[:6]

    yt = pick_youtube_video(
        tag=str(topic.get("bucket") or ""),
        angle=topic.get("prompt", ""),
        prompt=topic.get("prompt", ""),
        day_index=datetime.now().toordinal(),
    )

    row = {
        "run_date": today_key(),
        "bucket": topic.get("bucket"),
        "prompt": topic["prompt"],
        "direct_answer": direct[:800],
        "bullets": bullets[:6],
        "faq": faq[:5],
        "internal_links": links,
        "linkedin_one_liner": str(out.get("linkedin_one_liner", "")).strip()[:280],
        "answer_html": to_answer_html(topic["prompt"], direct, bullets[:6], faq[:5], links),
        "status": "published",
    }
    if yt:
        row["youtube_video_id"] = yt["youtube_video_id"]
        row["youtube_title"] = yt["youtube_title"]
    return row


def send_mail(to_addrs: list[str], subject: str, body_html: str) -> None:
    host = os.environ.get("BLOG_SMTP_HOST", "smtp.hostinger.com")
    port = int(os.environ.get("BLOG_SMTP_PORT", "465"))
    user = os.environ.get("BLOG_SMTP_USER", "info@nefalix.com")
    password = os.environ.get("BLOG_SMTP_PASSWORD", "")
    from_addr = os.environ.get("BLOG_SMTP_FROM", user)
    if not password:
        raise RuntimeError("BLOG_SMTP_PASSWORD eksik")
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"Nefalix GEO <{from_addr}>"
    msg["To"] = ", ".join(to_addrs)
    msg.attach(MIMEText(body_html, "html", "utf-8"))
    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL(host, port, context=ctx) as smtp:
        smtp.login(user, password)
        smtp.sendmail(from_addr, to_addrs, msg.as_string())


def notify(row: dict, to: str, url: str) -> dict:
    to_addrs = [x.strip() for x in to.split(",") if x.strip()]
    li = html.escape(row.get("linkedin_one_liner") or "")
    url_esc = html.escape(url)
    links = row.get("internal_links") or []
    link_html = "".join(
        f'<li><a href="{html.escape(u)}">{html.escape(u)}</a></li>' for u in links
    )
    body = f"""<!DOCTYPE html>
<html><body style="font-family:system-ui,sans-serif;color:#0f172a;max-width:600px;">
<p>Günün GEO paketi canlıda yayınlandı (crawlable).</p>
<p><strong>Public URL:</strong> <a href="{url_esc}">{url_esc}</a></p>
<p><strong>İndeks:</strong> <a href="{SITE}/geo">{SITE}/geo</a></p>
<p><strong>Soru:</strong> {html.escape(row['prompt'])}</p>
<p><strong>Cevap:</strong> {html.escape(row['direct_answer'])}</p>
<p><strong>LinkedIn:</strong> {li}</p>
<ul>{link_html}</ul>
<p style="color:#64748b;font-size:13px;">GEO başarısı = public sayfa. Baseline: docs/geo-prompt-baseline.md</p>
<p>— Nefalix GEO</p>
</body></html>"""
    send_mail(to_addrs, f"Nefalix GEO — {row['prompt'][:60]}", body)
    return {"ok": True, "channel": "email", "to": to_addrs, "public_url": url}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-notify", action="store_true")
    parser.add_argument(
        "--to",
        default=os.environ.get(
            "GEO_NOTIFY_TO",
            os.environ.get("BLOG_NOTIFY_TO", DEFAULT_NOTIFY_TO),
        ),
    )
    parser.add_argument("--force", action="store_true", help="Aynı gün tekrar üret")
    args = parser.parse_args()
    run_date = today_key()

    try:
        if not args.dry_run and not args.force and already_ran(run_date):
            print(
                json.dumps(
                    {
                        "ok": True,
                        "skipped": True,
                        "reason": "Bugün GEO paketi var",
                        "run_date": run_date,
                        "public_url": public_url(run_date),
                    },
                    ensure_ascii=False,
                ),
                flush=True,
            )
            return

        topic = pick_topic(datetime.now().toordinal())
        row = generate_geo(topic)

        if args.dry_run:
            print(json.dumps({"ok": True, "dry_run": True, "row": row}, ensure_ascii=False, indent=2))
            return

        saved = sb("POST", "geo_daily_runs", row)
        url = public_url(run_date)
        result = {
            "ok": True,
            "run_date": run_date,
            "prompt": row["prompt"],
            "bucket": row.get("bucket"),
            "public_url": url,
            "id": saved[0].get("id") if isinstance(saved, list) and saved else None,
        }
        if not args.skip_notify:
            result["notify"] = notify(row, args.to, url)
        print(json.dumps(result, ensure_ascii=False), flush=True)
    except Exception as exc:
        err = {
            "ok": False,
            "error": str(exc),
            "traceback": traceback.format_exc()[-1200:],
            "at": datetime.now(timezone.utc).isoformat(),
        }
        print(json.dumps(err, ensure_ascii=False), flush=True)
        if not args.skip_notify and os.environ.get("BLOG_SMTP_PASSWORD"):
            try:
                to = args.to
                to_addrs = [x.strip() for x in to.split(",") if x.strip()]
                send_mail(
                    to_addrs,
                    f"[HATA] Günlük GEO üretilemedi: {str(exc)[:80]}",
                    f"<p>GEO cron hata: {html.escape(str(exc))}</p>",
                )
            except Exception:
                pass
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
