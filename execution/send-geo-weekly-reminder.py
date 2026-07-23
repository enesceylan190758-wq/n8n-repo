#!/usr/bin/env python3
"""Pazar GEO citation hatırlatması — DB'den eksik skor + 25 prompt listesi.

  python3 execution/send-geo-weekly-reminder.py
  python3 execution/send-geo-weekly-reminder.py --dry-run
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import smtplib
import ssl
import sys
import urllib.error
import urllib.request
from datetime import date, datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_NOTIFY_TO = "enes.ceylan190758@gmail.com,akadirysr@gmail.com"
ENGINES = ("chatgpt", "perplexity", "gemini")
EXPECTED = 25 * len(ENGINES)
BASELINE = ROOT / "docs" / "geo-prompt-baseline.md"


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


def sb_base() -> str:
    base = os.environ.get("SUPABASE_URL", "http://127.0.0.1:54321").rstrip("/")
    if "host.docker.internal" in base:
        base = "http://127.0.0.1:54321"
    return base


def fetch_scored_count(week_monday: str) -> tuple[int, int | None]:
    """Returns (scored_rows, missing_or_none_if_unavailable)."""
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not key:
        return 0, None
    url = (
        f"{sb_base()}/rest/v1/geo_citation_scores"
        f"?select=id,prompt_id,engine&week=eq.{week_monday}"
    )
    req = urllib.request.Request(
        url, headers={"apikey": key, "Authorization": f"Bearer {key}"}
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            rows = json.loads(resp.read().decode() or "[]")
    except urllib.error.HTTPError:
        return 0, None
    except Exception:
        return 0, None
    if not isinstance(rows, list):
        return 0, None
    pairs = {(str(r.get("prompt_id")), str(r.get("engine"))) for r in rows}
    return len(pairs), max(0, EXPECTED - len(pairs))


def load_prompts() -> list[tuple[str, str, str]]:
    """Parse baseline table → (id, bucket, prompt)."""
    if not BASELINE.exists():
        return []
    text = BASELINE.read_text(encoding="utf-8")
    out: list[tuple[str, str, str]] = []
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cols = [c.strip() for c in line.strip("|").split("|")]
        if len(cols) < 3:
            continue
        if not re.match(r"^\d+$", cols[0]):
            continue
        out.append((cols[0], cols[1], cols[2]))
    return out


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

    today = datetime.now(timezone.utc).astimezone().date()
    week_monday = (today - __import__("datetime").timedelta(days=today.weekday())).isoformat()
    iso_label = today.strftime("%Y-W%W")
    scored, missing = fetch_scored_count(week_monday)
    prompts = load_prompts()

    missing_label = "DB erişilemedi" if missing is None else str(missing)
    prompt_lis = "\n".join(
        f"<li><strong>#{html.escape(pid)}</strong> [{html.escape(bucket)}] "
        f"{html.escape(prompt)}</li>"
        for pid, bucket, prompt in prompts[:25]
    ) or "<li>(baseline tablosu okunamadı)</li>"

    body = f"""<!DOCTYPE html>
<html><body style="font-family:system-ui,sans-serif;max-width:640px;color:#0f172a;">
<p>Haftalık GEO citation ölçümü ({html.escape(iso_label)} / week={html.escape(week_monday)}).</p>
<p><strong>Bu hafta skorlanacak:</strong> 25 prompt × 3 motor = {EXPECTED} satır.<br>
<strong>DB'de kayıtlı:</strong> {scored}<br>
<strong>Eksik satır:</strong> {html.escape(missing_label)}</p>
<ol>
<li>25 prompt'u ChatGPT / Perplexity / Gemini'de sor</li>
<li><code>execution/record-geo-citation.py</code> ile satır ekle (veya CSV import)</li>
<li>Özet: <code>execution/report-geo-citation.py --week {html.escape(week_monday)} --format md</code></li>
<li><code>docs/geo-prompt-baseline.md</code> yalnızca şablon; kaynak skorlar DB</li>
</ol>
<p><strong>25 prompt</strong></p>
<ol>{prompt_lis}</ol>
<p>Public: <a href="https://nefalix.com/geo">nefalix.com/geo</a> · Blog: <a href="https://nefalix.com/blog">nefalix.com/blog</a></p>
<p>— Nefalix GEO</p>
</body></html>"""

    payload = {
        "ok": True,
        "week": week_monday,
        "iso": iso_label,
        "expected_rows": EXPECTED,
        "scored_rows": scored,
        "missing_rows": missing,
        "prompt_count": len(prompts),
    }
    if args.dry_run:
        payload["dry_run"] = True
        print(json.dumps(payload, ensure_ascii=False))
        return

    to_addrs = [x.strip() for x in args.to.split(",") if x.strip()]
    send_mail(
        to_addrs,
        f"Nefalix GEO — 25 prompt / eksik {missing_label} ({iso_label})",
        body,
    )
    payload["to"] = to_addrs
    print(json.dumps(payload, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
