#!/usr/bin/env python3
"""wf-06: WhatsApp NPS puanı → wf-01. wf-08: outbound NPS işareti. wf-01: hasta mesajı priority."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WF06 = ROOT / "workflows" / "nefalix-06-inbox-routing.json"
WF01 = ROOT / "workflows" / "nefalix-01-feedback-reviews-loop.json"
WF08 = ROOT / "workflows" / "nefalix-08-inbox-send.json"

NPS_CHECK = r"""const base = ($env.SUPABASE_URL || 'http://host.docker.internal:54321').replace(/\/$/, '');
const key = $env.SUPABASE_SERVICE_ROLE_KEY;
if (!key) throw new Error('SUPABASE_SERVICE_ROLE_KEY eksik');

const ctx = $('Sohbet Geçmişi').first().json;
const phone = String(ctx.phone || '').replace(/\D/g, '');
const clinicId = ctx.clinic_id || '51738ea8-c12e-40ce-a0e2-42869496d76b';
const msg = String(ctx.originalMessage || ctx.message || '').trim();
const headers = { apikey: key, Authorization: `Bearer ${key}` };
const npsHint = /1\s*[-–]\s*10|puanlar\s*mısınız|puanlay|memnuniyet|değerlendir/i;
const NPS_WINDOW_MS = 7 * 24 * 3600000;

function parseScore(text) {
  const t = String(text || '').trim();
  const patterns = [
    /^(?:puan\s*)?(\d{1,2})(?:\s*\/\s*10)?$/i,
    /\b(\d{1,2})\s*\/\s*10\b/,
    /^(?:puan\s*)?(\d{1,2})\s*puan$/i,
  ];
  if (t.length <= 12) patterns.push(/(?:^|\s)(\d{1,2})(?:\s|$)/);
  for (const re of patterns) {
    const m = t.match(re);
    if (!m) continue;
    const n = Number(m[1]);
    if (n >= 1 && n <= 10) return n;
  }
  return null;
}

const score = parseScore(msg);

let rows = [];
let sendLogs = [];
if (phone) {
  rows = await this.helpers.httpRequest({
    method: 'GET',
    url: `${base}/rest/v1/inbox_messages?clinic_id=eq.${clinicId}&sender_phone=eq.${phone}&channel=eq.whatsapp&order=created_at.desc&limit=20`,
    headers,
    json: true,
  });
  sendLogs = await this.helpers.httpRequest({
    method: 'GET',
    url: `${base}/rest/v1/whatsapp_send_log?phone=eq.${phone}&order=created_at.desc&limit=15&select=created_at,message_preview,source_workflow`,
    headers,
    json: true,
  }).catch(() => []);
}

const cutoff = Date.now() - NPS_WINDOW_MS;
const recent = (rows || []).filter((r) => new Date(r.created_at).getTime() >= cutoff);

const surveyTimes = [];
for (const r of recent) {
  if (r.direction === 'outbound' && (npsHint.test(r.body || '') || r.metadata?.npsSurvey)) {
    surveyTimes.push(new Date(r.created_at).getTime());
  }
  if (r.message_kind === 'estesoft_nps' && r.status === 'replied') {
    surveyTimes.push(new Date(r.created_at).getTime());
  }
}
for (const s of sendLogs || []) {
  if (new Date(s.created_at).getTime() >= cutoff && npsHint.test(s.message_preview || '')) {
    surveyTimes.push(new Date(s.created_at).getTime());
  }
}

const lastSurveyMs = surveyTimes.length ? Math.max(...surveyTimes) : 0;
const awaitingNps = lastSurveyMs > 0 && Date.now() - lastSurveyMs < NPS_WINDOW_MS;

const lastScoreMs = Math.max(
  0,
  ...recent
    .filter((r) => r.direction === 'inbound' && r.metadata?.npsScore != null)
    .map((r) => new Date(r.created_at).getTime()),
);

const duplicateRecent = lastSurveyMs > 0 && lastScoreMs >= lastSurveyMs;
const isNpsScore = Boolean(score && awaitingNps && !duplicateRecent);

