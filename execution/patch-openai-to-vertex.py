#!/usr/bin/env python3
"""Workflow JSON: OpenAI lmChatOpenAi → Vertex Gemini (GCP kredisi)."""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
WORKFLOWS = REPO / "workflows"
VERTEX_MODEL = "gemini-2.5-flash"
OLD_TYPE = "@n8n/n8n-nodes-langchain.lmChatOpenAi"
NEW_TYPE = "@n8n/n8n-nodes-langchain.lmChatGoogleVertex"
OLD_NAME = "OpenAI Chat Model"
NEW_NAME = "Gemini Vertex Model"


def patch_node(node: dict) -> bool:
    if node.get("type") != OLD_TYPE:
        return False
    node["type"] = NEW_TYPE
    node["typeVersion"] = 1
    node["name"] = NEW_NAME
    node["parameters"] = {
        "projectId": {
            "__rl": True,
            "mode": "id",
            "value": "={{ $env.GCP_PROJECT_ID }}",
        },
        "modelName": VERTEX_MODEL,
        "options": {"temperature": 0.4, "maxOutputTokens": 2048},
    }
    node.pop("credentials", None)
    return True


def patch_connections(conns: dict) -> dict:
    if OLD_NAME not in conns:
        return conns
    conns[NEW_NAME] = conns.pop(OLD_NAME)
    return conns


def patch_sticky(content: str) -> str:
    return content.replace("OpenAI", "Vertex Gemini").replace("openai", "Vertex")


def patch_file(path: Path) -> int:
    data = json.loads(path.read_text())
    n = 0
    for node in data.get("nodes", []):
        if patch_node(node):
            n += 1
        if node.get("type") == "n8n-nodes-base.stickyNote":
            p = node.get("parameters", {})
            if "content" in p:
                p["content"] = patch_sticky(p["content"])
    data["connections"] = patch_connections(data.get("connections", {}))
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    return n


def main():
    total = 0
    for path in sorted(WORKFLOWS.glob("nefalix-*.json")):
        if path.name in ("nefalix-web-chatbot.json", "nefalix-telegram-chatbot.json"):
            continue
        count = patch_file(path)
        if count:
            print(f"✓ {path.name}: {count} model node(s)")
            total += count
    if not total:
        print("No OpenAI nodes found (already patched?)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
