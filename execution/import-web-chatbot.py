#!/usr/bin/env python3
"""Import / activate Nefalix AI - Web Chatbot (skipped by import-workflows.py)."""
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

N8N_URL = os.environ.get("N8N_URL", "http://localhost:5678")
EMAIL = os.environ.get("N8N_EMAIL")
PASSWORD = os.environ.get("N8N_PASSWORD")
WORKFLOW = Path(__file__).resolve().parent.parent / "workflows" / "nefalix-web-chatbot.json"
COOKIE_FILE = str(Path(__file__).resolve().parent.parent / ".tmp" / "n8n-import-cookies.txt")
VERTEX_CRED_ID = os.environ.get("N8N_VERTEX_CRED_ID", os.environ.get("N8N_OPENAI_CRED_ID", "iBZAz4f5OUKfmohg"))


def curl(*args):
    return subprocess.check_output(
        ["curl", "-s", "-b", COOKIE_FILE, "-c", COOKIE_FILE, *args],
        text=True,
    )


def login():
    subprocess.run(
        [
            "curl",
            "-s",
            "-c",
            COOKIE_FILE,
            "-X",
            "POST",
            f"{N8N_URL}/rest/login",
            "-H",
            "Content-Type: application/json",
            "-d",
            json.dumps({"emailOrLdapLoginId": EMAIL, "password": PASSWORD}),
        ],
        check=True,
    )


def attach_credentials(workflow: dict) -> dict:
    for node in workflow.get("nodes", []):
        if node.get("type") == "@n8n/n8n-nodes-langchain.lmChatGoogleVertex":
            node["credentials"] = {
                "googleApi": {"id": VERTEX_CRED_ID, "name": "GCP Vertex Gemini"}
            }
    return workflow


def chat_webhook_id(workflow: dict) -> Optional[str]:
    for node in workflow.get("nodes", []):
        if node.get("type") == "@n8n/n8n-nodes-langchain.chatTrigger":
            return node.get("webhookId")
    return None


def main():
    login()
    data = attach_credentials(json.loads(WORKFLOW.read_text()))
    name = data["name"]

    existing = json.loads(curl(f"{N8N_URL}/rest/workflows"))
    wf_id = None
    for w in existing.get("data", []):
        if w.get("name") == name:
            wf_id = w["id"]
            break

    payload = {
        "name": data["name"],
        "nodes": data["nodes"],
        "connections": data["connections"],
        "settings": data.get("settings", {}),
    }

    if wf_id:
        out = json.loads(
            curl(
                "-X",
                "PATCH",
                f"{N8N_URL}/rest/workflows/{wf_id}",
                "-H",
                "Content-Type: application/json",
                "-d",
                json.dumps(payload),
            )
        )
        action = "updated"
    else:
        out = json.loads(
            curl(
                "-X",
                "POST",
                f"{N8N_URL}/rest/workflows",
                "-H",
                "Content-Type: application/json",
                "-d",
                json.dumps(data),
            )
        )
        action = "imported"
        wf_id = out["data"]["id"]

    ver = out["data"]["versionId"]
    act = json.loads(
        curl(
            "-X",
            "POST",
            f"{N8N_URL}/rest/workflows/{wf_id}/activate",
            "-H",
            "Content-Type: application/json",
            "-d",
            json.dumps({"versionId": ver}),
        )
    )
    active = act.get("data", {}).get("active", act.get("message", "?"))

    refreshed = json.loads(curl(f"{N8N_URL}/rest/workflows/{wf_id}"))
    hook_id = chat_webhook_id(refreshed.get("data", {}))
    host = os.environ.get("N8N_PUBLIC_HOST", "api.nefalixai.com")
    if hook_id:
        chat_url = f"https://{host}/webhook/{hook_id}/chat"
        print(f"✓ {name} — {action}, active={active}")
        print(f"CHAT_WEBHOOK_URL={chat_url}")
    else:
        print(f"✓ {name} — {action}, active={active}")
        print("⚠ webhookId bulunamadı — n8n UI'dan Web Chat node kontrol et", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
