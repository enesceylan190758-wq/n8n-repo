#!/usr/bin/env python3
"""Tek özet mail: batch blog + GEO linkleri.

  python3 execution/send-batch-digest.py --payload-json '{"blogs":[...],"geos":[...]}'
"""
from __future__ import annotations

import argparse
import html
import json
import os
import smtplib
import ssl
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TO = "enes.ceylan190758@gmail.com,akadirysr@gmail.com"
SITE = "https://nefalix.com"


def send_email(to_addrs: list[str], subject: str, body_html: str) -> None:
    host = os.environ.get("BLOG_SMTP_HOST", "smtp.hostinger.com")
    port = int(os.environ.get("BLOG_SMTP_PORT", "465"))
    user = os.environ.get("BLOG_SMTP_USER", "info@nefalix.com")
    password = os.environ.get("BLOG_SMTP_PASSWORD", "")
    from_addr = os.environ.get("BLOG_SMTP_FROM", user)
    if not password:
        raise RuntimeError("BLOG_SMTP_PASSWORD eksik")
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"Nefalix Content <{from_addr}>"
    msg["To"] = ", ".join(to_addrs)
    msg.attach(MIMEText(body_html, "html", "utf-8"))
    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL(host, port, context=ctx) as smtp:
        smtp.login(user, password)
        smtp.sendmail(from_addr, to_addrs, msg.as_string())


def build_html(blogs: list[dict], geos: list[dict]) -> str:
    blog_items = []
    for i, p in enumerate(blogs, 1):
        blog_items.append(
            f'<li style="margin:0 0 12px;">'
            f'<span style="color:#64748b;">{i}.</span> '
            f'<strong>{html.escape(p.get("title") or "")}</strong> '
            f'<span style="color:#F9734E;font-size:12px;font-weight:700;">{html.escape(p.get("tag") or "")}</span><br>'
            f'<a href="{html.escape(p.get("url") or "")}" style="color:#2F6BFF;">{html.escape(p.get("url") or "")}</a>'
            f"</li>"
        )
    geo_items = []
    for i, g in enumerate(geos, 1):
        geo_items.append(
            f'<li style="margin:0 0 12px;">'
            f'<span style="color:#64748b;">{i}.</span> '
            f'<strong>{html.escape(g.get("prompt") or "")}</strong> '
            f'<span style="color:#7C5CF5;font-size:12px;font-weight:700;">{html.escape(g.get("bucket") or "GEO")}</span> '
            f'<span style="color:#64748b;font-size:12px;">· {html.escape(g.get("run_date") or "")}</span><br>'
            f'<a href="{html.escape(g.get("url") or "")}" style="color:#2F6BFF;">{html.escape(g.get("url") or "")}</a>'
            f"</li>"
        )
    return f"""<!DOCTYPE html>
<html><body style="font-family:system-ui,-apple-system,sans-serif;color:#0f172a;max-width:640px;line-height:1.5;">
<p>Merhaba,</p>
<p><strong>10 blog + 10 GEO</strong> (SEO / AI arama odaklı) canlıya alındı. Tek özet:</p>
<p style="margin:18px 0 8px;"><strong style="color:#F9734E;">Blog playbook’ları</strong>
 · <a href="{SITE}/blog">{SITE}/blog</a></p>
<ul style="padding-left:18px;">{"".join(blog_items) or "<li>—</li>"}</ul>
<p style="margin:22px 0 8px;"><strong style="color:#7C5CF5;">GEO paketleri</strong>
 · <a href="{SITE}/geo">{SITE}/geo</a></p>
<ul style="padding-left:18px;">{"".join(geo_items) or "<li>—</li>"}</ul>
<p style="color:#64748b;font-size:13px;margin-top:24px;">Konu seti: AEO, AI Overviews, ChatGPT/Perplexity/Gemini alıntısı, entity, citation ölçümü.</p>
<p>— Nefalix otomasyon</p>
</body></html>"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--payload-json", required=True, help='{"blogs":[...],"geos":[...]}')
    parser.add_argument(
        "--to",
        default=os.environ.get("BLOG_NOTIFY_TO", DEFAULT_TO),
    )
    parser.add_argument(
        "--subject",
        default="Nefalix — 10 Blog + 10 GEO (SEO/AI) hazır",
    )
    args = parser.parse_args()
    payload = json.loads(args.payload_json)
    blogs = payload.get("blogs") or []
    geos = payload.get("geos") or []
    to_addrs = [x.strip() for x in args.to.split(",") if x.strip()]
    body = build_html(blogs, geos)
    send_email(to_addrs, args.subject, body)
    print(
        json.dumps(
            {"ok": True, "channel": "email", "to": to_addrs, "blogs": len(blogs), "geos": len(geos)},
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        raise SystemExit(1) from exc
