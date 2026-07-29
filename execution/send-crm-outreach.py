#!/usr/bin/env python3
"""CRM toplu outreach — Hostinger SMTP (BLOG_SMTP_*).

stdin JSON:
{
  "templateId": "t2",
  "senderKey": "kadir" | "enes",
  "replyTo": "optional@nefalix.com",
  "recipients": [{"email":"a@b.com","name":"Ahmet","firm":"Klinik X"}],
  "customSubject": "optional override (placeholders ok)",
  "customBody": "optional override (placeholders ok)",
  "includeSignature": true,
  "delaySec": 3,
  "maxPerHour": 20
}
stdout: {ok, sent, skipped, errors, results:[...]}
"""
from __future__ import annotations

import json
import os
import re
import smtplib
import ssl
import sys
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TEMPLATES_PATH = ROOT / "outreach-templates.json"
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def load_pack() -> dict:
    return json.loads(TEMPLATES_PATH.read_text(encoding="utf-8"))


def title_short(title: str) -> str:
    if re.search(r"CEO", title or "", re.I):
        return "kurucusu"
    if re.search(r"CTO", title or "", re.I):
        return "kurucu ortağı"
    if re.search(r"İletişim|Iletisim", title or "", re.I):
        return "iletişim ekibinden"
    return "kurucusu"


def strip_text_signature(body: str) -> str:
    """HTML imza varken 'Saygılarımla,' sonrası kişi satırlarını kaldır (çift imza olmasın)."""
    text = (body or "").replace("\r\n", "\n")
    m = re.search(r"(?is)(^|\n)(saygılarımla,?)\s*\n", text)
    if not m:
        return text.rstrip()
    # Keep greeting line, drop everything after it
    keep = text[: m.end()].rstrip()
    return keep


def hitap_suffix(hitap: str) -> str:
    key = str(hitap or "unknown").strip().lower()
    if key in ("bey", "erkek", "male", "m"):
        return " Bey"
    if key in ("hanim", "hanım", "kadin", "kadın", "female", "f"):
        return " Hanım"
    return ""


def apply_hitap(text: str, hitap: str) -> str:
    """Bey/Hanım veya [Hitap] → seçime göre; bilinmiyor = sadece isim."""
    suf = hitap_suffix(hitap)
    out = text or ""
    out = out.replace("[Hitap]", suf)
    # Common template forms
    out = out.replace(" Bey/Hanım", suf)
    out = out.replace("Bey/Hanım", suf.lstrip() if suf else "")
    return out


def fill(text: str, sender: dict, recip: dict) -> str:
    name = recip.get("name") or "[İsim]"
    firm = recip.get("firm") or "[Firma]"
    out = text or ""
    for k, v in {
        "{name}": sender.get("name") or "",
        "{title}": sender.get("title") or "",
        "{titleShort}": title_short(sender.get("title") or ""),
        "{email}": sender.get("email") or "",
        "{phone}": sender.get("phone") or "",
        "{web}": sender.get("web") or "",
        "{calUrl}": sender.get("calUrl") or "https://cal.com/enes-ceylan/15min",
        "[İsim]": name,
        "[Firma]": firm,
    }.items():
        out = out.replace(k, str(v))
    return apply_hitap(out, recip.get("hitap") or "unknown")


def web_href(web: str) -> str:
    w = (web or "www.nefalix.com").strip()
    if re.match(r"^https?://", w, re.I):
        return w
    return "https://" + w.lstrip("/")


