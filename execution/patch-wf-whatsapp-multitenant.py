#!/usr/bin/env python3
"""Patch wf-06, wf-00, wf-08 for per-clinic Evolution instance routing."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PILOT = "51738ea8-c12e-40ce-a0e2-42869496d76b"

SOHBET_PREFIX = """const base = ($env.SUPABASE_URL || 'http://host.docker.internal:54321').replace(/\\/$/, '');
const key = $env.SUPABASE_SERVICE_ROLE_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0.EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU';
const PILOT_CLINIC = '51738ea8-c12e-40ce-a0e2-42869496d76b';
const m = $('Mesaj Normalize').first().json;
const headers = { apikey: key, Authorization: `Bearer ${key}` };
let CLINIC_ID = PILOT_CLINIC;
const instanceName = String(m.instance || $env.EVOLUTION_INSTANCE || 'medident-pilot').trim();
if (instanceName) {
  const clinics = await this.helpers.httpRequest({
    method: 'GET',
    url: `${base}/rest/v1/clinics?evolution_instance_name=eq.${encodeURIComponent(instanceName)}&select=id&limit=1`,
    headers,
    json: true,
  });
  if (Array.isArray(clinics) && clinics[0]?.id) CLINIC_ID = clinics[0].id;
}
const phone = String(m.phone || '').replace(/\\D/g, '');
const currentMsg = String(m.message || '').trim();
"""

SOHBET_SUFFIX = """
return [{
  json: {
    ...m,
    clinic_id: CLINIC_ID,
    instance: instanceName,
    message: mergedMessage,
    originalMessage: currentMsg,
    historyText,
    historyCount: older.length,
  },
}];"""

INBOX_SAVE = f"""const base = ($env.SUPABASE_URL || 'http://host.docker.internal:54321').replace(/\\/$/, '');
const key = $env.SUPABASE_SERVICE_ROLE_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0.EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU';
const m = $('Sohbet Geçmişi').item.json;
const ai = $('AI Taslak Yanıt').item.json;
const draft = ai.output || ai.text || '';
const row = await this.helpers.httpRequest({{
  method: 'POST',
  url: `${{base}}/rest/v1/inbox_messages`,
  headers: {{
    apikey: key,
    Authorization: `Bearer ${{key}}`,
    'Content-Type': 'application/json',
    Prefer: 'return=representation',
  }},
  body: {{
    clinic_id: m.clinic_id || '{PILOT}',
    channel: m.channel || 'whatsapp',
    direction: 'inbound',
    body: m.originalMessage || m.message || '',
    sender_phone: m.phone || '',
    sender_name: m.patientName || 'Hasta',
    ai_draft_reply: draft,
    status: draft ? 'draft_ready' : 'open',
  }},
  json: true,
}});
return [{{ json: {{ ok: true, row }} }}];"""

GATEWAY_EXTRA = """
const clinicId = String(input.clinicId || input.clinic_id || '51738ea8-c12e-40ce-a0e2-42869496d76b');
let instance = String(input.instance || '').trim();
if (!instance) {
  const clinicRows = await this.helpers.httpRequest({
    method: 'GET',
    url: `${sbBase}/rest/v1/clinics?id=eq.${clinicId}&select=evolution_instance_name&limit=1`,
    headers: sbH,
    json: true,
  });
  instance = clinicRows?.[0]?.evolution_instance_name || $env.EVOLUTION_INSTANCE || 'medident-pilot';
}
const CLINIC_ID = clinicId;
"""

WF08_PARSE_CLINIC = {
    "id": "4",
    "name": "clinicId",
    "value": "={{ $json.body?.clinicId ?? $json.body?.clinic_id ?? $json.clinicId ?? '' }}",
    "type": "string",
}

WF08_GATEWAY_BODY = (
    "={{ JSON.stringify({ number: $json.phone, text: $json.text, "
    "source: 'inbox-send', priority: 'normal', "
    "clinicId: $json.clinicId || undefined }) }}"
)

WF08_SUPABASE = f"""const base = ($env.SUPABASE_URL || 'http://host.docker.internal:54321').replace(/\\/$/, '');
const key = $env.SUPABASE_SERVICE_ROLE_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0.EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU';
const PILOT = '{PILOT}';
const req = $('Parse İstek').item.json;
const messageId = req.messageId;
const phone = req.phone || '';
const text = req.text || '';
let CLINIC_ID = req.clinicId || PILOT;
const headers = {{
  apikey: key,
  Authorization: `Bearer ${{key}}`,
  'Content-Type': 'application/json',
  Prefer: 'return=minimal',
}};

