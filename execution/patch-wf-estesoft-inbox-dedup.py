#!/usr/bin/env python3
"""Estesoft dedup: inbox temizlendiyse taslak yeniden üretilebilir."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DEDUP_WF12 = r"""const item = $json;
if (!item.appointmentId) return [{ json: item }];

const CLINIC_ID = item.clinic_id;
const sbBase = ($env.SUPABASE_URL || 'http://host.docker.internal:54321').replace(/\/$/, '');
const sbKey = $env.SUPABASE_SERVICE_ROLE_KEY;
if (!sbKey) return [{ json: item }];

const headers = {
  apikey: sbKey,
  Authorization: `Bearer ${sbKey}`,
};

const events = await this.helpers.httpRequest({
  method: 'GET',
  url: `${sbBase}/rest/v1/automation_events?clinic_id=eq.${CLINIC_ID}&event_type=eq.estesoft_nps_triggered&payload->>appointmentId=eq.${encodeURIComponent(item.appointmentId)}&select=id,payload&limit=5`,
  headers,
  json: true,
});

if (Array.isArray(events) && events.some((r) => r.payload?.source === 'historical_seed')) {
  return [{ json: { skip: true, reason: 'historical_seed', appointmentId: item.appointmentId } }];
}

const inbox = await this.helpers.httpRequest({
  method: 'GET',
  url: `${sbBase}/rest/v1/inbox_messages?message_kind=eq.estesoft_nps&metadata->>appointmentId=eq.${encodeURIComponent(item.appointmentId)}&select=id,status&limit=5`,
  headers,
  json: true,
});

const activeInbox = Array.isArray(inbox) && inbox.some((r) => r.status === 'draft_ready' || r.status === 'replied');
if (activeInbox) {
  return [{ json: { skip: true, reason: 'dedup_inbox', appointmentId: item.appointmentId } }];
}

return [{ json: item }];"""

ALREADY_TRIGGERED_NEW = r"""async function alreadyTriggered(extId) {
  const rows = await this.helpers.httpRequest({
    method: 'GET',
    url: `${sbBase}/rest/v1/automation_events?clinic_id=eq.${CLINIC_ID}&event_type=eq.estesoft_nps_triggered&payload->>appointmentId=eq.${encodeURIComponent(extId)}&select=id,payload&limit=5`,
    headers: sbH,
    json: true,
  });
  if (Array.isArray(rows) && rows.some((r) => r.payload?.source === 'historical_seed')) {
    return true;
  }
  const inbox = await this.helpers.httpRequest({
    method: 'GET',
    url: `${sbBase}/rest/v1/inbox_messages?message_kind=eq.estesoft_nps&metadata->>appointmentId=eq.${encodeURIComponent(extId)}&select=id,status&limit=5`,
    headers: sbH,
    json: true,
  });
  return Array.isArray(inbox) && inbox.some((r) => r.status === 'draft_ready' || r.status === 'replied');
}"""


def patch_wf12() -> None:
    path = ROOT / "workflows" / "nefalix-12-estesoft-adapter.json"
    data = json.loads(path.read_text())
    for node in data["nodes"]:
        if node.get("name") == "Dedup Kontrol":
            node["parameters"]["jsCode"] = DEDUP_WF12
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print("✓ wf-12 dedup (inbox-aware)")


def patch_wf13() -> None:
    path = ROOT / "workflows" / "nefalix-13-estesoft-poll.json"
    data = json.loads(path.read_text())
    old = """async function alreadyTriggered(extId) {
  const rows = await this.helpers.httpRequest({
    method: 'GET',
    url: `${sbBase}/rest/v1/automation_events?clinic_id=eq.${CLINIC_ID}&event_type=eq.estesoft_nps_triggered&payload->>appointmentId=eq.${encodeURIComponent(extId)}&select=id,payload&limit=5`,
    headers: sbH,
    json: true,
  });
  return Array.isArray(rows) && rows.some((r) => {
    const src = String(r.payload?.source || '');
    return src === 'adapter_draft' || src === 'adapter';
  });
}"""
    for node in data["nodes"]:
        if node.get("name") == "Estesoft Poll":
            code = node["parameters"]["jsCode"]
            if old not in code:
                raise SystemExit("wf-13 alreadyTriggered eski blok bulunamadı")
            node["parameters"]["jsCode"] = code.replace(old, ALREADY_TRIGGERED_NEW)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print("✓ wf-13 dedup (inbox-aware)")


def main() -> None:
    patch_wf12()
    patch_wf13()


if __name__ == "__main__":
    main()