def build_signature_html(sender: dict) -> str:
    """iletisim/imza tablosu — renkli marka + kompakt kişi bilgisi."""
    p = sender or {}
    name = escape(str(p.get("name") or "Nefalix"))
    title = escape(str(p.get("title") or ""))
    phone = escape(str(p.get("phone") or ""))
    email = escape(str(p.get("email") or ""))
    web_disp = re.sub(r"^https?://", "", str(p.get("web") or "www.nefalix.com"), flags=re.I)
    web_url = escape(web_href(str(p.get("web") or "www.nefalix.com")))
    address = escape(str(p.get("address") or "Kartal, İstanbul"))
    linkedin = escape(str(p.get("linkedin") or "https://www.linkedin.com/company/nefalixai/"))
    instagram = escape(str(p.get("instagram") or "https://www.instagram.com/nefalixai/"))
    youtube = escape(str(p.get("youtube") or "https://www.youtube.com/@Nefalixai"))
    slogan = escape(
        str(p.get("slogan") or "Müşterinizi anlayın. Deneyimi yönetin. İtibarınızı büyütün.")
    )
    return f"""<table cellpadding="0" cellspacing="0" border="0" role="presentation" style="font-family:Arial,Helvetica,sans-serif; border-collapse:collapse; margin-top:20px;">
  <tr>
    <td valign="middle" style="padding:2px 18px 2px 0;">
      <table cellpadding="0" cellspacing="0" border="0" role="presentation">
        <tr>
          <td valign="middle" style="padding-right:10px;">
            <table cellpadding="0" cellspacing="0" border="0" role="presentation" width="34" style="width:34px;">
              <tr><td height="7" bgcolor="#17727E" style="line-height:7px; font-size:0; border-radius:3px;">&nbsp;</td></tr>
              <tr><td height="4" style="line-height:4px; font-size:0;">&nbsp;</td></tr>
              <tr><td height="7" bgcolor="#0C2A31" style="line-height:7px; font-size:0; border-radius:3px;">&nbsp;</td></tr>
              <tr><td height="4" style="line-height:4px; font-size:0;">&nbsp;</td></tr>
              <tr><td height="7" bgcolor="#E8734A" style="line-height:7px; font-size:0; border-radius:3px;">&nbsp;</td></tr>
            </table>
          </td>
          <td valign="middle">
            <div style="font-size:20px; font-weight:bold; letter-spacing:2.5px; color:#17727E;">NEFALIX</div>
            <div style="font-size:10px; color:#5E7075; letter-spacing:.4px; margin-top:2px;">Experience Intelligence Platform</div>
          </td>
        </tr>
      </table>
    </td>
    <td width="1" bgcolor="#DDE7E7" style="width:1px; line-height:1px; font-size:0;">&nbsp;</td>
    <td valign="middle" style="padding:2px 0 2px 18px; color:#33474C;">
      <div style="font-size:15px; font-weight:bold; color:#0C2A31;">{name}</div>
      <div style="font-size:12.5px; font-weight:bold; color:#17727E; padding-bottom:6px;">{title}</div>
      <div style="font-size:12.5px; padding:1px 0;"><span style="color:#17727E; font-weight:bold;">M</span>&nbsp;&nbsp;{phone}</div>
      <div style="font-size:12.5px; padding:1px 0;"><span style="color:#17727E; font-weight:bold;">E</span>&nbsp;&nbsp;<a href="mailto:{email}" style="color:#33474C; text-decoration:none;">{email}</a></div>
      <div style="font-size:12.5px; padding:1px 0;"><span style="color:#17727E; font-weight:bold;">W</span>&nbsp;&nbsp;<a href="{web_url}" style="color:#33474C; text-decoration:none;">{escape(web_disp)}</a></div>
      <div style="font-size:12.5px; padding:1px 0;"><span style="color:#17727E; font-weight:bold;">A</span>&nbsp;&nbsp;{address}</div>
      <div style="font-size:12px; font-weight:bold; padding-top:7px;">
        <a href="{linkedin}" style="color:#17727E; text-decoration:none;">LinkedIn</a>&nbsp;&nbsp;·&nbsp;&nbsp;
        <a href="{instagram}" style="color:#17727E; text-decoration:none;">Instagram</a>&nbsp;&nbsp;·&nbsp;&nbsp;
        <a href="{youtube}" style="color:#17727E; text-decoration:none;">YouTube</a>
      </div>
    </td>
  </tr>
  <tr>
    <td colspan="3" style="padding-top:12px;">
      <div style="border-top:1px solid #DDE7E7; padding-top:8px; font-size:11px; color:#5E7075;">{slogan}</div>
    </td>
  </tr>
</table>"""


def build_signature_plain(sender: dict) -> str:
    p = sender or {}
    web = re.sub(r"^https?://", "", str(p.get("web") or "www.nefalix.com"), flags=re.I)
    lines = [
        "",
        "--",
        str(p.get("name") or "Nefalix"),
        str(p.get("title") or ""),
        str(p.get("phone") or ""),
        str(p.get("email") or ""),
        web,
        str(p.get("address") or "Kartal, İstanbul"),
    ]
    return "\n".join(x for i, x in enumerate(lines) if i < 2 or x)


