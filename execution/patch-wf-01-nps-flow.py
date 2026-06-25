#!/usr/bin/env python3
"""wf-01 NPS akışı: 8+ Google Maps, 7- hasta önce → yönetici alarm + panel."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WF01 = ROOT / "workflows" / "nefalix-01-feedback-reviews-loop.json"

PANEL_ALARM = r"""const detractor = $('Detractor Şikayet').first()?.json;
if (!detractor) {
  return [{ json: { panelAlert: false } }];
}

const parse = $('NPS Skor Parse').first().json;
const base = ($env.SUPABASE_URL || 'http://host.docker.internal:54321').replace(/\/$/, '');
const key = $env.SUPABASE_SERVICE_ROLE_KEY;
if (!key) throw new Error('SUPABASE_SERVICE_ROLE_KEY eksik');

const clinicId = '51738ea8-c12e-40ce-a0e2-42869496d76b';
const phone = String(parse.patientPhone || '').replace(/\D/g, '');
const score = Number(parse.score || 0);
const name = String(parse.patientName || 'Hasta').trim();
const alertBody = [
  `🚨 Düşük NPS: ${score}/10`,
  `Hasta: ${name}`,
  phone ? `Tel: +${phone}` : '',
  '',
  'Hastayı arayıp gönül alın; Google olumsuz yorumdan önce sorunu çözün.',
].filter(Boolean).join('\n');

await this.helpers.httpRequest({
  method: 'POST',
  url: `${base}/rest/v1/inbox_messages`,
  headers: {
    apikey: key,
    Authorization: `Bearer ${key}`,
    'Content-Type': 'application/json',
    Prefer: 'return=minimal',
  },
  body: {
    clinic_id: clinicId,
    channel: 'whatsapp',
    direction: 'inbound',
    message_kind: 'nps_alert',
    body: alertBody,
    sender_phone: phone,
    sender_name: name,
    status: 'open',
    metadata: {
      npsScore: score,
      flow: 'detractor',
      needsManagerCall: true,
      alertMessage: detractor.alertMessage,
    },
  },
  json: true,
});

return [{ json: { panelAlert: true, score, phone, name } }];"""


def main() -> None:
    data = json.loads(WF01.read_text())
    nodes = {n["name"]: n for n in data["nodes"]}

    # Mesaj metinleri
    nodes["Promoter Google Link"]["parameters"]["assignments"]["assignments"][0]["value"] = (
        "=Teşekkürler {{ $json.patientName }}! Memnuniyetiniz bizi çok mutlu etti. "
        "Google'da 5 yıldız verip kısa bir yorum yazar mısınız? "
        "{{ $json.googleMapsUrl || $json.googleReviewUrl }}"
    )
    nodes["Detractor Şikayet"]["parameters"]["assignments"]["assignments"][0]["value"] = (
        "=Teşekkürler {{ $json.patientName }}, geri bildiriminizi aldık. "
        "Yaşadığınız sorunu çözmek için en kısa sürede sizinle iletişime geçeceğiz."
    )
    nodes["Detractor Şikayet"]["parameters"]["assignments"]["assignments"][2]["value"] = (
        "=🚨 DÜŞÜK NPS — ARAYIN\\n\\n"
        "Hasta: {{ $json.patientName }}\\n"
        "Tel: {{ $json.patientPhone }}\\n"
        "Puan: {{ $json.score }}/10\\n\\n"
        "Hastayı arayıp gönül alın. Google'da olumsuz yorum yazmadan önce sorunu çözün."
    )

    # NPS Skor Parse — googleMapsUrl
    for a in nodes["NPS Skor Parse"]["parameters"]["assignments"]["assignments"]:
        if a.get("name") == "googleReviewUrl":
            a["name"] = "googleMapsUrl"
            a["value"] = "={{ $json.body?.googleMapsUrl ?? $json.body?.googleReviewUrl ?? $json.googleMapsUrl ?? $json.googleReviewUrl }}"
            break
    else:
        nodes["NPS Skor Parse"]["parameters"]["assignments"]["assignments"].append(
            {
                "id": "6",
                "name": "googleMapsUrl",
                "value": "={{ $json.body?.googleMapsUrl ?? $json.body?.googleReviewUrl ?? $json.googleMapsUrl ?? $json.googleReviewUrl }}",
                "type": "string",
            }
        )

    # Supabase — hasta bilgisi
    fields = nodes["Supabase NPS Kaydet"]["parameters"]["fieldsUi"]["fieldValues"]
    extra = [
        ("patient_name", "={{ $('NPS Skor Parse').item.json.patientName }}"),
        ("patient_phone", "={{ $('NPS Skor Parse').item.json.patientPhone }}"),
        ("resolution_status", "={{ $('Detractor Şikayet').isExecuted ? 'open' : '' }}"),
    ]
    existing = {f["fieldId"] for f in fields}
    for fid, val in extra:
        if fid not in existing:
            fields.append({"fieldId": fid, "fieldValue": val})

    # Yeni node'lar
    if "Detractor mu?" not in nodes:
        data["nodes"].append(
            {
                "parameters": {
                    "conditions": {
                        "options": {
                            "caseSensitive": True,
                            "leftValue": "",
                            "typeValidation": "loose",
                        },
                        "conditions": [
                            {
                                "id": "det",
                                "leftValue": "={{ $('Detractor Şikayet').isExecuted }}",
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
                "name": "Detractor mu?",
                "type": "n8n-nodes-base.if",
                "typeVersion": 2.2,
                "position": [1260, 680],
            }
        )
    if "Panel NPS Alarm Kaydet" not in nodes:
        data["nodes"].append(
            {
                "parameters": {"jsCode": PANEL_ALARM},
                "name": "Panel NPS Alarm Kaydet",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [1540, 780],
            }
        )

    sticky = nodes.get("Sticky Note")
    if sticky:
        sticky["parameters"]["content"] = (
            "## NPS Yanıt (aktif)\n\n"
            "Estesoft taslak → yönetici onay → anket.\n"
            "8–10: Google Maps + 5 yıldız/yorum iste.\n"
            "7 ve altı: kısa hasta mesajı → yönetici WhatsApp + panel alarm."
        )

    data["connections"] = {
        **data["connections"],
        "Detractor Şikayet": {
            "main": [[{"node": "WA Gateway NPS Yanıt Gönder", "type": "main", "index": 0}]]
        },
        "WA Gateway NPS Yanıt Gönder": {
            "main": [[{"node": "Detractor mu?", "type": "main", "index": 0}]]
        },
        "Detractor mu?": {
            "main": [
                [{"node": "WA Gateway Yönetici NPS Alarm", "type": "main", "index": 0}],
                [{"node": "Supabase NPS Kaydet", "type": "main", "index": 0}],
            ]
        },
        "WA Gateway Yönetici NPS Alarm": {
            "main": [[{"node": "Panel NPS Alarm Kaydet", "type": "main", "index": 0}]]
        },
        "Panel NPS Alarm Kaydet": {
            "main": [[{"node": "Supabase NPS Kaydet", "type": "main", "index": 0}]]
        },
    }
    # Kriz Alarm Log artık zincirde değil
    data["connections"].pop("Kriz Alarm Log", None)

    WF01.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    print("✓ wf-01 NPS akışı güncellendi")


if __name__ == "__main__":
    main()
