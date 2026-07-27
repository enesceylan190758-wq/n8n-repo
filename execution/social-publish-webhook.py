#!/usr/bin/env python3
"""Minimal VPS webhook — social publish + CRM mail (randevu / outreach).

POST /publish | /internal/social/publish
POST /randevu-mail | /internal/crm/randevu-mail
POST /outreach-mail | /internal/crm/outreach-mail  (async job)
GET  /outreach-status?jobId=… | /internal/crm/outreach-status?jobId=…
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent.parent
PORT = int(os.environ.get("SOCIAL_WEBHOOK_PORT", "8791"))
JOBS = ROOT / ".tmp" / "outreach-jobs"


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
            self._run_script("send-crm-randevu-notification.py", raw, 60)
            return

        if path in ("/outreach-mail", "/internal/crm/outreach-mail"):
            self._queue_outreach(data)
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

    def _run_script(self, script: str, raw: bytes, timeout: int) -> None:
        cmd = [sys.executable, str(ROOT / "execution" / script)]
        try:
            proc = subprocess.run(
                cmd,
                cwd=str(ROOT),
                input=raw.decode() or "{}",
                capture_output=True,
                text=True,
                timeout=timeout,
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

    def _queue_outreach(self, data: dict) -> None:
        JOBS.mkdir(parents=True, exist_ok=True)
        job_id = uuid.uuid4().hex[:16]
        job_path = JOBS / f"{job_id}.json"
        job = {
            "jobId": job_id,
            "status": "queued",
            "payload": data,
            "result": None,
            "error": None,
        }
        job_path.write_text(json.dumps(job, ensure_ascii=False), encoding="utf-8")
        cmd = [
            sys.executable,
            str(ROOT / "execution" / "send-crm-outreach.py"),
            "--job-id",
            job_id,
        ]
        try:
            log_path = JOBS / f"{job_id}.log"
            log_f = open(log_path, "ab")  # noqa: SIM115
            subprocess.Popen(
                cmd,
                cwd=str(ROOT),
                stdout=log_f,
                stderr=subprocess.STDOUT,
                start_new_session=True,
                env={**os.environ},
            )
        except Exception as exc:  # noqa: BLE001
            job["status"] = "error"
            job["error"] = str(exc)
            job_path.write_text(json.dumps(job, ensure_ascii=False), encoding="utf-8")
            self._json(500, {"ok": False, "error": str(exc), "jobId": job_id})
            return
        self._json(
            200,
            {
                "ok": True,
                "queued": True,
                "jobId": job_id,
                "status": "queued",
                "recipients": len(data.get("recipients") or []),
                "hint": "Durum için outreach-status?jobId=… poll edin",
            },
        )

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        if path in ("/health", "/internal/social/health", "/internal/crm/health"):
            self._json(200, {"ok": True, "service": "social-publish-webhook"})
            return
        if path in ("/outreach-status", "/internal/crm/outreach-status"):
            if not self._auth_ok():
                self._json(401, {"ok": False, "error": "unauthorized"})
                return
            qs = parse_qs(parsed.query or "")
            job_id = (qs.get("jobId") or qs.get("job_id") or [""])[0].strip()
            if not job_id or not all(c.isalnum() for c in job_id):
                self._json(400, {"ok": False, "error": "jobId gerekli"})
                return
            job_path = JOBS / f"{job_id}.json"
            if not job_path.exists():
                self._json(404, {"ok": False, "error": "job bulunamadı"})
                return
            try:
                job = json.loads(job_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                self._json(500, {"ok": False, "error": "job dosyası bozuk"})
                return
            out = {
                "ok": True,
                "jobId": job_id,
                "status": job.get("status"),
                "error": job.get("error"),
            }
            if job.get("result"):
                out["mail"] = job["result"]
            self._json(200, out)
            return
        self._json(404, {"ok": False})


def main() -> None:
    if not os.environ.get("NEFALIX_INTERNAL_KEY"):
        raise SystemExit("NEFALIX_INTERNAL_KEY eksik")
    JOBS.mkdir(parents=True, exist_ok=True)
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print(json.dumps({"ok": True, "listening": PORT}), flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