def body_to_html(plain: str, signature_html: str = "", style: str = "personal") -> str:
    """style=personal → sade HTML (Gmail Birincil şansı daha yüksek).
    style=branded → teal kart (görsel güzel, Tanıtımlar riski yüksek).
    """
    paras = [p.strip() for p in plain.replace("\r\n", "\n").split("\n\n") if p.strip()]
    if not paras:
        paras = [plain.strip() or ""]
    blocks = "".join(
        f'<p style="margin:0 0 1em;font-size:14px;line-height:1.5;color:#222">'
        f'{escape(p).replace(chr(10), "<br>")}</p>'
        for p in paras
    )
    sig = ""
    if signature_html:
        sig = f'<div style="margin-top:16px">{signature_html}</div>'

    style = (style or "personal").strip().lower()
    if style in ("branded", "marka", "card"):
        return f"""<!DOCTYPE html><html><body style="margin:0;padding:0;background:#E9F0F0;font-family:Arial,Helvetica,sans-serif">
<div style="max-width:640px;margin:24px auto;background:#fff;border:1px solid #DDE7E7;border-radius:12px;overflow:hidden">
  <div style="padding:22px 28px;background:linear-gradient(135deg,#0E4A52,#17727E);color:#fff">
    <div style="font-size:18px;font-weight:700;letter-spacing:.12em">NEFALIX</div>
    <div style="font-size:12px;opacity:.9;margin-top:4px">Experience Intelligence Platform</div>
  </div>
  <div style="padding:22px 28px">{blocks}{sig}</div>
  <div style="padding:14px 28px 22px;font-size:11.5px;color:#5E7075;border-top:1px solid #DDE7E7">
    www.nefalix.com
  </div>
</div></body></html>"""

    # personal — newsletter/kart sinyali yok
    return (
        "<!DOCTYPE html><html><body style=\"margin:0;padding:12px 8px;"
        "font-family:Arial,Helvetica,sans-serif;color:#222;background:#fff\">"
        f"{blocks}{sig}</body></html>"
    )


def resolve_smtp_creds(from_addr: str) -> tuple[str, int, str, str, str]:
    """Gönderen adresine göre SMTP oturumu — Hostinger alias spoof kabul etmez."""
    host = os.environ.get("BLOG_SMTP_HOST", "smtp.hostinger.com")
    port = int(os.environ.get("BLOG_SMTP_PORT", "465"))
    addr = (from_addr or "").strip().lower()
    default_user = os.environ.get("BLOG_SMTP_USER", "info@nefalix.com")
    default_pass = os.environ.get("BLOG_SMTP_PASSWORD", "")
    default_from = os.environ.get("BLOG_SMTP_FROM", default_user)

    profiles = {
        "info@nefalix.com": (
            os.environ.get("BLOG_SMTP_USER", "info@nefalix.com"),
            os.environ.get("BLOG_SMTP_PASSWORD", ""),
        ),
        "abdulkadir@nefalix.com": (
            os.environ.get("KADIR_SMTP_USER", "abdulkadir@nefalix.com"),
            os.environ.get("KADIR_SMTP_PASSWORD", ""),
        ),
        "enes@nefalix.com": (
            os.environ.get("ENES_SMTP_USER", "enes@nefalix.com"),
            os.environ.get("ENES_SMTP_PASSWORD", ""),
        ),
    }
    if addr in profiles:
        user, password = profiles[addr]
        if not password:
            label = "BLOG" if "info@" in addr else ("KADIR" if "abdulkadir" in addr else "ENES")
            raise RuntimeError(
                f"{addr} için SMTP şifresi eksik — VPS .env içine {label}_SMTP_PASSWORD ekleyin"
            )
        return host, port, user, password, addr or user

    if not default_pass:
        raise RuntimeError("BLOG_SMTP_PASSWORD eksik")
    return host, port, default_user, default_pass, addr or default_from


