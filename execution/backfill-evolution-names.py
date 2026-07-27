#!/usr/bin/env python3
"""Backfill Evolution Chat.name + Contact.pushName so Manager shows names/phones.

Uses:
  - GET /group/fetchAllGroups/{instance} → group subject → Chat.name
  - Message.key.participantAlt + pushName → Contact
  - Message remoteJid (1:1) → Chat.name from Contact/pushName

Env:
  EVOLUTION_API_URL (default https://evo.nefalix.com)
  EVOLUTION_API_KEY
  EVOLUTION_INSTANCE (default nefalix-crm)
  Or run via: python3 execution/backfill-evolution-names.py

VPS SQL mode (preferred when docker available):
  EVOLUTION_SQL=1  → also writes via docker exec psql
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.request
import uuid
from pathlib import Path

# load .env if present
for env_path in (
    Path(__file__).resolve().parents[1] / ".env",
    Path("/opt/nefalix/.env"),
):
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
        break

BASE = (os.environ.get("EVOLUTION_API_URL") or "https://evo.nefalix.com").rstrip("/")
KEY = os.environ.get("EVOLUTION_API_KEY") or ""
INSTANCE = os.environ.get("EVOLUTION_INSTANCE") or "nefalix-crm"
IID = os.environ.get("EVOLUTION_INSTANCE_ID") or "e6341120-128f-4261-bc6c-259a0017d485"


def evo(method: str, path: str, body=None):
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(
        f"{BASE}{path}",
        data=data,
        method=method,
        headers={
            "apikey": KEY,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode() or "null")


def sql(query: str) -> str:
    cmd = [
        "docker",
        "exec",
        "-i",
        "nefalix-evolution-postgres",
        "psql",
        "-U",
        "evolution",
        "-d",
        "evolution",
        "-v",
        "ON_ERROR_STOP=1",
        "-t",
        "-A",
        "-c",
        query,
    ]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(p.stderr or p.stdout)
    return p.stdout.strip()


def esc(s: str) -> str:
    return (s or "").replace("'", "''")[:100]


def main() -> int:
    if not KEY:
        print("EVOLUTION_API_KEY eksik", file=sys.stderr)
        return 1

    # Enable history sync (best-effort)
    try:
        evo(
            "POST",
            f"/settings/set/{INSTANCE}",
            {
                "syncFullHistory": True,
                "readMessages": False,
                "readStatus": False,
                "alwaysOnline": False,
                "rejectCall": False,
                "groupsIgnore": False,
            },
        )
        print("settings: syncFullHistory=true")
    except Exception as e:
        print("settings warn:", e)

    print("fetching groups…")
    groups = evo("GET", f"/group/fetchAllGroups/{INSTANCE}?getParticipants=false")
    if not isinstance(groups, list):
        print("groups unexpected:", groups)
        groups = []
    print(f"groups: {len(groups)}")

    # Build chat upserts from groups
    chat_rows = []
    for g in groups:
        jid = g.get("id") or ""
        subject = (g.get("subject") or "").strip()
        if jid and subject:
            chat_rows.append((jid, subject))

    # Contacts + chats from messages (SQL)
    print("reading messages from postgres…")
    msg_tsv = sql(
        f"""
SELECT COALESCE("key"->>'remoteJid',''),
       COALESCE("pushName",''),
       COALESCE("key"->>'participantAlt',"key"->>'participant',''),
       COALESCE("key"->>'fromMe','false')
