#!/usr/bin/env python3
"""Günlük GEO paketi — alıcı sorusu → alıntı cevabı → Supabase + public site + mail.

Blog ≠ GEO.
  Blog  = uzun playbook (/blog/:slug)
  GEO   = kısa, answer-first, AI motorlarının alıntılayacağı paket (/geo/YYYY-MM-DD)

VPS cron 09:15 TR:
  python3 execution/publish-daily-geo.py
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

from lib.content_quality import (  # noqa: E402
    ALLOWED_PATHS,
    SITE,
    geo_cover_url,
    geo_quality_gate,
    looks_bloggy,
    normalize_geo_links,
    public_geo_url,
)
from lib.topic_picker import (  # noqa: E402
    find_related_blog_slug,
    pick_geo_topic,
    recent_geo_buckets,
    recent_geo_prompts,
)
from vertex_gemini import vertex_json  # noqa: E402

TOPICS = json.loads((ROOT / "execution" / "geo-topics.json").read_text(encoding="utf-8"))
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


def sb_get(path: str) -> list | dict:
    return sb("GET", path)


def today_key() -> str:
    return datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d")


def already_ran(run_date: str) -> bool:
    rows = sb("GET", f"geo_daily_runs?select=id&run_date=eq.{run_date}&limit=1")
    return isinstance(rows, list) and len(rows) > 0


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
            " · ".join(f'<a href="{html.escape(u)}">{html.escape(u)}</a>' for u in links)
        )
        parts.append("</p>")
    return "\n".join(parts)


def generate_geo(topic: dict, attempt: int = 1, *, retry_log: list[str] | None = None) -> dict:
    path = topic.get("internal_path") or "/"
    if path not in ALLOWED_PATHS:
        path = "/"
    bucket = topic.get("bucket", "kategori")
    brand_rule = (
        "Bu kova marka: Nefalix'i doğru tanımla; abartılı vaat yok."
        if bucket == "marka"
        else (
            "Bu kova marka değil: Cevabı operasyonel gerçeklerle ver. "
            "Nefalix en fazla bir kez, örnek araç olarak geçebilir; ürün reklamı yasak."
        )
    )

    prompt = f"""Bugünün tarihi: {today_key()}
Alıcı sorusu: {topic['prompt']}
Kova: {bucket}
İlgili sayfa (tek gerçek URL): {SITE}{path}

Görev: Türkçe GEO paketi üret — ChatGPT / Perplexity / Gemini / AI Overviews'ın alıntılayacağı kısa soru-cevap.

GEO ≠ blog. Yasak:
- Uzun rehber / playbook / "bu yazıda" dili
- "Nefalix ile kolaylaşır/hızlanır" satış açılışı
- Demo CTA, "hemen başla", abartılı vaat
- Uydurma URL (yalnızca verilen ilgili sayfa + /geo + /blog)

GEO zorunlu biçim:
1) direct_answer: 40-70 kelime, sorunun doğrudan cevabı, ilk cümlede net tanım/yöntem
2) bullets: 3-5 uygulanabilir madde (fiil ile başla)
3) faq: tam 3 madde; alan bilgisi, ürün satışı değil
4) linkedin_one_liner: max 220 karakter, tek cümle içgörü

{brand_rule}

Nefalix (yalnızca gerektiğinde): klinik/otel/auto için WhatsApp, NPS, Google yorum, HBYS geri bildirim otomasyonu. Marka adı: Nefalix.

