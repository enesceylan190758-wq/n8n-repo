#!/usr/bin/env python3
"""Saha CRM randevu bildirimi — Hostinger SMTP (BLOG_SMTP_*).

stdin veya --json ile payload:
  {
    "event": "created" | "cancelled",
    "clinic": "Klinik adı",
    "tarih": "2026-07-15",
    "saat": "14:00",
    "adres": "...",
    "tel": "...",
    "katilimcilar": ["Abdülkadir Yaşar", "Enes Ceylan"],
    "olusturan": "Kader Hanım",
    "notu": "..."
  }
"""
from __future__ import annotations

import argparse
import json
import os
import smtplib
import ssl
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from html import escape


def send_email(to_addrs: list[str], subject: str, html: str) -> None:
    host = os.environ.get("BLOG_SMTP_HOST", "smtp.hostinger.com")
    port = int(os.environ.get("BLOG_SMTP_PORT", "465"))
    user = os.environ.get("BLOG_SMTP_USER", "info@nefalix.com")
    password = os.environ.get("BLOG_SMTP_PASSWORD", "")
    from_addr = os.environ.get("BLOG_SMTP_FROM", user)
    if not password:
        raise RuntimeError("BLOG_SMTP_PASSWORD eksik")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"Nefalix Saha CRM <{from_addr}>"
    msg["To"] = ", ".join(to_addrs)
    msg.attach(MIMEText(html, "html", "utf-8"))

    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL(host, port, context=ctx) as smtp:
        smtp.login(user, password)
        smtp.sendmail(from_addr, to_addrs, msg.as_string())


def build_html(payload: dict) -> tuple[str, str]:
    event = (payload.get("event") or "created").strip().lower()
    clinic = str(payload.get("clinic") or "Klinik")
    tarih = str(payload.get("tarih") or "")
    saat = str(payload.get("saat") or "")
    adres = str(payload.get("adres") or "—")
    tel = str(payload.get("tel") or "—")
    notu = str(payload.get("notu") or "—")
    olusturan = str(payload.get("olusturan") or "—")
    kats = payload.get("katilimcilar") or []
    if isinstance(kats, str):
        kats = [kats]
    kat_txt = ", ".join(str(x) for x in kats) or "—"

    if event == "cancelled":
        subject = f"[CRM] Randevu iptal: {clinic} · {tarih} {saat}"
        headline = "Randevu iptal edildi"
        color = "#b45309"
    else:
        subject = f"[CRM] Yeni randevu: {clinic} · {tarih} {saat}"
        headline = "Yeni randevu oluşturuldu"
        color = "#0d9488"

    html = f"""<!DOCTYPE html><html><body style="font-family:system-ui,sans-serif;line-height:1.5;color:#0f172a">
<div style="max-width:560px;margin:0 auto;padding:24px">
  <p style="margin:0 0 8px;font-size:12px;letter-spacing:.04em;color:#64748b">NEFALIX SAHA CRM</p>
  <h1 style="margin:0 0 16px;font-size:20px;color:{color}">{escape(headline)}</h1>
  <table style="width:100%;border-collapse:collapse;font-size:14px">
    <tr><td style="padding:6px 0;color:#64748b;width:120px">Klinik</td><td style="padding:6px 0"><b>{escape(clinic)}</b></td></tr>
    <tr><td style="padding:6px 0;color:#64748b">Tarih</td><td style="padding:6px 0"><b>{escape(tarih)} · {escape(saat)}</b></td></tr>
    <tr><td style="padding:6px 0;color:#64748b">Adres</td><td style="padding:6px 0">{escape(adres)}</td></tr>
    <tr><td style="padding:6px 0;color:#64748b">Telefon</td><td style="padding:6px 0">{escape(tel)}</td></tr>
    <tr><td style="padding:6px 0;color:#64748b">Katılımcılar</td><td style="padding:6px 0">{escape(kat_txt)}</td></tr>
    <tr><td style="padding:6px 0;color:#64748b">Oluşturan</td><td style="padding:6px 0">{escape(olusturan)}</td></tr>
    <tr><td style="padding:6px 0;color:#64748b">Not</td><td style="padding:6px 0">{escape(notu)}</td></tr>
  </table>
  <p style="margin:24px 0 0"><a href="https://nefalix.com/crm" style="color:#0d9488">Saha CRM’i aç →</a></p>
</div></body></html>"""
    return subject, html


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", help="Payload JSON string; yoksa stdin")
    ap.add_argument(
        "--to",
        default=os.environ.get("CRM_NOTIFY_TO")
        or os.environ.get("BLOG_NOTIFY_TO")
        or "enes.ceylan190758@gmail.com,akadirysr@gmail.com",
    )
    args = ap.parse_args()
    raw = args.json if args.json else sys.stdin.read()
    try:
        payload = json.loads(raw or "{}")
    except json.JSONDecodeError as exc:
        print(json.dumps({"ok": False, "error": f"invalid json: {exc}"}), flush=True)
        return 1

    to_addrs = [x.strip() for x in str(args.to).split(",") if x.strip()]
    subject, html = build_html(payload)
    send_email(to_addrs, subject, html)
    print(json.dumps({"ok": True, "to": to_addrs, "subject": subject}, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
