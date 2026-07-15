#!/usr/bin/env python3
"""Sosyal medya bildirimi — e-posta (+ görsel eki) + isteğe bağlı WhatsApp.

Varsayılan: manuel paylaşım paketi (görsel eki + kopyala-yapıştır metin).
"""
from __future__ import annotations

import argparse
import html
import json
import os
import smtplib
import ssl
import urllib.error
import urllib.parse
import urllib.request
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path


def sb_get_post(post_id: str) -> dict:
    base = os.environ.get("SUPABASE_URL", "http://127.0.0.1:54321").rstrip("/")
    if "host.docker.internal" in base:
        base = "http://127.0.0.1:54321"
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not key:
        raise RuntimeError("SUPABASE_SERVICE_ROLE_KEY eksik")
    url = (
        f"{base}/rest/v1/social_posts?id=eq.{post_id}"
        "&select=*,social_post_templates(slug,post_number,eyebrow)&limit=1"
    )
    req = urllib.request.Request(
        url,
        headers={"apikey": key, "Authorization": f"Bearer {key}"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        rows = json.loads(resp.read().decode())
    if not rows:
        raise RuntimeError(f"Post bulunamadı: {post_id}")
    return rows[0]


def instagram_text(post: dict) -> str:
    caption = (post.get("caption") or "").strip()
    hashtags = (post.get("hashtags") or "").strip()
    if hashtags and hashtags not in caption:
        return f"{caption}\n\n{hashtags}".strip()
    return caption


def build_manual_html(post: dict, has_attachment: bool) -> str:
    template = post.get("social_post_templates") or {}
    num = template.get("post_number", "?")
    title = html.escape(post.get("headline") or template.get("eyebrow") or "Nefalix Sosyal Post")
    full_text = html.escape(instagram_text(post))
    img_note = (
        "<p style='color:#0d9488;font-weight:600;'>📎 Görsel bu mailde <strong>instagram-post.png</strong> eki olarak geldi.</p>"
        if has_attachment
        else "<p><em>Görsel eki yok — sunucudaki dosyayı kontrol edin.</em></p>"
    )
    return f"""<!DOCTYPE html>
<html><body style="font-family:system-ui,sans-serif;color:#0f172a;max-width:560px;">
<p>Merhaba,</p>
<p>Bugünkü <strong>Instagram + LinkedIn</strong> paylaşımın hazır. Aşağıdaki metni kopyala, görseli ektan al, ~2 dk'da paylaş.</p>
<p style="color:#64748b;font-size:13px;">Post {num}/10 · {html.escape(template.get('slug', ''))}</p>
<h2 style="font-size:18px;margin:16px 0 8px;">{title}</h2>
{img_note}
<p style="font-size:13px;color:#64748b;margin:20px 0 8px;">Kopyala → Instagram / LinkedIn'e yapıştır:</p>
<div style="background:#f1f5f9;border:1px solid #e2e8f0;border-radius:12px;padding:16px;white-space:pre-wrap;font-size:14px;line-height:1.55;color:#334155;">{full_text}</div>
<ol style="color:#475569;font-size:14px;line-height:1.7;padding-left:20px;">
  <li>Mail ekinden <strong>instagram-post.png</strong> indir (veya telefonda kaydet)</li>
  <li>Instagram → + → görseli seç</li>
  <li>Yukarıdaki metni yapıştır → Paylaş</li>
  <li>LinkedIn şirket sayfasında aynı görsel + metin</li>
</ol>
<p style="color:#64748b;font-size:12px;">Otomatik API yayını kapalı — token gerekmez.</p>
<p>— Nefalix otomasyon</p>
</body></html>"""


def build_auto_html(post: dict, approve_url: str, reject_url: str) -> str:
    template = post.get("social_post_templates") or {}
    title = html.escape(post.get("headline") or template.get("eyebrow") or "Nefalix Sosyal Post")
    caption = html.escape((post.get("caption") or "")[:600])
    hashtags = html.escape(post.get("hashtags") or "")
    img = post.get("image_url") or ""
    img_block = (
        f'<img src="{html.escape(img)}" alt="" style="max-width:100%;border-radius:12px;margin:16px 0;" />'
        if img
        else ""
    )
    return f"""<!DOCTYPE html>
<html><body style="font-family:system-ui,sans-serif;color:#0f172a;max-width:560px;">
<p>Bugünkü paylaşım hazır. Onaylarsanız otomatik yayınlanır.</p>
<h2 style="font-size:18px;">{title}</h2>
{img_block}
<p style="white-space:pre-wrap;">{caption}</p>
<p style="color:#64748b;">{hashtags}</p>
<p><a href="{html.escape(approve_url)}">Onayla</a> · <a href="{html.escape(reject_url)}">Reddet</a></p>
</body></html>"""


def send_email(
    to_addrs: list[str],
    subject: str,
    html_body: str,
    plain_body: str,
    image_path: Path | None,
) -> None:
    host = os.environ.get("BLOG_SMTP_HOST", "smtp.hostinger.com")
    port = int(os.environ.get("BLOG_SMTP_PORT", "465"))
    user = os.environ.get("BLOG_SMTP_USER", "info@nefalix.com")
    password = os.environ.get("BLOG_SMTP_PASSWORD", "")
    from_addr = os.environ.get("BLOG_SMTP_FROM", user)
    if not password:
        raise RuntimeError("BLOG_SMTP_PASSWORD eksik")

    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"] = f"Nefalix Sosyal <{from_addr}>"
    msg["To"] = ", ".join(to_addrs)

    alt = MIMEMultipart("alternative")
    alt.attach(MIMEText(plain_body, "plain", "utf-8"))
    alt.attach(MIMEText(html_body, "html", "utf-8"))
    msg.attach(alt)

    if image_path and image_path.is_file():
        img = MIMEImage(image_path.read_bytes(), _subtype="png")
        img.add_header("Content-Disposition", "attachment", filename="instagram-post.png")
        msg.attach(img)

    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL(host, port, context=ctx) as smtp:
        smtp.login(user, password)
        smtp.sendmail(from_addr, to_addrs, msg.as_string())


def send_whatsapp(text: str) -> bool:
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--post-id", required=True)
    parser.add_argument("--to", default="enes.ceylan190758@gmail.com,akadirysr@gmail.com")
    parser.add_argument("--subject", help="Özel mail konusu (A/B test için)")
    parser.add_argument(
        "--mode",
        choices=["manual", "auto"],
        default=os.environ.get("SOCIAL_DELIVERY", "manual"),
    )
    args = parser.parse_args()

    post = sb_get_post(args.post_id)
    template = post.get("social_post_templates") or {}
    slug = template.get("slug", "post")
    num = template.get("post_number", "?")
    image_path = Path(post.get("image_path") or "")
    full_text = instagram_text(post)

    if args.mode == "auto":
        token = post.get("approval_token", "")
        base = os.environ.get("SOCIAL_APPROVE_BASE_URL", "https://nefalix.com/api/social").rstrip("/")
        approve_url = f"{base}/approve?token={urllib.parse.quote(token)}"
        reject_url = f"{base}/reject?token={urllib.parse.quote(token)}"
        subject = f"Nefalix Sosyal — Onay bekliyor ({slug})"
        html_body = build_auto_html(post, approve_url, reject_url)
        plain_body = f"Onayla: {approve_url}\n\n{full_text}"
        wa_text = f"Nefalix sosyal onay ({slug})\n{approve_url}"
    else:
        subject = args.subject or f"Nefalix Sosyal — Post {num}/10 hazır (Instagram + LinkedIn)"
        html_body = build_manual_html(post, image_path.is_file())
        plain_body = (
            f"Nefalix sosyal post {num}/10 ({slug})\n\n"
            f"Görsel: mail eki instagram-post.png\n\n"
            f"--- Kopyala yapıştır ---\n\n{full_text}\n"
        )
        wa_text = f"Nefalix sosyal post {num}/10 hazır.\n\n{full_text[:900]}"

    to_addrs = [x.strip() for x in args.to.split(",") if x.strip()]
    send_email(to_addrs, subject, html_body, plain_body, image_path if args.mode == "manual" else None)
    wa_ok = send_whatsapp(wa_text)

    print(json.dumps({
        "ok": True,
        "mode": args.mode,
        "post_id": args.post_id,
        "to": to_addrs,
        "attachment": image_path.is_file(),
        "whatsapp": wa_ok,
        "slug": slug,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
