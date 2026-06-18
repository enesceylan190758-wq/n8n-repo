#!/usr/bin/env python3
"""Import all Nefalix workflows into local n8n."""
import json
import os
import subprocess
import sys
from pathlib import Path

N8N_URL = os.environ.get("N8N_URL", "http://localhost:5678")
EMAIL = os.environ.get("N8N_EMAIL", "enkahealthist@gmail.com")
PASSWORD = os.environ.get("N8N_PASSWORD", "Nefalix2026!")
WORKFLOWS_DIR = Path(__file__).resolve().parent.parent / "workflows"
COOKIE_FILE = str(Path(__file__).resolve().parent.parent / ".tmp" / "n8n-import-cookies.txt")
OPENAI_CRED_ID = os.environ.get("N8N_OPENAI_CRED_ID", "ykdMpTuO0tgtcpkb")

SKIP = {"nefalix-web-chatbot.json", "nefalix-telegram-chatbot.json"}


def curl(*args, check=True):
    cmd = ["curl", "-s", "-b", COOKIE_FILE, "-c", COOKIE_FILE, *args]
    return subprocess.check_output(cmd, text=True) if check else subprocess.run(cmd, text=True)


def login():
    subprocess.run(
        [
            "curl", "-s", "-c", COOKIE_FILE, "-X", "POST", f"{N8N_URL}/rest/login",
            "-H", "Content-Type: application/json",
            "-d", json.dumps({"emailOrLdapLoginId": EMAIL, "password": PASSWORD}),
        ],
        check=True,
    )


def attach_openai(workflow: dict) -> dict:
    for node in workflow.get("nodes", []):
        if node.get("type") == "@n8n/n8n-nodes-langchain.lmChatOpenAi":
            node["credentials"] = {
                "openAiApi": {"id": OPENAI_CRED_ID, "name": "OpenAI account"}
            }
            params = node.get("parameters", {})
            model = params.get("model", {})
            if not model.get("value"):
                params["model"] = {
                    "__rl": True,
                    "mode": "list",
                    "value": "gpt-4o-mini",
                    "cachedResultName": "gpt-4o-mini",
                }
    return workflow


def import_workflow(path: Path):
    data = json.loads(path.read_text())
    data = attach_openai(data)
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
