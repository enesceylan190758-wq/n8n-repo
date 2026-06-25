#!/usr/bin/env python3
"""WhatsApp gateway workflow + tüm Evolution sendText node'larını gateway'e yönlendir."""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
WF_DIR = REPO / "workflows"

GATEWAY_JS = r"""const input = $json.body ?? $json;
const number = String(input.number || '').replace(/\D/g, '');
const text = String(input.text || '').trim();
const source = String(input.source || input.workflow || 'unknown').slice(0, 80);
const priority = String(input.priority || 'normal');

if (!number || number.length < 10) {
  return [{ json: { sent: false, error: 'invalid_number' } }];
}
if (!text) {
  return [{ json: { sent: false, error: 'empty_text' } }];
}

const ENABLED = String($env.WHATSAPP_SEND_ENABLED ?? 'true').toLowerCase() !== 'false';
const MIN_INTERVAL = Number($env.WHATSAPP_MIN_INTERVAL_SEC || 45);
const MAX_HOUR = Number($env.WHATSAPP_MAX_PER_HOUR || 20);
const MAX_5MIN = Number($env.WHATSAPP_MAX_BURST_5MIN || 3);
const CLINIC_ID = '51738ea8-c12e-40ce-a0e2-42869496d76b';

const sbBase = ($env.SUPABASE_URL || 'http://host.docker.internal:54321').replace(/\/$/, '');
const sbKey = $env.SUPABASE_SERVICE_ROLE_KEY;
if (!sbKey) throw new Error('SUPABASE_SERVICE_ROLE_KEY eksik');

const sbH = {
  apikey: sbKey,
  Authorization: `Bearer ${sbKey}`,
  'Content-Type': 'application/json',
  Prefer: 'return=minimal',
};

async function countSince(iso) {
  const rows = await this.helpers.httpRequest({
    method: 'GET',
    url: `${sbBase}/rest/v1/whatsapp_send_log?created_at=gte.${encodeURIComponent(iso)}&status=eq.sent&select=id`,
    headers: sbH,
    json: true,
  });
  return Array.isArray(rows) ? rows.length : 0;
}

async function lastSentAt() {
  const rows = await this.helpers.httpRequest({
    method: 'GET',
    url: `${sbBase}/rest/v1/whatsapp_send_log?status=eq.sent&order=created_at.desc&limit=1&select=created_at`,
    headers: sbH,
    json: true,
  });
  return rows?.[0]?.created_at ? new Date(rows[0].created_at).getTime() : 0;
}

async function logRow(row) {
  await this.helpers.httpRequest({
    method: 'POST',
    url: `${sbBase}/rest/v1/whatsapp_send_log`,
    headers: sbH,
    body: { clinic_id: CLINIC_ID, phone: number, message_preview: text.slice(0, 160), source_workflow: source, ...row },
    json: true,
  });
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

if (!ENABLED) {
  await logRow.call(this, { status: 'skipped', block_reason: 'whatsapp_disabled' });
  return [{ json: { sent: false, skipped: true, reason: 'whatsapp_disabled', source } }];
}

const now = Date.now();
const hourAgo = new Date(now - 3600000).toISOString();
const fiveMinAgo = new Date(now - 300000).toISOString();
const hourCount = await countSince.call(this, hourAgo);
const burstCount = await countSince.call(this, fiveMinAgo);
const lastMs = await lastSentAt.call(this);
const sinceLastSec = lastMs ? (now - lastMs) / 1000 : 9999;

let blocked = false;
let reason = '';
if (hourCount >= MAX_HOUR) {
  blocked = true;
  reason = 'hourly_limit';
} else if (burstCount >= MAX_5MIN) {
  blocked = true;
  reason = 'burst_limit';
} else if (sinceLastSec < MIN_INTERVAL) {
  blocked = true;
  reason = 'min_interval';
}

if (blocked) {
  const allowCritical = priority === 'critical' && hourCount < MAX_HOUR + 2 && burstCount < MAX_5MIN + 1;
  if (!allowCritical) {
    await logRow.call(this, { status: 'blocked', block_reason: reason });
    return [{
      json: {
        sent: false,
        blocked: true,
        reason,
        retryAfterSec: Math.max(1, Math.ceil(MIN_INTERVAL - sinceLastSec)),
        source,
        hourCount,
        burstCount,
      },
    }];
  }
  const waitMs = Math.max(0, (Math.min(15, MIN_INTERVAL) - sinceLastSec) * 1000);
  if (waitMs > 0) await sleep(waitMs);
} else if (sinceLastSec < MIN_INTERVAL) {
  await sleep((MIN_INTERVAL - sinceLastSec) * 1000);
}

const evoBase = ($env.EVOLUTION_API_URL || 'http://evolution-api:8080').replace(/\/$/, '');
const evoKey = $env.EVOLUTION_API_KEY;
const instance = $env.EVOLUTION_INSTANCE || 'medident-pilot';
if (!evoKey) {
  await logRow.call(this, { status: 'failed', block_reason: 'no_evolution_key' });
  return [{ json: { sent: false, error: 'EVOLUTION_API_KEY eksik' } }];
}

try {
  await this.helpers.httpRequest({
    method: 'POST',
    url: `${evoBase}/message/sendText/${instance}`,
    headers: { apikey: evoKey, 'Content-Type': 'application/json' },
    body: { number, text },
    json: true,
  });
  await logRow.call(this, { status: 'sent' });
  return [{ json: { sent: true, number, source, hourCount: hourCount + 1 } }];
} catch (e) {
  await logRow.call(this, { status: 'failed', block_reason: String(e.message || e).slice(0, 200) });
  return [{ json: { sent: false, error: String(e.message || e), source } }];
}
"""

