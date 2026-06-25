#!/usr/bin/env python3
"""Import all Nefalix workflows into local n8n."""
import json
import os
import subprocess
import sys
from pathlib import Path

N8N_URL = os.environ.get("N8N_URL", "http://localhost:5678")
EMAIL = os.environ.get("N8N_EMAIL")
PASSWORD = os.environ.get("N8N_PASSWORD")
WORKFLOWS_DIR = Path(__file__).resolve().parent.parent / "workflows"
COOKIE_FILE = str(Path(__file__).resolve().parent.parent / ".tmp" / "n8n-import-cookies.txt")
OPENAI_CRED_ID = os.environ.get("N8N_OPENAI_CRED_ID", "ykdMpTuO0tgtcpkb")
VERTEX_CRED_ID = os.environ.get("N8N_VERTEX_CRED_ID", os.environ.get("N8N_OPENAI_CRED_ID", "ykdMpTuO0tgtcpkb"))
SUPABASE_CRED_ID = os.environ.get("N8N_SUPABASE_CRED_ID", "UYVzTr3Rfadp18iR")

SKIP = {"nefalix-web-chatbot.json", "nefalix-telegram-chatbot.json"}

# Bu workflow'lar import sonrası KAPALI kalmalı (ban / güvenlik freni).
# Yeniden aktive edilmesi gerekirse: N8N_FORCE_ACTIVATE_ALL=1 ile çalıştır.
# wf-01: yalnızca NPS yanıt (HBYS otomatik gönderim node'ları JSON'da disabled)
KEEP_INACTIVE: set[str] = set()
FORCE_ACTIVATE_ALL = os.environ.get("N8N_FORCE_ACTIVATE_ALL", "").lower() in (
    "1",
    "true",
    "yes",
)


def curl(*args, check=True):
    cmd = ["curl", "-s", "-b", COOKIE_FILE, "-c", COOKIE_FILE, *args]
    return subprocess.check_output(cmd, text=True) if check else subprocess.run(cmd, text=True)


def login():
    if not EMAIL or not PASSWORD:
        print("❌ N8N_EMAIL ve N8N_PASSWORD .env içinde tanımlı olmalı", file=sys.stderr)
        sys.exit(1)
    subprocess.run(
        [
            "curl", "-s", "-c", COOKIE_FILE, "-X", "POST", f"{N8N_URL}/rest/login",
            "-H", "Content-Type: application/json",
            "-d", json.dumps({"emailOrLdapLoginId": EMAIL, "password": PASSWORD}),
        ],
        check=True,
    )


def attach_credentials(workflow: dict) -> dict:
    for node in workflow.get("nodes", []):
        if node.get("type") == "@n8n/n8n-nodes-langchain.lmChatGoogleVertex":
            node["credentials"] = {
                "googleApi": {"id": VERTEX_CRED_ID, "name": "GCP Vertex Gemini"}
            }
        if node.get("type") == "@n8n/n8n-nodes-langchain.lmChatOpenAi":
            node["credentials"] = {
                "openAiApi": {"id": OPENAI_CRED_ID, "name": "OpenAI account"}
            }
        if node.get("type") == "n8n-nodes-base.supabase":
            node["credentials"] = {
                "supabaseApi": {
                    "id": SUPABASE_CRED_ID,
                    "name": "Nefalix Supabase Local",
                }
            }
    return workflow


def import_workflow(path: Path):
    data = json.loads(path.read_text())
    data = attach_credentials(data)
    name = data["name"]
    keep_inactive = path.name in KEEP_INACTIVE and not FORCE_ACTIVATE_ALL

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
                "-X", "PATCH", f"{N8N_URL}/rest/workflows/{wf_id}",
                "-H", "Content-Type: application/json",
                "-d", json.dumps(payload),
            )
        )
        action = "updated"
    else:
        out = json.loads(
            curl(
                "-X", "POST", f"{N8N_URL}/rest/workflows",
                "-H", "Content-Type: application/json",
                "-d", json.dumps(data),
            )
        )
        action = "imported"
        wf_id = out["data"]["id"]

    ver = out["data"]["versionId"]

    if keep_inactive:
        # Güvenlik freni: kapalı kalsın. Daha önce aktifse deaktive et.
        act = json.loads(
            curl(
                "-X", "POST", f"{N8N_URL}/rest/workflows/{wf_id}/deactivate",
                "-H", "Content-Type: application/json",
                "-d", json.dumps({"versionId": ver}),
            )
        )
        active = act.get("data", {}).get("active", act.get("message", "?"))
        print(f"⏸ {name} — {action}, KAPALI tutuldu (active={active})")
        return wf_id

    act = json.loads(
        curl(
            "-X", "POST", f"{N8N_URL}/rest/workflows/{wf_id}/activate",
            "-H", "Content-Type: application/json",
            "-d", json.dumps({"versionId": ver}),
        )
    )
    active = act.get("data", {}).get("active", act.get("message", "?"))
    print(f"✓ {name} — {action}, active={active}")
    return wf_id


def main():
    login()
    files = sorted(WORKFLOWS_DIR.glob("nefalix-*.json"))
    if not files:
        print("No workflow files found", file=sys.stderr)
        sys.exit(1)

    for f in files:
        if f.name in SKIP:
            print(f"⊘ skip {f.name} (already exists)")
            continue
        try:
            import_workflow(f)
        except subprocess.CalledProcessError as e:
            print(f"✗ {f.name} failed: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
