#!/usr/bin/env python3
"""Pazar GEO citation hatırlatması — manuel skor için mail.

  python3 execution/send-geo-weekly-reminder.py
  python3 execution/send-geo-weekly-reminder.py --dry-run
"""
from __future__ import annotations

import argparse
import json
import os
import smtplib
import ssl
import sys
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_NOTIFY_TO = "enes.ceylan190758@gmail.com,akadirysr@gmail.com"


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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--to",
        default=os.environ.get(
            "GEO_NOTIFY_TO",
            os.environ.get("BLOG_NOTIFY_TO", DEFAULT_NOTIFY_TO),
        ),
    )
    args = parser.parse_args()
    week = datetime.now(timezone.utc).astimezone().strftime("%Y-W%W")
    body = f"""<!DOCTYPE html>
<html><body style="font-family:system-ui,sans-serif;max-width:600px;color:#0f172a;">
<p>Haftalık GEO citation ölçümü zamanı ({week}).</p>
<ol>
<li><code>docs/geo-prompt-baseline.md</code> dosyasını aç</li>
<li>25 prompt'u ChatGPT / Perplexity / Gemini'de sor</li>
<li>Mention / URL / rakip sütunlarını doldur</li>
<li>Citation rate'i hafta satırına yaz</li>
</ol>
<p>Blog: <a href="https://nefalix.com/blog">nefalix.com/blog</a></p>
<p>— Nefalix GEO</p>
</body></html>"""
    if args.dry_run:
        print(json.dumps({"ok": True, "dry_run": True, "week": week}, ensure_ascii=False))
        return
    to_addrs = [x.strip() for x in args.to.split(",") if x.strip()]
    send_mail(to_addrs, f"Nefalix GEO — Haftalık citation checklist ({week})", body)
    print(json.dumps({"ok": True, "week": week, "to": to_addrs}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
