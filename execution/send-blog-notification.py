#!/usr/bin/env python3
"""Blog yayın bildirimi — e-posta (+ FormSubmit / WhatsApp yedek)."""
from __future__ import annotations

import argparse
import json
import os
import re
import smtplib
import ssl
import urllib.error
import urllib.parse
import urllib.request
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(to_addrs: list[str], subject: str, html: str) -> None:
    host = os.environ.get("BLOG_SMTP_HOST", "smtp.hostinger.com")
    port = int(os.environ.get("BLOG_SMTP_PORT", "465"))
    user = os.environ.get("BLOG_SMTP_USER", "info@nefalix.com")
    password = os.environ.get("BLOG_SMTP_PASSWORD", "")
    from_addr = os.environ.get("BLOG_SMTP_FROM", user)

    if not password:
        raise RuntimeError(
            "BLOG_SMTP_PASSWORD eksik — VPS .env içine info@nefalix.com şifresini ekleyin"
        )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"Nefalix Blog <{from_addr}>"
    msg["To"] = ", ".join(to_addrs)
    msg.attach(MIMEText(html, "html", "utf-8"))

    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL(host, port, context=ctx) as smtp:
        smtp.login(user, password)
        smtp.sendmail(from_addr, to_addrs, msg.as_string())


def send_via_formsubmit(to_addrs: list[str], subject: str, html: str) -> None:
    plain = re.sub(r"<[^>]+>", " ", html).replace("  ", " ").strip()
    body_text = f"{subject}\n\n{plain}"
    for addr in to_addrs:
        payload = json.dumps(
            {
                "_subject": subject,
                "message": body_text,
                "_captcha": "false",
                "_template": "box",
            }
        ).encode()
        req = urllib.request.Request(
            f"https://formsubmit.co/ajax/{urllib.parse.quote(addr)}",
            data=payload,
            method="POST",
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=45) as res:
            if res.status not in (200, 201):
                raise RuntimeError(f"FormSubmit {addr}: HTTP {res.status}")


def send_whatsapp_fallback(text: str) -> bool:
    base = (os.environ.get("EVOLUTION_API_URL") or os.environ.get("EVOLUTION_SERVER_URL") or "").rstrip("/")
    key = os.environ.get("EVOLUTION_API_KEY", "")
    instance = os.environ.get("EVOLUTION_INSTANCE", "")
    number = os.environ.get("CLINIC_MANAGER_WHATSAPP", "").replace("+", "").replace(" ", "")
    if not (base and key and instance and number):
        return False
    payload = json.dumps({"number": number, "text": text}).encode()
    req = urllib.request.Request(
        f"{base}/message/sendText/{instance}",
        data=payload,
        method="POST",
        headers={"apikey": key, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            return 200 <= res.status < 300
    except urllib.error.HTTPError:
        return False


def build_html(posts: list[dict]) -> str:
    items = []
    for p in posts:
        when = p.get("publish_label", "Yayında")
        items.append(
            f'<li style="margin-bottom:14px;">'
            f'<strong>{p["title"]}</strong><br>'
            f'<span style="color:#64748b;">{when}</span><br>'
            f'<a href="{p["url"]}" style="color:#0d9488;">{p["url"]}</a>'
            f"</li>"
        )
    return f"""<!DOCTYPE html>
<html><body style="font-family:system-ui,sans-serif;color:#0f172a;max-width:560px;">
<p>Merhaba,</p>
<p>Bugün planlanan Nefalix blog yazıları:</p>
<ul>{"".join(items)}</ul>
<p style="color:#64748b;font-size:13px;">Tüm yazılar: <a href="https://nefalix.com/kaynaklar">nefalix.com/kaynaklar</a></p>
<p>— Nefalix otomasyon</p>
</body></html>"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--posts-json", required=True, help="JSON dizi: title, url, publish_label")
    parser.add_argument(
        "--to",
        default="enes.ceylan190758@gmail.com,akadirysr@gmail.com",
        help="Virgülle ayrılmış alıcılar",
    )
    args = parser.parse_args()

    posts = json.loads(args.posts_json)
    to_addrs = [x.strip() for x in args.to.split(",") if x.strip()]
    subject = f"Nefalix Blog — {posts[0]['title']}" if len(posts) == 1 else f"Nefalix Blog — {len(posts)} yeni yazı"
    html = build_html(posts)

    try:
        send_email(to_addrs, subject, html)
        print(json.dumps({"ok": True, "channel": "email", "to": to_addrs}, ensure_ascii=False))
    except Exception as exc:
        try:
            send_via_formsubmit(to_addrs, subject, html)
            print(
                json.dumps(
                    {"ok": True, "channel": "formsubmit", "to": to_addrs, "smtp_note": str(exc)},
                    ensure_ascii=False,
                )
            )
        except Exception as exc2:
            wa_text = "Nefalix blog yazıları:\n" + "\n".join(
                f"• {p['title']}\n  {p['url']} ({p.get('publish_label', '')})" for p in posts
            )
            if send_whatsapp_fallback(wa_text):
                print(
                    json.dumps(
                        {
                            "ok": True,
                            "channel": "whatsapp",
                            "email_error": str(exc),
                            "formsubmit_error": str(exc2),
                        },
                        ensure_ascii=False,
                    )
                )
            else:
                raise SystemExit(f"E-posta gönderilemedi: {exc}; FormSubmit: {exc2}") from exc2


if __name__ == "__main__":
    main()
