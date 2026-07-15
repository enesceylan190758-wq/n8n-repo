#!/usr/bin/env python3
"""Minimal VPS webhook — onay sonrası social-publish-approved.py çalıştırır.

Usage (systemd / docker):
  python3 execution/social-publish-webhook.py

POST /publish
  Header: X-Nefalix-Internal-Key
  Body: {"post_id": "uuid"} veya {"token": "approval_token"}
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
PORT = int(os.environ.get("SOCIAL_WEBHOOK_PORT", "8791"))


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write(f"[social-webhook] {self.address_string()} - {fmt % args}\n")

    def _auth_ok(self) -> bool:
        expected = os.environ.get("NEFALIX_INTERNAL_KEY", "")
        got = self.headers.get("X-Nefalix-Internal-Key", "")
        return bool(expected) and got == expected

    def _json(self, code: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        path = urlparse(self.path).path.rstrip("/") or "/"
        if not self._auth_ok():
            self._json(401, {"ok": False, "error": "unauthorized"})
            return

        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            data = json.loads(raw.decode() or "{}")
        except json.JSONDecodeError:
            self._json(400, {"ok": False, "error": "invalid json"})
            return

        if path in ("/randevu-mail", "/internal/crm/randevu-mail"):
            self._run_randevu_mail(raw)
            return

        if path not in ("/publish", "/internal/social/publish"):
            self._json(404, {"ok": False, "error": "not found"})
            return

        post_id = data.get("post_id")
        token = data.get("token")
        cmd = [sys.executable, str(ROOT / "execution" / "social-publish-approved.py")]
        if post_id:
            cmd.extend(["--post-id", str(post_id)])
        elif token:
            cmd.extend(["--token", str(token)])
        else:
            self._json(400, {"ok": False, "error": "post_id or token required"})
            return

        try:
            proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=180)
            stdout = proc.stdout.strip()
            stderr = proc.stderr.strip()
            if proc.returncode != 0:
                self._json(500, {"ok": False, "error": stderr or stdout or f"exit {proc.returncode}"})
                return
            try:
                result = json.loads(stdout)
            except json.JSONDecodeError:
                result = {"raw": stdout}
            self._json(200, {"ok": True, **result})
        except subprocess.TimeoutExpired:
            self._json(504, {"ok": False, "error": "publish timeout"})
        except Exception as exc:  # noqa: BLE001
            self._json(500, {"ok": False, "error": str(exc)})

    def _run_randevu_mail(self, raw: bytes) -> None:
        cmd = [sys.executable, str(ROOT / "execution" / "send-crm-randevu-notification.py")]
        try:
            proc = subprocess.run(
                cmd,
                cwd=str(ROOT),
                input=raw.decode() or "{}",
                capture_output=True,
                text=True,
                timeout=60,
            )
            stdout = proc.stdout.strip()
            stderr = proc.stderr.strip()
            if proc.returncode != 0:
                self._json(500, {"ok": False, "error": stderr or stdout or f"exit {proc.returncode}"})
                return
            try:
                result = json.loads(stdout)
            except json.JSONDecodeError:
                result = {"raw": stdout}
            self._json(200, {"ok": True, **result})
        except subprocess.TimeoutExpired:
            self._json(504, {"ok": False, "error": "mail timeout"})
        except Exception as exc:  # noqa: BLE001
            self._json(500, {"ok": False, "error": str(exc)})

    def do_GET(self) -> None:
        if urlparse(self.path).path in ("/health", "/internal/social/health", "/internal/crm/health"):
            self._json(200, {"ok": True, "service": "social-publish-webhook"})
            return
        self._json(404, {"ok": False})


def main() -> None:
    if not os.environ.get("NEFALIX_INTERNAL_KEY"):
        raise SystemExit("NEFALIX_INTERNAL_KEY eksik")
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print(json.dumps({"ok": True, "listening": PORT}), flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