return [{
  json: {
    ...ctx,
    npsScore: score,
    isNpsScore,
    awaitingNps,
    duplicateRecent,
    lastSurveyMs: lastSurveyMs ? new Date(lastSurveyMs).toISOString() : null,
  },
}];"""

NPS_TRIGGER = r"""const base = ($env.SUPABASE_URL || 'http://host.docker.internal:54321').replace(/\/$/, '');
const key = $env.SUPABASE_SERVICE_ROLE_KEY;
const item = $('NPS Skor Kontrol').first().json;
const score = item.npsScore;
const phone = String(item.phone || '').replace(/\D/g, '');
const clinicId = item.clinic_id || '51738ea8-c12e-40ce-a0e2-42869496d76b';
const headers = { apikey: key, Authorization: `Bearer ${key}`, 'Content-Type': 'application/json' };

const clinics = await this.helpers.httpRequest({
  method: 'GET',
  url: `${base}/rest/v1/clinics?id=eq.${clinicId}&select=name,google_review_url,google_maps_url,complaint_form_url,sikayetvar_url&limit=1`,
  headers,
  json: true,
});
const clinic = Array.isArray(clinics) && clinics[0] ? clinics[0] : {};

const webhookBase = ($env.WEBHOOK_URL || $env.N8N_WEBHOOK_URL || 'http://127.0.0.1:5678/').replace(/\/$/, '');
const payload = {
  score,
  patientName: item.patientName || 'Hasta',
  patientPhone: phone,
  googleMapsUrl: clinic.google_maps_url || clinic.google_review_url || '',
  googleReviewUrl: clinic.google_maps_url || clinic.google_review_url || '',
  complaintFormUrl: clinic.complaint_form_url || clinic.sikayetvar_url || '',
};

const npsRes = await this.helpers.httpRequest({
  method: 'POST',
  url: `${webhookBase}/webhook/nefalix/nps/response`,
  headers: { ...headers, Accept: 'application/json' },
  body: payload,
  json: true,
});

const flow = npsRes?.flow || npsRes?.json?.flow || null;

await this.helpers.httpRequest({
  method: 'POST',
  url: `${base}/rest/v1/inbox_messages`,
  headers: { ...headers, Prefer: 'return=minimal' },
  body: {
    clinic_id: clinicId,
    channel: 'whatsapp',
    direction: 'inbound',
    message_kind: 'inbound',
    body: String(score),
    sender_phone: phone,
    sender_name: item.patientName || 'Hasta',
    status: 'replied',
    metadata: { npsScore: score, flow, npsHandled: true },
  },
  json: true,
});

return [{ json: { ok: true, score, flow, nps: npsRes } }];"""

WF08_SAVE = r"""const base = ($env.SUPABASE_URL || 'http://host.docker.internal:54321').replace(/\/$/, '');
const key = $env.SUPABASE_SERVICE_ROLE_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0.EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU';
const PILOT = '51738ea8-c12e-40ce-a0e2-42869496d76b';
const req = $('Parse İstek').item.json;
const messageId = req.messageId;
const phone = req.phone || '';
const text = req.text || '';
let CLINIC_ID = req.clinicId || PILOT;
const headers = {
  apikey: key,
  Authorization: `Bearer ${key}`,
  'Content-Type': 'application/json',
  Prefer: 'return=minimal',
};

let srcKind = '';
let npsSurvey = /1\s*[-–]\s*10|puanlar\s*mısınız|puanlay|memnuniyet|değerlendir/i.test(text);

if (!req.clinicId && messageId) {
  const rows = await this.helpers.httpRequest({
    method: 'GET',
    url: `${base}/rest/v1/inbox_messages?id=eq.${messageId}&select=clinic_id,message_kind,ai_draft_reply&limit=1`,
    headers,
    json: true,
  });
  if (rows?.[0]?.clinic_id) CLINIC_ID = rows[0].clinic_id;
  srcKind = rows?.[0]?.message_kind || '';
  if (srcKind === 'estesoft_nps') npsSurvey = true;
}

if (messageId) {
  await this.helpers.httpRequest({
    method: 'PATCH',
    url: `${base}/rest/v1/inbox_messages?id=eq.${messageId}`,
    headers,
    body: { status: 'replied' },
    json: true,
  });
}

if (phone && text) {
  await this.helpers.httpRequest({
    method: 'POST',
    url: `${base}/rest/v1/inbox_messages`,
    headers,
    body: {
      clinic_id: CLINIC_ID,
      channel: 'whatsapp',
      direction: 'outbound',
      message_kind: srcKind === 'estesoft_nps' ? 'estesoft_nps' : 'inbound',
      body: text,
      sender_phone: phone,
      status: 'replied',
      metadata: npsSurvey ? { npsSurvey: true, source: srcKind || 'inbox-send' } : {},
    },
    json: true,
  });
}