if (!req.clinicId && messageId) {{
  const rows = await this.helpers.httpRequest({{
    method: 'GET',
    url: `${{base}}/rest/v1/inbox_messages?id=eq.${{messageId}}&select=clinic_id&limit=1`,
    headers,
    json: true,
  }});
  if (rows?.[0]?.clinic_id) CLINIC_ID = rows[0].clinic_id;
}}

if (messageId) {{
  await this.helpers.httpRequest({{
    method: 'PATCH',
    url: `${{base}}/rest/v1/inbox_messages?id=eq.${{messageId}}`,
    headers,
    body: {{ status: 'replied' }},
    json: true,
  }});
}}

if (phone && text) {{
  await this.helpers.httpRequest({{
    method: 'POST',
    url: `${{base}}/rest/v1/inbox_messages`,
    headers,
    body: {{
      clinic_id: CLINIC_ID,
      channel: 'whatsapp',
      direction: 'outbound',
      body: text,
      sender_phone: phone,
      status: 'replied',
    }},
    json: true,
  }});
}}

return [{{ json: {{ ok: true, updated: Boolean(messageId), outboundLogged: Boolean(phone && text), clinicId: CLINIC_ID }} }}];"""


def patch_wf06(data: dict) -> None:
    for node in data["nodes"]:
        if node["name"] == "Mesaj Normalize":
            assigns = node["parameters"]["assignments"]["assignments"]
            if not any(a.get("name") == "instance" for a in assigns):
                assigns.append(
                    {
                        "id": "5",
                        "name": "instance",
                        "value": "={{ $json.body?.instance ?? $json.instance ?? '' }}",
                        "type": "string",
                    }
                )
        if node["name"] == "Sohbet Geçmişi":
            old = node["parameters"]["jsCode"]
            mid_start = old.find("let rows = []")
            mid_end = old.find("return [{")
            if mid_start < 0 or mid_end < 0:
                raise RuntimeError("wf-06 Sohbet Geçmişi yapısı beklenenden farklı")
            mid = old[mid_start:mid_end]
            node["parameters"]["jsCode"] = SOHBET_PREFIX + mid + SOHBET_SUFFIX
        if node["name"] == "Supabase Inbox Kaydet":
            node["parameters"]["jsCode"] = INBOX_SAVE


def patch_wf00(data: dict) -> None:
    for node in data["nodes"]:
        if node["name"] != "Rate Limit + Gönder":
            continue
        code = node["parameters"]["jsCode"]
        if "let instance = String(input.instance" in code and code.find("const sbBase") < code.find("const clinicId"):
            return
        code = code.replace(
            "const CLINIC_ID = '51738ea8-c12e-40ce-a0e2-42869496d76b';",
            "/* clinic resolved after sbH */",
        )
        code = code.replace(
            "const instance = $env.EVOLUTION_INSTANCE || 'medident-pilot';",
            "/* instance resolved below */",
        )
        marker = "const sbH = {"
        idx = code.find(marker)
        if idx < 0:
            raise RuntimeError("wf-00 sbH marker not found")
        end = code.find("};", idx) + 2
        node["parameters"]["jsCode"] = (
            code[:end] + "\n\n" + GATEWAY_EXTRA.strip() + "\n" + code[end:]
        )


def patch_wf08(data: dict) -> None:
    for node in data["nodes"]:
        if node["name"] == "Parse İstek":
            assigns = node["parameters"]["assignments"]["assignments"]
            if not any(a.get("name") == "clinicId" for a in assigns):
                assigns.append(WF08_PARSE_CLINIC)
        if node["name"] == "WA Gateway Gönder":
            node["parameters"]["jsonBody"] = WF08_GATEWAY_BODY
        if node["name"] == "Supabase Durum Güncelle":
            node["parameters"]["jsCode"] = WF08_SUPABASE


def main() -> None:
    for fname, patcher in [
        ("nefalix-06-inbox-routing.json", patch_wf06),
        ("nefalix-00-whatsapp-gateway.json", patch_wf00),
        ("nefalix-08-inbox-send.json", patch_wf08),
    ]:
        path = ROOT / "workflows" / fname
        data = json.loads(path.read_text())
        patcher(data)
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
        print(f"patched {fname}")


if __name__ == "__main__":
    main()