GATEWAY_URL_EXPR = (
    "={{ ($env.WEBHOOK_URL || $env.N8N_WEBHOOK_URL || 'http://127.0.0.1:5678/')"
    ".replace(/\\/$/, '') + '/webhook/nefalix/whatsapp/send' }}"
)

NODE_SOURCES = {
    "Evolution NPS Gönder": ("wf-01", "nps-outbound", "normal"),
    "Evolution NPS Yanıt Gönder": ("wf-01", "nps-reply", "normal"),
    "Evolution Yönetici NPS Alarm": ("wf-01", "nps-manager-alert", "critical"),
    "Evolution Yöneticiye Bildir": ("wf-04", "sentinel-alert", "critical"),
    "Evolution Recall Gönder": ("wf-05", "recall", "normal"),
    "Evolution Gönder": ("wf-08", "inbox-send", "normal"),
}


def gateway_workflow() -> dict:
    return {
        "name": "Nefalix - WhatsApp Gateway",
        "nodes": [
            {
                "parameters": {
                    "content": "## WhatsApp Rate Limit Gateway\n\nTüm outbound WA bu webhook üzerinden.\n\n`WHATSAPP_MIN_INTERVAL_SEC` (45)\n`WHATSAPP_MAX_PER_HOUR` (20)\n`WHATSAPP_MAX_BURST_5MIN` (3)\n`WHATSAPP_SEND_ENABLED` (true/false)\n\nPOST `/webhook/nefalix/whatsapp/send`\n`{ number, text, source, priority? }`",
                    "height": 180,
                    "width": 420,
                    "color": 6,
                },
                "name": "Sticky Note",
                "type": "n8n-nodes-base.stickyNote",
                "typeVersion": 1,
                "position": [180, 60],
            },
            {
                "parameters": {
                    "httpMethod": "POST",
                    "path": "nefalix/whatsapp/send",
                    "responseMode": "lastNode",
                    "options": {},
                },
                "name": "WhatsApp Send Webhook",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 2.1,
                "position": [240, 280],
                "webhookId": "nefalix-whatsapp-send",
            },
            {
                "parameters": {"jsCode": GATEWAY_JS},
                "name": "Rate Limit + Gönder",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [520, 280],
            },
        ],
        "connections": {
            "WhatsApp Send Webhook": {
                "main": [[{"node": "Rate Limit + Gönder", "type": "main", "index": 0}]]
            }
        },
        "settings": {"executionOrder": "v1", "availableInMCP": False},
    }


def patch_evolution_node(node: dict, wf_file: str) -> bool:
    if node.get("type") != "n8n-nodes-base.httpRequest":
        return False
    url = node.get("parameters", {}).get("url", "")
    if "nefalix/whatsapp/send" in url:
        return False
    if "sendText" not in url and "EVOLUTION_API_URL" not in url:
        return False

    name = node.get("name", "")
    wf_id, source, priority = NODE_SOURCES.get(name, ("unknown", name.lower().replace(" ", "-"), "normal"))

    node["parameters"]["url"] = GATEWAY_URL_EXPR
    node["parameters"].pop("sendHeaders", None)
    node["parameters"].pop("headerParameters", None)

    body = node["parameters"].get("jsonBody", "")
    if "source:" not in body and "source'" not in body:
        m = re.search(r"JSON\.stringify\(\{([^}]+)\}\)", body)
        if m:
            inner = m.group(1).rstrip().rstrip(",")
            node["parameters"]["jsonBody"] = (
                f"={{ JSON.stringify({{ {inner}, source: '{source}', priority: '{priority}' }}) }}"
            )
    node["name"] = name.replace("Evolution ", "WA Gateway ")
    return True


