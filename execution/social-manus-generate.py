#!/usr/bin/env python3
"""Manus API görsel üretimi — task.create + poll (SOCIAL_IMAGE_PROVIDER=manus).

Manus'un ayrı bir image endpoint'i yok; agent task ile PNG üretilir.
Cron için varsayılan: OpenAI gpt-image-2 + social_manus_prompt + Pillow overlay.
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API_BASE = os.environ.get("MANUS_API_BASE", "https://api.manus.ai").rstrip("/")
POLL_SEC = float(os.environ.get("MANUS_POLL_INTERVAL_SEC", "5"))
TIMEOUT_SEC = int(os.environ.get("MANUS_TASK_TIMEOUT_SEC", "300"))


def _api_key() -> str:
    key = os.environ.get("MANUS_API_KEY", "").strip()
    if not key:
        raise RuntimeError("MANUS_API_KEY eksik")
    return key


def _request(method: str, path: str, body: dict | None = None, query: dict | None = None) -> dict:
    url = f"{API_BASE}{path}"
    if query:
        url = f"{url}?{urllib.parse.urlencode(query)}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "x-manus-api-key": _api_key(),
            "Content-Type": "application/json",
            "User-Agent": "Nefalix/1",
        },
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        payload = json.loads(resp.read().decode())
    if not payload.get("ok", True):
        err = payload.get("error") or {}
        raise RuntimeError(f"Manus API: {err.get('code', 'error')} — {err.get('message', payload)}")
    return payload


def _build_task_message(prompt: str) -> str:
    return (
        "Generate a single square 1024x1024 PNG image for an Instagram social media post. "
        "Return ONLY the image file as an attachment — no extra text or slides.\n\n"
        f"Image brief:\n{prompt}"
    )


def _image_urls_from_messages(messages: list) -> list[str]:
    urls: list[str] = []
    for msg in messages:
        for field in ("assistant_message", "user_message"):
            block = msg.get(field) or {}
            for att in block.get("attachments") or []:
                if att.get("type") != "image":
                    continue
                url = (att.get("url") or "").strip()
                if url:
                    urls.append(url)
        content = msg.get("assistant_message", {}).get("content")
        if isinstance(content, str) and content.startswith("http"):
            urls.append(content.strip())
    return urls


def _latest_agent_status(messages: list) -> str | None:
    for msg in messages:
        upd = msg.get("status_update") or {}
        status = (upd.get("agent_status") or upd.get("status") or "").strip()
        if status:
            return status
    return None


def _confirm_auto_accept(task_id: str, messages: list) -> None:
    for msg in messages:
        upd = msg.get("status_update") or {}
        if (upd.get("agent_status") or "") != "waiting":
            continue
        detail = upd.get("status_detail") or {}
        event_id = detail.get("waiting_for_event_id") or msg.get("id")
        event_type = detail.get("waiting_for_event_type") or ""
        if not event_id:
            continue
        if event_type == "messageAskUser":
            _request(
                "POST",
                "/v2/task.sendMessage",
                {"task_id": task_id, "message": {"content": "Proceed with image generation. No logo in top-left."}},
            )
            continue
        payload: dict = {"task_id": task_id, "event_id": event_id, "input": {"accept": True}}
        if event_type == "videoGenerate":
            payload["input"] = {"choice": "standard"}
        try:
            _request("POST", "/v2/task.confirmAction", payload)
        except urllib.error.HTTPError:
            pass


def render_manus_image(prompt: str, output: Path) -> dict:
    create = _request(
        "POST",
        "/v2/task.create",
        {
            "message": {"content": _build_task_message(prompt)},
            "title": "Nefalix social image",
            "hide_in_task_list": True,
            "interactive_mode": False,
            "agent_profile": os.environ.get("MANUS_AGENT_PROFILE", "manus-1.6-lite"),
        },
    )
    task_id = create.get("task_id")
    if not task_id:
        raise RuntimeError(f"Manus task_id yok: {create}")

    deadline = time.time() + TIMEOUT_SEC
    image_url = None
    while time.time() < deadline:
        listed = _request(
            "GET",
            "/v2/task.listMessages",
            query={"task_id": task_id, "order": "desc", "limit": "50"},
        )
        messages = listed.get("messages") or []
        _confirm_auto_accept(task_id, messages)
        urls = _image_urls_from_messages(messages)
        if urls:
            image_url = urls[0]
            break

        status = _latest_agent_status(messages)
        if status == "stopped":
            urls = _image_urls_from_messages(messages)
            if urls:
                image_url = urls[0]
            break
        if status == "error":
            for msg in messages:
                err = msg.get("error_message") or {}
                text = err.get("content") or err.get("message") or str(err)
                if text:
                    raise RuntimeError(f"Manus task failed: {text}")
            raise RuntimeError("Manus task error")

        time.sleep(POLL_SEC)

    if not image_url:
        raise RuntimeError(f"Manus görsel üretilemedi (timeout {TIMEOUT_SEC}s, task={task_id})")

    req = urllib.request.Request(image_url, headers={"User-Agent": "Nefalix/1"})
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(urllib.request.urlopen(req, timeout=120).read())

    return {
        "provider": "manus",
        "model": os.environ.get("MANUS_AGENT_PROFILE", "manus-1.6-lite"),
        "task_id": task_id,
        "path": str(output),
    }


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    result = render_manus_image(args.prompt, Path(args.output))
    print(json.dumps({"ok": True, **result}, ensure_ascii=False))


if __name__ == "__main__":
    main()
