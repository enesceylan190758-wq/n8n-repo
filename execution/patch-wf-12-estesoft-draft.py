#!/usr/bin/env python3
"""wf-12: Estesoft tamamlandı → AI NPS taslak → inbox (gönderim yok)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WF = ROOT / "workflows" / "nefalix-12-estesoft-adapter.json"

INBOX_SAVE = r"""const item = $('Dedup Kontrol').first().json;
const ai = $('AI NPS Taslak').first().json;
const draft = String(ai.output || ai.text || '').trim();
if (!draft) throw new Error('AI NPS taslak üretilemedi');

const sbBase = ($env.SUPABASE_URL || 'http://host.docker.internal:54321').replace(/\/$/, '');
const sbKey = $env.SUPABASE_SERVICE_ROLE_KEY;
if (!sbKey) throw new Error('SUPABASE_SERVICE_ROLE_KEY eksik');

const phone = String(item.patientPhone || '').replace(/\D/g, '');
const treatment = item.treatment || 'tedavi';
const doctor = item.doctorName || '';
const summary = `Estesoft: ${treatment}${doctor ? ` · ${doctor}` : ''} tamamlandı — NPS taslak onayı bekliyor`;

const row = await this.helpers.httpRequest({
  method: 'POST',
  url: `${sbBase}/rest/v1/inbox_messages`,
  headers: {
    apikey: sbKey,
    Authorization: `Bearer ${sbKey}`,
    'Content-Type': 'application/json',
    Prefer: 'return=representation',
  },
  body: {
    clinic_id: item.clinic_id,
    channel: 'whatsapp',
    direction: 'outbound',
    message_kind: 'estesoft_nps',
    body: summary,
    ai_draft_reply: draft,
    sender_phone: phone,
    sender_name: item.patientName || 'Hasta',
    status: 'draft_ready',
    metadata: {
      appointmentId: item.appointmentId,
      treatment: item.treatment,
      doctorName: item.doctorName,
      source: 'estesoft',
    },
  },
  json: true,
});

return [{ json: { ok: true, row, appointmentId: item.appointmentId, draft } }];"""


def main() -> None:
    data = json.loads(WF.read_text())

    # Remove old auto-send node
    data["nodes"] = [n for n in data["nodes"] if n.get("name") != "NPS Akışını Tetikle"]

    for n in data["nodes"]:
        if n.get("name") == "Sticky Note":
            n["parameters"]["content"] = (
                "## Estesoft → NPS Taslak (onaylı gönderim)\n\n"
                "Randevu **Tamamlandı** → AI NPS metni → `inbox_messages` (message_kind=estesoft_nps).\n"
                "**Otomatik WhatsApp gönderilmez** — yönetici dashboard'dan onaylar.\n\n"
                "Webhook: `POST /webhook/nefalix/estesoft/webhook`"
            )
        if n.get("name") == "Dedup Kaydet":
            n["parameters"]["jsCode"] = n["parameters"]["jsCode"].replace(
                "source: 'adapter'",
                "source: 'adapter_draft'",
            )

    data["nodes"].extend(
        [
            {
                "parameters": {
                    "promptType": "define",
                    "text": "=Randevu/tedavi tamamlandı. Hastaya WhatsApp ile NPS anketi gönderilecek (yönetici onayından sonra).\n\nHasta: {{ $('Dedup Kontrol').item.json.patientName }}\nKlinik: {{ $('Dedup Kontrol').item.json.clinicName }}\nDoktor: {{ $('Dedup Kontrol').item.json.doctorName }}\nTedavi: {{ $('Dedup Kontrol').item.json.treatment }}\n\nMesaj şunları içersin:\n1) Teşekkür ve kısa samimi giriş\n2) \"Deneyiminizi 1-10 arası puanlar mısınız?\" sorusu (tek net soru)\n3) Puanı bu sohbette yazabileceğini belirt\n\nKVKK uyumlu, Türkçe, max 4 cümle. Sadece mesaj metnini döndür.",
                    "options": {"maxIterations": 3, "enableStreaming": False},
                },
                "name": "AI NPS Taslak",
                "type": "@n8n/n8n-nodes-langchain.agent",
                "typeVersion": 3.1,
                "position": [1360, 260],
            },
            {
                "parameters": {
                    "projectId": {"__rl": True, "mode": "id", "value": "={{ $env.GCP_PROJECT_ID }}"},
                    "modelName": "gemini-2.5-flash",
                    "options": {"temperature": 0.4, "maxOutputTokens": 2048},
                },
                "name": "Gemini NPS Model",
                "type": "@n8n/n8n-nodes-langchain.lmChatGoogleVertex",
                "typeVersion": 1,
                "position": [1360, 480],
            },
            {
                "parameters": {"jsCode": INBOX_SAVE},
                "name": "Inbox Taslak Kaydet",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [1580, 260],
            },
        ]
    )

    data["connections"] = {
        "Estesoft Webhook": {"main": [[{"node": "Estesoft Normalize", "type": "main", "index": 0}]]},
        "Estesoft Normalize": {"main": [[{"node": "Tamamlandı mı?", "type": "main", "index": 0}]]},
        "Tamamlandı mı?": {"main": [[{"node": "Dedup Kontrol", "type": "main", "index": 0}], []]},
        "Dedup Kontrol": {"main": [[{"node": "Yeni randevu?", "type": "main", "index": 0}]]},
        "Yeni randevu?": {"main": [[{"node": "AI NPS Taslak", "type": "main", "index": 0}], []]},
        "AI NPS Taslak": {"main": [[{"node": "Inbox Taslak Kaydet", "type": "main", "index": 0}]]},
        "Inbox Taslak Kaydet": {"main": [[{"node": "Dedup Kaydet", "type": "main", "index": 0}]]},
        "Gemini NPS Model": {
            "ai_languageModel": [[{"node": "AI NPS Taslak", "type": "ai_languageModel", "index": 0}]]
        },
    }

    WF.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(f"patched {WF.name}")


if __name__ == "__main__":
    main()