def fix_connections(data: dict) -> None:
    """Bağlantı anahtarlarını yeniden adlandırılmış node isimleriyle eşle."""
    renames = {}
    for node in data.get("nodes", []):
        old = node.get("name", "")
        if old.startswith("WA Gateway "):
            old_name = old.replace("WA Gateway ", "Evolution ", 1)
            renames[old_name] = old

    if not renames:
        return

    conns = data.get("connections", {})
    new_conns = {}
    for key, val in conns.items():
        new_key = renames.get(key, key)
        new_main = []
        for branch in val.get("main", []):
            new_branch = []
            for link in branch:
                link = dict(link)
                if link.get("node") in renames:
                    link["node"] = renames[link["node"]]
                new_branch.append(link)
            new_main.append(new_branch)
        new_val = dict(val)
        if new_main:
            new_val["main"] = new_main
        ai = val.get("ai_languageModel") or val.get("ai_outputParser")
        if val.get("ai_languageModel"):
            new_val["ai_languageModel"] = []
            for branch in val["ai_languageModel"]:
                nb = []
                for link in branch:
                    link = dict(link)
                    if link.get("node") in renames:
                        link["node"] = renames[link["node"]]
                    nb.append(link)
                new_val["ai_languageModel"].append(nb)
        if val.get("ai_outputParser"):
            new_val["ai_outputParser"] = []
            for branch in val["ai_outputParser"]:
                nb = []
                for link in branch:
                    link = dict(link)
                    if link.get("node") in renames:
                        link["node"] = renames[link["node"]]
                    nb.append(link)
                new_val["ai_outputParser"].append(nb)
        new_conns[new_key] = new_val
    data["connections"] = new_conns


def patch_wf04(data: dict) -> None:
    """Sentinel: boş cron kapat, WA sadece kritik."""
    for node in data["nodes"]:
        if node["name"] == "Her 4 Saatte Tara":
            node["disabled"] = True
        if node["name"] == "Sticky Note":
            node["parameters"]["content"] = (
                "## Sentinel — İtibar analizi\n\n"
                "Webhook: `POST /webhook/nefalix/sentinel/mention`\n"
                "Google yeni düşük puanlı yorumlar wf-09 üzerinden otomatik gelir.\n\n"
                "WhatsApp yalnızca `alert_urgent` (kritik) → gateway rate limit."
            )

    data["connections"] = {
        "Mention Webhook": {"main": [[{"node": "Mention Normalize", "type": "main", "index": 0}]]},
        "Mention Normalize": {"main": [[{"node": "AI Duygu Analizi", "type": "main", "index": 0}]]},
        "Structured Output": {
            "ai_outputParser": [[{"node": "AI Duygu Analizi", "type": "ai_outputParser", "index": 0}]]
        },
        "AI Duygu Analizi": {"main": [[{"node": "Kritik mi?", "type": "main", "index": 0}]]},
        "Kritik mi?": {
            "main": [
                [{"node": "Yönetici Özet Mesajı", "type": "main", "index": 0}],
                [{"node": "Haftalık Rapora Ekle", "type": "main", "index": 0}],
            ]
        },
        "Yönetici Özet Mesajı": {
            "main": [[{"node": "WA Gateway Yöneticiye Bildir", "type": "main", "index": 0}]]
        },
        "WA Gateway Yöneticiye Bildir": {
            "main": [[{"node": "Kritik Alarm Log", "type": "main", "index": 0}]]
        },
        "Kritik Alarm Log": {"main": [[{"node": "Supabase Mention Kaydet", "type": "main", "index": 0}]]},
        "Haftalık Rapora Ekle": {"main": [[{"node": "Supabase Mention Kaydet", "type": "main", "index": 0}]]},
        "Gemini Vertex Model": {
            "ai_languageModel": [[{"node": "AI Duygu Analizi", "type": "ai_languageModel", "index": 0}]]
        },
    }


def patch_wf05(data: dict) -> None:
    for node in data["nodes"]:
        if node["name"] == "Günlük Kontrol":
            node["disabled"] = True


