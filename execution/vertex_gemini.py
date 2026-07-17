#!/usr/bin/env python3
"""Vertex AI Gemini — GCP faturalandırması (trial kredi). OpenAI yerine."""
from __future__ import annotations

import json
import os
import re
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


def _mint_token_from_sa(sa: dict | None = None) -> str:
    """Service account ile taze access token üret (env token kullanmaz)."""
    now = int(time.time())
    if _TOKEN_CACHE["token"] and now < int(_TOKEN_CACHE["exp"]) - 60:
        return str(_TOKEN_CACHE["token"])

    if sa is None:
        sa = _load_service_account()

    try:
        import jwt  # type: ignore
    except ImportError:
        key_file = os.environ.get(
            "GOOGLE_APPLICATION_CREDENTIALS",
            str(REPO / ".tmp" / "gcp-service-account.json"),
        )
        if Path(key_file).is_file():
            subprocess.run(
                ["gcloud", "auth", "activate-service-account", "--key-file", key_file],
                check=False,
                capture_output=True,
            )
        tok = subprocess.check_output(
            ["gcloud", "auth", "print-access-token"],
            text=True,
            timeout=30,
        ).strip()
        _TOKEN_CACHE["token"] = tok
        _TOKEN_CACHE["exp"] = now + 3500
        return tok

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


def _access_token(sa: dict | None = None, *, prefer_env: bool = False) -> str:
    """Access token.

    Varsayılan: SA JWT ile mint (bayat GCP_ACCESS_TOKEN yüzünden 401 olmaz).
    prefer_env=True yalnızca n8n .env yazımı için refresh script'te kullanılır.
    """
    if prefer_env:
        env_tok = os.environ.get("GCP_ACCESS_TOKEN", "").strip()
        if env_tok:
            return env_tok
    return _mint_token_from_sa(sa)


def _vertex_request(
    url: str,
    payload: dict,
    *,
    sa: dict | None = None,
    timeout: int = 120,
) -> dict:
    """Bearer token ile POST; 401'de env token'ı atıp SA ile bir kez yeniden dene."""
    if sa is None:
        sa = _load_service_account()
    token = _access_token(sa)
    for attempt in range(2):
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
            with urllib.request.urlopen(req, timeout=timeout) as res:
                return json.loads(res.read().decode())
        except urllib.error.HTTPError as e:
            detail = e.read().decode()[:500]
            if e.code == 401 and attempt == 0:
                os.environ.pop("GCP_ACCESS_TOKEN", None)
                _TOKEN_CACHE["token"] = None
                _TOKEN_CACHE["exp"] = 0
                token = _mint_token_from_sa(sa)
                continue
            raise RuntimeError(f"Vertex {e.code}: {detail}") from e
    raise RuntimeError("Vertex 401: token yenileme sonrası de başarısız")


def parse_json_relaxed(raw: str) -> dict:
    """Gemini JSON çıktısını parse et; fence / akıllı tırnak / kesik yanıt toleransı."""
    text = (raw or "").strip()
    if not text:
        raise json.JSONDecodeError("empty response", text, 0)

    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text).strip()

    text = (
        text.replace("\u201c", '"')
        .replace("\u201d", '"')
        .replace("\u2018", "'")
        .replace("\u2019", "'")
    )

    start = text.find("{")
    if start < 0:
        raise json.JSONDecodeError("no JSON object", text, 0)
    blob = text[start:]

    for candidate in (blob, re.sub(r",\s*([}\]])", r"\1", blob)):
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            continue

    raise json.JSONDecodeError("invalid JSON after cleanup", blob, 0)


def vertex_generate(
    prompt: str,
    *,
    system: str = "Sadece istenen formatta yanıt ver.",
    model: str | None = None,
    temperature: float = 0.4,
    json_mode: bool = False,
    response_schema: dict | None = None,
    max_output_tokens: int = 4096,
    project: str | None = None,
    region: str | None = None,
) -> str:
    """Vertex generateContent — ham metin döner."""
    sa = _load_service_account()
    project = project or DEFAULT_PROJECT
    region = region or DEFAULT_REGION
    model = model or DEFAULT_MODEL
    url = (
        f"https://{region}-aiplatform.googleapis.com/v1/"
        f"projects/{project}/locations/{region}/publishers/google/models/{model}:generateContent"
    )
    generation_config: dict = {
        "temperature": temperature,
        "maxOutputTokens": max_output_tokens,
    }
    if json_mode:
        generation_config["responseMimeType"] = "application/json"
        if response_schema:
            generation_config["responseSchema"] = response_schema

    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "systemInstruction": {"parts": [{"text": system}]},
        "generationConfig": generation_config,
    }
    out = _vertex_request(url, payload, sa=sa, timeout=120)

    parts = out.get("candidates", [{}])[0].get("content", {}).get("parts", [])
    text = "".join(p.get("text", "") for p in parts)
    if not text.strip():
        raise RuntimeError(f"Vertex boş yanıt: {json.dumps(out)[:300]}")
    return text.strip()


def vertex_json(prompt: str, **kwargs) -> dict:
    raw = vertex_generate(prompt, json_mode=True, **kwargs)
    return parse_json_relaxed(raw)


def vertex_vision_json(
    prompt: str,
    image_paths: list[Path],
    *,
    system: str = "Sadece istenen formatta yanıt ver.",
    model: str | None = None,
    temperature: float = 0.2,
    project: str | None = None,
    region: str | None = None,
) -> dict:
    """Vertex Gemini multimodal — görsel(ler) + metin → JSON."""
    import base64

    sa = _load_service_account()
    project = project or DEFAULT_PROJECT
    region = region or DEFAULT_REGION
    model = model or os.environ.get("VERTEX_GEMINI_VISION_MODEL", DEFAULT_MODEL)

    parts: list[dict] = []
    for path in image_paths:
        p = Path(path)
        if not p.is_file():
            continue
        mime = "image/png" if p.suffix.lower() == ".png" else "image/jpeg"
        b64 = base64.standard_b64encode(p.read_bytes()).decode()
        parts.append({"inlineData": {"mimeType": mime, "data": b64}})
    parts.append({"text": prompt})

    url = (
        f"https://{region}-aiplatform.googleapis.com/v1/"
        f"projects/{project}/locations/{region}/publishers/google/models/{model}:generateContent"
    )
    payload = {
        "contents": [{"role": "user", "parts": parts}],
        "systemInstruction": {"parts": [{"text": system}]},
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": 8192,
            "responseMimeType": "application/json",
        },
    }
    out = _vertex_request(url, payload, sa=sa, timeout=180)

    text_parts = out.get("candidates", [{}])[0].get("content", {}).get("parts", [])
    text = "".join(p.get("text", "") for p in text_parts)
    if not text.strip():
        raise RuntimeError(f"Vertex vision boş yanıt: {json.dumps(out)[:300]}")
    return json.loads(text.strip())
