#!/usr/bin/env python3
"""Upload social post package to Google Drive (+ local fallback).

Creates folder: YYYY-MM-DD_post_XX_slug/
  - image.png
  - caption.txt  (caption + hashtags, Instagram planlayıcıya yapıştır)

Usage:
  python3 execution/social-upload-drive.py --post-id <uuid>
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "execution"))

from vertex_gemini import _load_service_account  # noqa: E402

DRIVE_SCOPE = "https://www.googleapis.com/auth/drive.file"
LOCAL_DIR = REPO / ".tmp" / "social-ready"


def sb(method: str, path: str, body: dict | None = None) -> list | dict:
    base = os.environ.get("SUPABASE_URL", "http://127.0.0.1:54321").rstrip("/")
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
    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = resp.read().decode()
        return json.loads(raw) if raw.strip() else {}


def drive_token() -> str:
    try:
        import jwt  # type: ignore
    except ImportError as e:
        raise RuntimeError("PyJWT gerekli: pip install PyJWT cryptography") from e

    sa = _load_service_account()
    now = int(time.time())
    payload = {
        "iss": sa["client_email"],
        "sub": sa["client_email"],
        "aud": "https://oauth2.googleapis.com/token",
        "iat": now,
        "exp": now + 3600,
        "scope": DRIVE_SCOPE,
    }
    assertion = jwt.encode(payload, sa["private_key"], algorithm="RS256")
    body = urllib.parse.urlencode({
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "assertion": assertion,
    }).encode()
    req = urllib.request.Request(
        "https://oauth2.googleapis.com/token",
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as res:
        return json.loads(res.read().decode())["access_token"]


def drive_upload(token: str, parent_id: str, name: str, content: bytes, mime: str) -> str:
    meta = json.dumps({"name": name, "parents": [parent_id]}).encode()
    msg = MIMEMultipart("related")
    msg.attach(MIMEText(meta.decode(), "json", "utf-8"))
    part = MIMEApplication(content)
    part.add_header("Content-Type", mime)
    msg.attach(part)
    body = msg.as_bytes()
    req = urllib.request.Request(
        "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&fields=id,webViewLink",
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": f'multipart/related; boundary="{msg.get_boundary()}"',
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode())
    return data.get("webViewLink") or data.get("id", "")


def drive_mkdir(token: str, parent_id: str, name: str) -> str:
    body = json.dumps({"name": name, "mimeType": "application/vnd.google-apps.folder", "parents": [parent_id]}).encode()
    req = urllib.request.Request(
        "https://www.googleapis.com/drive/v3/files?fields=id,webViewLink",
        data=body,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode())
    return data["id"]


def build_caption_text(post: dict, template: dict) -> str:
    caption = (post.get("caption") or "").strip()
    hashtags = (post.get("hashtags") or "").strip()
    slug = (template.get("slug") or "post").strip()
    num = template.get("post_number", "?")
    lines = [
        f"NefalixAI — Post {num}/10",
        f"Şablon: {slug}",
        f"Üretim: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "=== INSTAGRAM CAPTION (kopyala-yapıştır) ===",
        "",
        caption,
        "",
        hashtags,
        "",
        "=== NOT ===",
        "Görseli Instagram planlayıcıya yükle, caption'ı yapıştır.",
        "Tel no ekleme. Mail: nefalixai@gmail.com",
    ]
    return "\n".join(lines)


def save_local(package_dir: Path, image_path: Path, caption_text: str) -> str:
    package_dir.mkdir(parents=True, exist_ok=True)
    dest_img = package_dir / "image.png"
    dest_img.write_bytes(image_path.read_bytes())
    (package_dir / "caption.txt").write_text(caption_text, encoding="utf-8")
    return str(package_dir)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--post-id", required=True)
    args = parser.parse_args()

    rows = sb("GET", f"social_posts?id=eq.{args.post_id}&select=*,social_post_templates(*)&limit=1")
    if not rows:
        raise SystemExit("Post bulunamadı")
    post = rows[0]
    template = post.get("social_post_templates") or {}
    image_path = Path(post.get("image_path") or "")
    if not image_path.is_file():
        raise SystemExit(f"Görsel yok: {image_path}")

    slug = template.get("slug", "post")
    num = template.get("post_number", 0)
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    package_name = f"{date}_post_{num:02d}_{slug}"
    caption_text = build_caption_text(post, template)

    # Her zaman local kaydet
    local_path = save_local(LOCAL_DIR / package_name, image_path, caption_text)

    drive_folder_id = os.environ.get("SOCIAL_DRIVE_FOLDER_ID", "").strip()
    drive_links: dict = {}

    if drive_folder_id:
        try:
            token = drive_token()
            sub_id = drive_mkdir(token, drive_folder_id, package_name)
            drive_links["image"] = drive_upload(token, sub_id, "image.png", image_path.read_bytes(), "image/png")
            drive_links["caption"] = drive_upload(
                token, sub_id, "caption.txt", caption_text.encode("utf-8"), "text/plain"
            )
            drive_links["folder_id"] = sub_id
        except Exception as e:  # noqa: BLE001
            drive_links["error"] = str(e)
            print(f"Drive uyarı: {e}", file=sys.stderr)
    else:
        drive_links["skipped"] = "SOCIAL_DRIVE_FOLDER_ID yok — sadece local: " + local_path

    meta = post.get("metadata") or {}
    if isinstance(meta, str):
        meta = json.loads(meta)
    sb("PATCH", f"social_posts?id=eq.{args.post_id}", {
        "status": "ready",
        "metadata": {
            **meta,
            "delivery": "drive",
            "local_path": local_path,
            "drive": drive_links,
            "package_name": package_name,
        },
        "updated_at": datetime.now(timezone.utc).isoformat(),
    })

    print(json.dumps({
        "ok": True,
        "post_id": args.post_id,
        "package_name": package_name,
        "local_path": local_path,
        "drive": drive_links,
        "status": "ready",
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