def patch_wf09(data: dict) -> None:
    for node in data["nodes"]:
        if node["name"] != "Google Senkron":
            continue
        code = node["parameters"]["jsCode"]
        if "sentinel/mention" in code:
            return
        sentinel_block = r"""
    const webhookBase = ($env.WEBHOOK_URL || $env.N8N_WEBHOOK_URL || 'http://127.0.0.1:5678/').replace(/\/$/, '');
    const sentinelHits = [];
"""
        code = code.replace(
            "const results = [];\n\nfor (const clinic of clinics)",
            "const results = [];\n" + sentinel_block + "\nfor (const clinic of clinics)",
        )
        insert = """
        if (inserted > 0 && review.rating <= 4 && text.trim()) {
          try {
            await this.helpers.httpRequest({
              method: 'POST',
              url: `${webhookBase}/webhook/nefalix/sentinel/mention`,
              headers: { 'Content-Type': 'application/json' },
              body: {
                source: 'google',
                brandName: clinic.name,
                text: `${author}: ${text}`,
                url: details.googleMapsUri || clinic.google_maps_url || '',
              },
              json: true,
            });
            sentinelHits.push({ clinic: clinic.name, rating: review.rating });
          } catch (_) { /* sentinel optional */ }
        }
"""
        code = code.replace(
            "        inserted++\n      }\n    }\n    results.push",
            "        inserted++\n" + insert + "      }\n    }\n    results.push",
        )
        code = code.replace(
            "return [{ json: { ok: true, at: new Date().toISOString(), results } }];",
            "return [{ json: { ok: true, at: new Date().toISOString(), results, sentinelHits } }];",
        )
        node["parameters"]["jsCode"] = code


def patch_wf13(data: dict) -> None:
    for node in data["nodes"]:
        if node["name"] != "Estesoft Poll":
            continue
        code = node["parameters"]["jsCode"]
        if "MAX_PER_RUN" in code:
            return
        code = code.replace(
            "const results = [];\n\nfor (const appt of appointments)",
            """const MAX_PER_RUN = Number($env.ESTESOFT_POLL_MAX_PER_RUN || 1);
const POLL_HOURS = Number($env.ESTESOFT_POLL_HOURS || 24);
const cutoff = Date.now() - POLL_HOURS * 3600000;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const results = [];
let triggeredThisRun = 0;

for (const appt of appointments)""",
        )
        loop_guard = """
  if (triggeredThisRun >= MAX_PER_RUN) {
    results.push({ id: appt.id, customerName: appt.customerName, skipped: true, reason: 'run_limit' });
    continue;
  }

  const rawDate = appt.appointmentDate || appt.startDate || appt.date || appt.endDate || appt.modifiedDate;
  if (rawDate) {
    const t = new Date(rawDate).getTime();
    if (!Number.isNaN(t) && t < cutoff) {
      results.push({ id: appt.id, customerName: appt.customerName, skipped: true, reason: 'too_old' });
      continue;
    }
  }
"""
        code = code.replace(
            "  if (await alreadyTriggered.call(this, extId)) {",
            loop_guard + "\n  if (await alreadyTriggered.call(this, extId)) {",
        )
        code = code.replace(
            "  results.push({ id: appt.id, customerName: appt.customerName, triggered: true });\n}",
            "  results.push({ id: appt.id, customerName: appt.customerName, triggered: true });\n  triggeredThisRun++;\n  if (triggeredThisRun < MAX_PER_RUN) await sleep(Number($env.WHATSAPP_MIN_INTERVAL_SEC || 45) * 1000);\n}",
        )
        node["parameters"]["jsCode"] = code
        if node.get("name") == "Estesoft Poll":
            pass
    for node in data["nodes"]:
        if node["name"] == "Sticky Note":
            node["parameters"]["content"] = (
                "## Estesoft poll (güvenli mod)\n\n"
                "Son `ESTESOFT_POLL_HOURS` (24s) Tamamlandı randevular.\n"
                "Koşu başına max `ESTESOFT_POLL_MAX_PER_RUN` (1) NPS.\n"
                "Aralık: `WHATSAPP_MIN_INTERVAL_SEC`."
            )


def main() -> None:
    (WF_DIR / "nefalix-00-whatsapp-gateway.json").write_text(
        json.dumps(gateway_workflow(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print("✓ nefalix-00-whatsapp-gateway.json")

    for path in sorted(WF_DIR.glob("nefalix-*.json")):
        if path.name == "nefalix-00-whatsapp-gateway.json":
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        changed = False
        if path.name == "nefalix-04-sentinel-reputation.json":
            patch_wf04(data)
            changed = True
        if path.name == "nefalix-05-recall-patient.json":
            patch_wf05(data)
            changed = True
        if path.name == "nefalix-09-google-reviews-sync.json":
            patch_wf09(data)
            changed = True
        if path.name == "nefalix-13-estesoft-poll.json":
            patch_wf13(data)
            changed = True
        for node in data.get("nodes", []):
            if patch_evolution_node(node, path.name):
                changed = True
        if any(n.get("name", "").startswith("WA Gateway ") for n in data.get("nodes", [])):
            fix_connections(data)
            changed = True
        if changed:
            path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            print(f"✓ patched {path.name}")


if __name__ == "__main__":
    main()