FROM "Message"
WHERE "instanceId" = '{esc(IID)}'
"""
    )
    contact_map: dict[str, str] = {}  # phoneJid -> pushName
    dm_names: dict[str, str] = {}  # remoteJid -> name for 1:1
    for line in msg_tsv.splitlines():
        if not line.strip():
            continue
        parts = line.split("|")
        if len(parts) < 4:
            continue
        remote, push, phone, from_me = parts[0], parts[1], parts[2], parts[3]
        push = (push or "").strip()
        if push in ("", "Você", "You"):
            continue
        if phone and "@s.whatsapp.net" in phone and from_me == "false":
            if phone not in contact_map or len(push) > len(contact_map.get(phone, "")):
                contact_map[phone] = push
        if remote.endswith("@s.whatsapp.net") and from_me == "false" and push:
            dm_names[remote] = push
        # group chats: keep subject from API; also store participants as contacts
        if remote.endswith("@g.us") and phone and "@s.whatsapp.net" in phone:
            if phone not in contact_map:
                contact_map[phone] = push

    for jid, name in dm_names.items():
        chat_rows.append((jid, name))

    # Dedupe chats by jid (prefer longer name)
    chat_best: dict[str, str] = {}
    for jid, name in chat_rows:
        if jid not in chat_best or len(name) > len(chat_best[jid]):
            chat_best[jid] = name

    # Manager findChats id = Contact.id — grup JID’leri de Contact olmalı
    for jid, name in chat_best.items():
        if jid not in contact_map:
            contact_map[jid] = name

    print(f"upsert Chat: {len(chat_best)}, Contact: {len(contact_map)}")

    # Write SQL in batches
    stmts = ["BEGIN;"]
    for jid, name in chat_best.items():
        cid = str(uuid.uuid4())
        stmts.append(
            f"""
INSERT INTO "Chat" (id, "remoteJid", name, "unreadMessages", "createdAt", "updatedAt", "instanceId")
VALUES ('{cid}', '{esc(jid)}', '{esc(name)}', 0, NOW(), NOW(), '{esc(IID)}')
ON CONFLICT ("instanceId", "remoteJid")
DO UPDATE SET name = EXCLUDED.name, "updatedAt" = NOW()
WHERE "Chat".name IS NULL OR "Chat".name = '' OR length(EXCLUDED.name) >= length(COALESCE("Chat".name,''));
"""
        )
    for jid, name in contact_map.items():
        cid = str(uuid.uuid4())
        stmts.append(
            f"""
INSERT INTO "Contact" (id, "remoteJid", "pushName", "createdAt", "updatedAt", "instanceId")
VALUES ('{cid}', '{esc(jid)}', '{esc(name)}', NOW(), NOW(), '{esc(IID)}')
ON CONFLICT ("remoteJid", "instanceId")
DO UPDATE SET "pushName" = EXCLUDED."pushName", "updatedAt" = NOW()
WHERE "Contact"."pushName" IS NULL OR "Contact"."pushName" = '' OR length(EXCLUDED."pushName") >= length(COALESCE("Contact"."pushName",''));
"""
        )
    stmts.append("COMMIT;")
    big = "\n".join(stmts)
    # pipe to psql
    cmd = [
        "docker",
        "exec",
        "-i",
        "nefalix-evolution-postgres",
        "psql",
        "-U",
        "evolution",
        "-d",
        "evolution",
        "-v",
        "ON_ERROR_STOP=1",
    ]
    p = subprocess.run(cmd, input=big, capture_output=True, text=True)
    if p.returncode != 0:
        print(p.stderr or p.stdout, file=sys.stderr)
        return 1
    print(p.stdout[-500:] if p.stdout else "ok")

    counts = sql(
        f"""SELECT
  (SELECT COUNT(*) FROM "Chat" WHERE "instanceId"='{esc(IID)}'),
  (SELECT COUNT(*) FROM "Contact" WHERE "instanceId"='{esc(IID)}')"""
    )
    print("Chat/Contact counts:", counts)

    # Verify API
    try:
        chats = evo("POST", f"/chat/findChats/{INSTANCE}", {"where": {}})
        arr = chats if isinstance(chats, list) else []
        named = sum(1 for c in arr if (c.get("pushName") or c.get("name")))
        print(f"findChats: {len(arr)} (named fields sample):")
        for c in arr[:5]:
            print(
                " ",
                c.get("remoteJid"),
                "| name=",
                c.get("name"),
                "| pushName=",
                c.get("pushName"),
            )
        print(f"named-ish: {named}/{len(arr)}")
    except Exception as e:
        print("findChats warn:", e)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
