#!/usr/bin/env python3
"""Estesoft poll + dedup: yeni tamamlanan randevuları kaçırma.

- too_old: modified/created öncelikli (startDate değil)
- dedup: historical_seed sayılmaz; sadece adapter_draft / adapter
"""
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

const rows = await this.helpers.httpRequest({
  method: 'GET',
  url: `${sbBase}/rest/v1/automation_events?clinic_id=eq.${CLINIC_ID}&event_type=eq.estesoft_nps_triggered&payload->>appointmentId=eq.${encodeURIComponent(item.appointmentId)}&select=id,payload&limit=5`,
  headers: {
    apikey: sbKey,
    Authorization: `Bearer ${sbKey}`,
  },
  json: true,
});

const alreadyDrafted = Array.isArray(rows) && rows.some((r) => {
  const src = String(r.payload?.source || '');
  return src === 'adapter_draft' || src === 'adapter';
});

if (alreadyDrafted) {
  return [{ json: { skip: true, reason: 'dedup', appointmentId: item.appointmentId } }];
}
return [{ json: item }];"""

ALREADY_TRIGGERED_OLD = """async function alreadyTriggered(extId) {
  const rows = await this.helpers.httpRequest({
    method: 'GET',
    url: `${sbBase}/rest/v1/automation_events?clinic_id=eq.${CLINIC_ID}&event_type=eq.estesoft_nps_triggered&payload->>appointmentId=eq.${encodeURIComponent(extId)}&select=id&limit=1`,
    headers: sbH,
    json: true,
  });
  return Array.isArray(rows) && rows.length > 0;
}"""

ALREADY_TRIGGERED_NEW = """async function alreadyTriggered(extId) {
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
}

function apptFreshness(appt) {
  return (
    appt.modified ||
    appt.modifiedDate ||
    appt.created ||
    appt.createdDate ||
    appt.endDate ||
    appt.startDate ||
    appt.appointmentDate ||
    appt.date
  );
}"""

RAW_DATE_OLD = """  const rawDate = appt.appointmentDate || appt.startDate || appt.date || appt.endDate || appt.modifiedDate;
  if (rawDate) {
    const t = new Date(rawDate).getTime();
    if (!Number.isNaN(t) && t < cutoff) {
      results.push({ id: appt.id, customerName: appt.customerName, skipped: true, reason: 'too_old' });
      continue;
    }
  }"""

RAW_DATE_NEW = """  const rawDate = apptFreshness(appt);
  if (rawDate) {
    const t = new Date(rawDate).getTime();
    if (!Number.isNaN(t) && t < cutoff) {
      results.push({ id: appt.id, customerName: appt.customerName, skipped: true, reason: 'too_old', at: rawDate });
      continue;
    }
  }"""


def patch_wf12() -> None:
    path = ROOT / "workflows" / "nefalix-12-estesoft-adapter.json"
    data = json.loads(path.read_text())
    for node in data["nodes"]:
        if node.get("name") == "Dedup Kontrol":
            node["parameters"]["jsCode"] = DEDUP_WF12
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print("✓ wf-12 Dedup Kontrol")


def patch_wf13() -> None:
    path = ROOT / "workflows" / "nefalix-13-estesoft-poll.json"
    data = json.loads(path.read_text())
    code = data["nodes"][3]["parameters"]["jsCode"]  # Estesoft Poll node

    code = code.replace(
        "url: `${sbBase}/rest/v1/automation_events?clinic_id=eq.${CLINIC_ID}&event_type=eq.estesoft_nps_triggered&payload->>appointmentId=eq.${encodeURIComponent(extId)}&select=id&limit=1`,",
        "url: `${sbBase}/rest/v1/automation_events?clinic_id=eq.${CLINIC_ID}&event_type=eq.estesoft_nps_triggered&payload->>appointmentId=eq.${encodeURIComponent(extId)}&select=id,payload&limit=5`,",
    )
    code = code.replace(
        "  return Array.isArray(rows) && rows.length > 0;\n}",
        "  return Array.isArray(rows) && rows.some((r) => {\n    const src = String(r.payload?.source || '');\n    return src === 'adapter_draft' || src === 'adapter';\n  });\n}\n\nfunction apptFreshness(appt) {\n  return (\n    appt.modified ||\n    appt.modifiedDate ||\n    appt.created ||\n    appt.createdDate ||\n    appt.endDate ||\n    appt.startDate ||\n    appt.appointmentDate ||\n    appt.date\n  );\n}",
    )
    code = code.replace(
        "  const rawDate = appt.appointmentDate || appt.startDate || appt.date || appt.endDate || appt.modifiedDate;",
        "  const rawDate = apptFreshness(appt);",
    )
    code = code.replace(
        "reason: 'too_old' }",
        "reason: 'too_old', at: rawDate }",
    )

    for node in data["nodes"]:
        if node.get("name") == "Estesoft Poll":
            node["parameters"]["jsCode"] = code
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print("✓ wf-13 poll freshness + dedup")


def main() -> None:
    patch_wf12()
    patch_wf13()


if __name__ == "__main__":
    main()
