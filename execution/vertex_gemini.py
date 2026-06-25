#!/usr/bin/env python3
"""Vertex AI Gemini — GCP faturalandırması (trial kredi). OpenAI yerine."""
from __future__ import annotations

import json
import os
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DEFAULT_MODEL = os.environ.get("VERTEX_GEMINI_MODEL", "gemini-2.5-flash")
DEFAULT_REGION = os.environ.get("GCP_REGION", "europe-west1")
DEFAULT_PROJECT = os.environ.get("GCP_PROJECT_ID", "utility-cumulus-484107-v3")

_TOKEN_CACHE: dict[str, object] = {"token": None, "exp": 0}


def _load_service_account() -> dict:
    raw = os.environ.get("GCP_SERVICE_ACCOUNT_JSON", "").strip()
    if raw:
        return json.loads(raw)
    path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")
    if path and Path(path).is_file():
        return json.loads(Path(path).read_text())
    fallback = REPO / ".tmp" / "gcp-service-account.json"
    if fallback.is_file():
        return json.loads(fallback.read_text())
    raise RuntimeError(
        "GCP service account yok — GCP_SERVICE_ACCOUNT_JSON, "
        "GOOGLE_APPLICATION_CREDENTIALS veya .tmp/gcp-service-account.json"
    )


def _access_token(sa: dict | None = None) -> str:
    env_tok = os.environ.get("GCP_ACCESS_TOKEN", "").strip()
    if env_tok:
        return env_tok

    now = int(time.time())
    if _TOKEN_CACHE["token"] and now < int(_TOKEN_CACHE["exp"]) - 60:
        return str(_TOKEN_CACHE["token"])

    if sa is None:
        sa = _load_service_account()

    try:
        import jwt  # type: ignore
    except ImportError:
        key_file = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", str(REPO / ".tmp" / "gcp-service-account.json"))
        if Path(key_file).is_file():
            subprocess.run(
                ["gcloud", "auth", "activate-service-account", "--key-file", key_file],
                check=False,
                capture_output=True,
            )
        return subprocess.check_output(
            ["gcloud", "auth", "print-access-token"],
            text=True,
            timeout=30,
        ).strip()

    iat = now
    exp = iat + 3600
    payload = {
        "iss": sa["client_email"],
        "sub": sa["client_email"],
        "aud": "https://oauth2.googleapis.com/token",
        "iat": iat,
        "exp": exp,
        "scope": "https://www.googleapis.com/auth/cloud-platform",
    }
    assertion = jwt.encode(payload, sa["private_key"], algorithm="RS256")
    body = urllib.parse.urlencode(
        {
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": assertion,
        }
    ).encode()
    req = urllib.request.Request(
        "https://oauth2.googleapis.com/token",
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as res:
        data = json.loads(res.read().decode())
    _TOKEN_CACHE["token"] = data["access_token"]
    _TOKEN_CACHE["exp"] = exp
    return data["access_token"]


def vertex_generate(
    prompt: str,
    *,
    system: str = "Sadece istenen formatta yanıt ver.",
    model: str | None = None,
    temperature: float = 0.4,
    json_mode: bool = False,
    project: str | None = None,
    region: str | None = None,
) -> str:
    """Vertex generateContent — ham metin döner."""
    sa = _load_service_account()
    token = _access_token(sa)
    project = project or DEFAULT_PROJECT
    region = region or DEFAULT_REGION
    model = model or DEFAULT_MODEL
    url = (
        f"https://{region}-aiplatform.googleapis.com/v1/"
        f"projects/{project}/locations/{region}/publishers/google/models/{model}:generateContent"
    )
    generation_config: dict = {"temperature": temperature, "maxOutputTokens": 2048}
    if json_mode:
        generation_config["responseMimeType"] = "application/json"

    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "systemInstruction": {"parts": [{"text": system}]},
        "generationConfig": generation_config,
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as res:
            out = json.loads(res.read().decode())
    except urllib.error.HTTPError as e:
        detail = e.read().decode()[:500]
        raise RuntimeError(f"Vertex {e.code}: {detail}") from e

    parts = out.get("candidates", [{}])[0].get("content", {}).get("parts", [])
    text = "".join(p.get("text", "") for p in parts)
    if not text.strip():
        raise RuntimeError(f"Vertex boş yanıt: {json.dumps(out)[:300]}")
    return text.strip()


def vertex_json(prompt: str, **kwargs) -> dict:
    raw = vertex_generate(prompt, json_mode=True, **kwargs)
    return json.loads(raw)