def send_one(
    to_addr: str,
    subject: str,
    plain: str,
    html: str,
    reply_to: str,
    from_name: str = "Nefalix",
    from_email: str = "",
) -> None:
    default_from = os.environ.get("BLOG_SMTP_FROM", os.environ.get("BLOG_SMTP_USER", "info@nefalix.com"))
    from_addr = (from_email or "").strip() or default_from
    host, port, user, password, envelope_from = resolve_smtp_creds(from_addr)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    safe_name = (from_name or "Nefalix").replace('"', "")
    msg["From"] = f'"{safe_name}" <{from_addr}>'
    msg["To"] = to_addr
    if reply_to:
        msg["Reply-To"] = reply_to
    msg.attach(MIMEText(plain, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))

    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL(host, port, context=ctx) as smtp:
        smtp.login(user, password)
        smtp.sendmail(envelope_from, [to_addr], msg.as_string())


def run_payload(payload: dict) -> dict:
    pack = load_pack()
    templates = {t["id"]: t for t in pack.get("templates") or []}
    senders = pack.get("senders") or {}

    tid = str(payload.get("templateId") or "").strip()
    tpl = templates.get(tid)
    if not tpl or tpl.get("channel") != "E-posta":
        raise RuntimeError("geçersiz templateId (e-posta şablonu gerekli)")

    sender_key = str(payload.get("senderKey") or "kadir").strip().lower()
    if sender_key in ("abdulkadir", "ak", "ay", "admin"):
        sender_key = "kadir"
    if sender_key in ("ec", "en"):
        sender_key = "enes"
    if sender_key in ("kader", "kh", "kd"):
        sender_key = "kader"
    sender = senders.get(sender_key) or senders.get("kadir")
    if not sender:
        raise RuntimeError("sender bulunamadı")

    reply_to = str(payload.get("replyTo") or sender.get("email") or "").strip()
    recipients = payload.get("recipients") or []
    if not isinstance(recipients, list):
        raise RuntimeError("recipients liste olmalı")
    if len(recipients) > 50:
        raise RuntimeError("en fazla 50 alıcı")

    delay = float(payload.get("delaySec") if payload.get("delaySec") is not None else 3)
    max_per_hour = int(payload.get("maxPerHour") if payload.get("maxPerHour") is not None else 20)
    if delay < 0:
        delay = 0
    if max_per_hour < 1:
        max_per_hour = 1

    results: list[dict] = []
    sent = skipped = errors = 0
    to_send: list[dict] = []

    for i, r in enumerate(recipients):
        if not isinstance(r, dict):
            results.append({"index": i, "status": "skipped", "reason": "geçersiz satır"})
            skipped += 1
            continue
        email = str(r.get("email") or "").strip().lower()
        if not email or not EMAIL_RE.match(email):
            results.append(
                {
                    "index": i,
                    "status": "skipped",
                    "email": email,
                    "firm": r.get("firm") or "",
                    "reason": "e-posta yok veya geçersiz",
                }
            )
            skipped += 1
            continue
        to_send.append({"index": i, **r, "email": email})

    if len(to_send) > max_per_hour:
        for r in to_send[max_per_hour:]:
            results.append(
                {
                    "index": r["index"],
                    "status": "skipped",
                    "email": r["email"],
                    "firm": r.get("firm") or "",
                    "reason": f"saatlik limit ({max_per_hour})",
                }
            )
            skipped += 1
        to_send = to_send[:max_per_hour]

    subj_src = (
        str(payload["customSubject"])
        if payload.get("customSubject") is not None
        else (tpl.get("subject") or "")
    )
    body_src = (
        str(payload["customBody"])
        if payload.get("customBody") is not None
        else (tpl.get("body") or "")
    )
    if not str(subj_src).strip():
        raise RuntimeError("konu boş")
    if not str(body_src).strip():
        raise RuntimeError("metin boş")

    include_sig = payload.get("includeSignature")
    if include_sig is None:
        include_sig = True
    include_sig = bool(include_sig)
    mail_style = str(payload.get("mailStyle") or "personal").strip().lower()
    if mail_style not in ("personal", "branded", "marka", "card"):
        mail_style = "personal"
    if mail_style in ("marka", "card"):
        mail_style = "branded"
    # From = seçilen profilin e-postası (enes@ / abdulkadir@ / info@)
    from_email = str(sender.get("email") or reply_to or "").strip()
    actual_from = from_email or os.environ.get("BLOG_SMTP_FROM", "info@nefalix.com")
    sig_html = build_signature_html(sender) if include_sig else ""
    sig_plain = build_signature_plain(sender) if include_sig else ""

    for j, r in enumerate(to_send):
        # Zorunlu alanlar — placeholder kalmasın
        name = str(r.get("name") or "").strip()
        firm = str(r.get("firm") or "").strip()
        if not name or not firm:
            results.append(
                {
                    "index": r["index"],
                    "status": "skipped",
                    "email": r["email"],
                    "firm": firm,
                    "name": name,
                    "reason": "isim ve firma zorunlu",
                }
            )
            skipped += 1
            continue
        subject = fill(subj_src, sender, r)
        body = fill(body_src, sender, r)
        if include_sig:
            body = strip_text_signature(body)
        # Hâlâ placeholder kaldıysa gönderme
        if "[İsim]" in subject or "[İsim]" in body or "[Firma]" in subject or "[Firma]" in body:
            results.append(
                {
                    "index": r["index"],
                    "status": "skipped",
                    "email": r["email"],
                    "firm": firm,
                    "name": name,
                    "reason": "isim/firma placeholder doldurulmadı",
                }
            )
            skipped += 1
            continue
        plain = body + sig_plain if sig_plain else body
        html = body_to_html(body, sig_html, style=mail_style)
        try:
            send_one(
                r["email"],
                subject,
                plain,
                html,
                reply_to,
                from_name=str(sender.get("name") or "Nefalix"),
                from_email=from_email,
            )
            results.append(
                {
                    "index": r["index"],
                    "status": "ok",
                    "email": r["email"],
                    "firm": r.get("firm") or "",
                    "name": r.get("name") or "",
                    "subject": subject,
                }
            )
            sent += 1
        except Exception as exc:  # noqa: BLE001
            results.append(
                {
                    "index": r["index"],
                    "status": "error",
                    "email": r["email"],
                    "firm": r.get("firm") or "",
                    "reason": str(exc),
                }
            )
            errors += 1
        if j < len(to_send) - 1 and delay > 0:
            time.sleep(delay)

    results.sort(key=lambda x: x.get("index", 0))
    return {
        "ok": errors == 0,
        "templateId": tid,
        "senderKey": sender_key,
        "from": actual_from,
        "replyTo": reply_to,
        "includeSignature": include_sig,
        "mailStyle": mail_style,
        "sent": sent,
        "skipped": skipped,
        "errors": errors,
        "results": results,
    }


