#!/usr/bin/env python3
"""Create or reuse n8n credentials for Medident pilot (Supabase + Vertex Gemini)."""
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
COOKIE_FILE = REPO / ".tmp" / "n8n-import-cookies.txt"

N8N_URL = os.environ.get("N8N_URL", "http://localhost:5678")
EMAIL = os.environ.get("N8N_EMAIL")
PASSWORD = os.environ.get("N8N_PASSWORD")

SUPABASE_HOST = os.environ.get(
    "N8N_SUPABASE_HOST", "http://host.docker.internal:54321"
)
SUPABASE_SERVICE_KEY = os.environ.get(
    "SUPABASE_SERVICE_ROLE_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0.EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU",
)

SUPABASE_NAME = "Nefalix Supabase Local"
VERTEX_NAME = "GCP Vertex Gemini"


def load_service_account() -> dict | None:
    raw = os.environ.get("GCP_SERVICE_ACCOUNT_JSON", "").strip()
    if raw:
        return json.loads(raw)
    path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")
    if path and Path(path).is_file():
        return json.loads(Path(path).read_text())
    fallback = REPO / ".tmp" / "gcp-service-account.json"
    if fallback.is_file():
        return json.loads(fallback.read_text())
    return None


def curl(*args, check=True):
    COOKIE_FILE.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["curl", "-s", "-b", str(COOKIE_FILE), "-c", str(COOKIE_FILE), *args]
    if check:
        return subprocess.check_output(cmd, text=True)
    subprocess.run(cmd, check=False, text=True)
    return ""


def login():
    subprocess.run(
        [
            "curl",
            "-s",
            "-c",
            str(COOKIE_FILE),
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


def list_credentials():
    raw = curl(f"{N8N_URL}/rest/credentials")
    data = json.loads(raw)
    return data.get("data", data if isinstance(data, list) else [])


def find_by_name(creds, name):
    for c in creds:
        if c.get("name") == name:
            return c.get("id")
    return None


def create_credential(name, cred_type, data):
    payload = {"name": name, "type": cred_type, "data": data}
    out = json.loads(
        curl(
            "-X",
            "POST",
            f"{N8N_URL}/rest/credentials",
            "-H",
            "Content-Type: application/json",
            "-d",
            json.dumps(payload),
        )
    )
    return out.get("data", out).get("id") or out.get("id")


def ensure_supabase(creds):
    if not SUPABASE_SERVICE_KEY:
        cid = find_by_name(creds, SUPABASE_NAME)
        if cid:
            print(f"⚠ SUPABASE_SERVICE_ROLE_KEY yok — mevcut credential: {cid}")
            return cid
        print("❌ SUPABASE_SERVICE_ROLE_KEY .env içinde yok", file=sys.stderr)
        sys.exit(1)

    data = {"host": SUPABASE_HOST, "serviceRole": SUPABASE_SERVICE_KEY}

    for c in creds:
        if c.get("type") == "supabaseApi":
            curl("-X", "DELETE", f"{N8N_URL}/rest/credentials/{c['id']}")
            print(f"▶ Eski Supabase credential silindi: {c['id']}")

    cid = create_credential(SUPABASE_NAME, "supabaseApi", data)
    print(f"✓ Supabase credential oluşturuldu: {cid}")
    return cid


def ensure_vertex(creds):
    sa = load_service_account()
    if not sa:
        cid = find_by_name(creds, VERTEX_NAME)
        if cid:
            print(f"⚠ GCP service account yok — mevcut Vertex credential: {cid}")
            return cid
        print(
            "⚠ GCP service account yok — .tmp/gcp-service-account.json ekleyin",
            file=sys.stderr,
        )
        return os.environ.get("N8N_VERTEX_CRED_ID", "")

    for c in creds:
        if c.get("type") == "googleApi":
            curl("-X", "DELETE", f"{N8N_URL}/rest/credentials/{c['id']}")
            print(f"▶ Eski Google API credential silindi: {c['id']}")

    data = {
        "email": sa["client_email"],
        "privateKey": sa["private_key"],
    }
    cid = create_credential(VERTEX_NAME, "googleApi", data)
    print(f"✓ Vertex Gemini credential oluşturuldu: {cid}")
    return cid


def main():
    login()
    creds = list_credentials()
    supabase_id = ensure_supabase(creds)
    vertex_id = ensure_vertex(creds)

    ids_file = REPO / ".tmp" / "n8n-credential-ids.json"
    ids_file.parent.mkdir(parents=True, exist_ok=True)
    ids_file.write_text(
        json.dumps(
            {"supabase": supabase_id, "vertex": vertex_id},
            indent=2,
        )
        + "\n"
    )
    print(f"\n→ {ids_file}")
    print(f"export N8N_SUPABASE_CRED_ID={supabase_id}")
    if vertex_id:
        print(f"export N8N_VERTEX_CRED_ID={vertex_id}")


if __name__ == "__main__":
    main()