JSON (tek nesne):
{{
  "direct_answer": "...",
  "bullets": ["...", "...", "..."],
  "faq": [{{"q": "...", "a": "..."}}, {{"q": "...", "a": "..."}}, {{"q": "...", "a": "..."}}],
  "internal_links": ["{SITE}{path}", "{SITE}/geo", "{SITE}/blog"],
  "linkedin_one_liner": "..."
}}
"""
    try:
        out = vertex_json(
            prompt,
            system=(
                "Sen Nefalix GEO editörüsün. Blog yazmazsın; AI alıntısı için "
                "kısa, nötr, answer-first JSON üretirsin. Yalnızca geçerli JSON."
            ),
            temperature=0.25 if attempt > 1 else 0.35,
        )
    except json.JSONDecodeError:
        if attempt < 3:
            return generate_geo(topic, attempt + 1, retry_log=retry_log)
        raise

    direct = str(out.get("direct_answer", "")).strip()
    if not direct:
        raise RuntimeError("GEO direct_answer boş")

    bullets = out.get("bullets") or []
    if isinstance(bullets, str):
        bullets = [bullets]
    bullets = [str(b).strip() for b in bullets if str(b).strip()][:6]

    faq = out.get("faq") or []
    if not isinstance(faq, list):
        faq = []
    faq = faq[:5]

    gate = geo_quality_gate(topic, direct, bullets, faq)
    if gate:
        if retry_log is not None:
            retry_log.append(f"attempt={attempt}: {gate}")
        if attempt < 4:
            return generate_geo(topic, attempt + 1, retry_log=retry_log)
        raise RuntimeError(f"GEO kalite kapısı başarısız: {gate}")

    run_date = today_key()
    related_slug = None
    try:
        related_slug = find_related_blog_slug(
            sb_get,
            tag_hint=str(bucket),
            keyword="geo" if "geo" in topic["prompt"].lower() else "",
        )
    except Exception:
        related_slug = None
    extra = [f"{SITE}/blog/{related_slug}"] if related_slug else []
    links = normalize_geo_links(
        out.get("internal_links") or [], path, run_date, extra_urls=extra
    )

    return {
        "run_date": run_date,
        "bucket": topic.get("bucket"),
        "prompt": topic["prompt"],
        "direct_answer": direct[:800],
        "bullets": bullets,
        "faq": faq,
        "internal_links": links,
        "linkedin_one_liner": str(out.get("linkedin_one_liner", "")).strip()[:280],
        "answer_html": to_answer_html(topic["prompt"], direct, bullets, faq, links),
        "cover_image_url": geo_cover_url(topic["prompt"], str(bucket or "GEO")),
        "status": "published",
        "_retry_log": retry_log or [],
    }


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
    bust = html.escape(f"{url}?v={today_key()}")
    body = f"""<!DOCTYPE html>
<html><body style="font-family:system-ui,sans-serif;color:#0f172a;max-width:600px;">
<p>Günün GEO paketi canlıda (crawlable). Bu bir blog yazısı değil; AI alıntı paketi.</p>
<p><strong>Public URL:</strong> <a href="{url_esc}">{url_esc}</a></p>
<p><strong>Cache-bust:</strong> <a href="{bust}">{bust}</a></p>
<p><strong>İndeks:</strong> <a href="{SITE}/geo">{SITE}/geo</a></p>
<p><strong>Soru:</strong> {html.escape(row['prompt'])}</p>
<p><strong>Cevap:</strong> {html.escape(row['direct_answer'])}</p>
<p><strong>LinkedIn:</strong> {li}</p>
<ul>{link_html}</ul>
<p style="color:#64748b;font-size:13px;">Citation skorları: execution/record-geo-citation.py</p>
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
                        "public_url": public_geo_url(run_date),
                    },
                    ensure_ascii=False,
                ),
                flush=True,
            )
            return

        day_index = datetime.now().toordinal()
        try:
            prompts = recent_geo_prompts(sb_get, days=21)
            buckets = recent_geo_buckets(sb_get, days=7)
        except Exception:
            prompts, buckets = set(), []
        topic = pick_geo_topic(
            TOPICS, day_index, recent_prompts=prompts, recent_buckets=buckets
        )
        retry_log: list[str] = []
        row = generate_geo(topic, retry_log=retry_log)
        retry_meta = row.pop("_retry_log", retry_log)

        if args.dry_run:
            print(
                json.dumps(
                    {"ok": True, "dry_run": True, "row": row, "retry_log": retry_meta},
                    ensure_ascii=False,
                    indent=2,
                )
            )
            return

        if args.force and already_ran(run_date):
            sb("DELETE", f"geo_daily_runs?run_date=eq.{run_date}")

        saved = sb("POST", "geo_daily_runs", row)
        url = public_geo_url(run_date)
        result = {
            "ok": True,
            "run_date": run_date,
            "prompt": row["prompt"],
            "bucket": row.get("bucket"),
            "public_url": url,
            "cache_bust_url": f"{url}?v={run_date}",
            "cover_image_url": row.get("cover_image_url"),
            "id": saved[0].get("id") if isinstance(saved, list) and saved else None,
            "retry_log": retry_meta,
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
                to_addrs = [x.strip() for x in args.to.split(",") if x.strip()]
                send_mail(
                    to_addrs,
                    f"[HATA] Günlük GEO üretilemedi: {str(exc)[:80]}",
                    f"<p>GEO cron hata: {html.escape(str(exc))}</p>",
                )
            except Exception:
                pass
        raise SystemExit(1) from exc


# Back-compat aliases for tests
quality_gate = geo_quality_gate
normalize_links = normalize_geo_links
public_url = public_geo_url


if __name__ == "__main__":
    main()