def run_job(job_id: str) -> None:
    jobs = ROOT.parent / ".tmp" / "outreach-jobs"
    # ROOT is execution/; parent is /opt/nefalix
    job_path = jobs / f"{job_id}.json"
    if not job_path.exists():
        raise SystemExit(f"job yok: {job_id}")
    # Load .env if SMTP missing (Popen edge cases)
    env_path = ROOT.parent / ".env"
    if env_path.exists() and not os.environ.get("BLOG_SMTP_PASSWORD"):
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            k, v = k.strip(), v.strip().strip('"').strip("'")
            if k and k not in os.environ:
                os.environ[k] = v
    job = json.loads(job_path.read_text(encoding="utf-8"))
    job["status"] = "running"
    job_path.write_text(json.dumps(job, ensure_ascii=False), encoding="utf-8")
    try:
        result = run_payload(job.get("payload") or {})
        job["status"] = "done"
        job["result"] = result
        job["error"] = None
    except Exception as exc:  # noqa: BLE001
        job["status"] = "error"
        job["error"] = str(exc)
        job["result"] = None
    job_path.write_text(json.dumps(job, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"jobId": job_id, "status": job["status"], "sent": (job.get("result") or {}).get("sent")}, ensure_ascii=False), flush=True)


def main() -> None:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--job-id", default="")
    args = ap.parse_args()
    if args.job_id:
        run_job(args.job_id)
        return

    raw = sys.stdin.read() if not sys.stdin.isatty() else "{}"
    try:
        payload = json.loads(raw or "{}")
    except json.JSONDecodeError as exc:
        print(json.dumps({"ok": False, "error": f"invalid json: {exc}"}, ensure_ascii=False))
        sys.exit(1)
    try:
        out = run_payload(payload)
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        sys.exit(1)
    print(json.dumps(out, ensure_ascii=False))
    if out.get("errors") and out.get("sent") == 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