return [{ json: { ok: true, updated: Boolean(messageId), outboundLogged: Boolean(phone && text), clinicId: CLINIC_ID, npsSurvey } }];"""

WF01_DISABLE = {
    "HBYS Randevu Bitti",
    "Normalize HBYS",
    "AI NPS Mesajı",
    "WA Gateway NPS Gönder",
    "Gemini Vertex Model",
}


def patch_wf06() -> None:
    data = json.loads(WF06.read_text())
    names = {n["name"] for n in data["nodes"]}
    if "NPS Skor Kontrol" not in names:
        data["nodes"].extend(
            [
                {
                    "parameters": {"jsCode": NPS_CHECK},
                    "name": "NPS Skor Kontrol",
                    "type": "n8n-nodes-base.code",
                    "typeVersion": 2,
                    "position": [700, 300],
                },
                {
                    "parameters": {
                        "conditions": {
                            "options": {
                                "caseSensitive": True,
                                "leftValue": "",
                                "typeValidation": "strict",
                            },
                            "conditions": [
                                {
                                    "id": "nps",
                                    "leftValue": "={{ $json.isNpsScore }}",
                                    "rightValue": True,
                                    "operator": {
                                        "type": "boolean",
                                        "operation": "equals",
                                    },
                                }
                            ],
                            "combinator": "and",
                        },
                        "options": {},
                    },
                    "name": "NPS Skoru mu?",
                    "type": "n8n-nodes-base.if",
                    "typeVersion": 2.2,
                    "position": [920, 300],
                },
                {
                    "parameters": {"jsCode": NPS_TRIGGER},
                    "name": "NPS Yanıt Tetikle",
                    "type": "n8n-nodes-base.code",
                    "typeVersion": 2,
                    "position": [1140, 200],
                },
            ]
        )

    for node in data["nodes"]:
        if node["name"] == "NPS Skor Kontrol":
            node["parameters"]["jsCode"] = NPS_CHECK
        if node["name"] == "NPS Yanıt Tetikle":
            node["parameters"]["jsCode"] = NPS_TRIGGER

    data["connections"]["Sohbet Geçmişi"] = {
        "main": [[{"node": "NPS Skor Kontrol", "type": "main", "index": 0}]]
    }
    data["connections"]["NPS Skor Kontrol"] = {
        "main": [[{"node": "NPS Skoru mu?", "type": "main", "index": 0}]]
    }
    data["connections"]["NPS Skoru mu?"] = {
        "main": [
            [{"node": "NPS Yanıt Tetikle", "type": "main", "index": 0}],
            [{"node": "AI Taslak Yanıt", "type": "main", "index": 0}],
        ]
    }

    WF06.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print("✓ wf-06 NPS skor dalı")


def patch_wf01() -> None:
    data = json.loads(WF01.read_text())
    for node in data["nodes"]:
        if node["name"] in WF01_DISABLE:
            node["disabled"] = True
        elif node["name"] == "Supabase NPS Kaydet":
            fields = node["parameters"]["fieldsUi"]["fieldValues"]
            for f in fields:
                if f["fieldId"] == "flow":
                    f["fieldValue"] = (
                        "={{ $('Promoter Google Link').isExecuted "
                        "? $('Promoter Google Link').item.json.flow "
                        ": $('Detractor Şikayet').item.json.flow }}"
                    )
                if f["fieldId"] == "message_sent":
                    f["fieldValue"] = (
                        "={{ $('Promoter Google Link').isExecuted "
                        "? $('Promoter Google Link').item.json.message "
                        ": $('Detractor Şikayet').item.json.message }}"
                    )
        elif node["name"] == "WA Gateway NPS Yanıt Gönder":
            body = node["parameters"].get("jsonBody", "")
            if "priority: 'normal'" in body or 'priority: "normal"' in body:
                node["parameters"]["jsonBody"] = body.replace(
                    "priority: 'normal'", "priority: 'critical'"
                ).replace('priority: "normal"', "priority: 'critical'")
    WF01.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print("✓ wf-01 NPS yanıt priority + kayıt")


def patch_wf08() -> None:
    data = json.loads(WF08.read_text())
    for node in data["nodes"]:
        if node["name"] == "Supabase Durum Güncelle":
            node["parameters"]["jsCode"] = WF08_SAVE
    WF08.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print("✓ wf-08 outbound NPS işareti")


def main() -> None:
    patch_wf06()
    patch_wf01()
    patch_wf08()


if __name__ == "__main__":
    main()
