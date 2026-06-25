#!/usr/bin/env python3
"""Notlardan gelen prompt + yönetici WhatsApp bildirim yamaları."""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
WORKFLOWS = REPO / "workflows"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from nefalix_prompts import (  # noqa: E402
    NPS_APPOINTMENT_SURVEY,
    SENTINEL_SENTIMENT,
    WHATSAPP_INBOX_AGENT,
)

MANAGER_NUMBER = "String($env.CLINIC_MANAGER_WHATSAPP || '905491190819').replace(/\\D/g, '')"

EVOLUTION_SEND = {
    "parameters": {
        "method": "POST",
        "url": "={{ $env.EVOLUTION_API_URL }}/message/sendText/{{ $env.EVOLUTION_INSTANCE }}",
        "sendHeaders": True,
        "headerParameters": {
            "parameters": [
                {"name": "apikey", "value": "={{ $env.EVOLUTION_API_KEY }}"},
                {"name": "Content-Type", "value": "application/json"},
            ]
        },
        "sendBody": True,
        "specifyBody": "json",
        "jsonBody": "",
        "options": {},
    },
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "onError": "continueRegularOutput",
}


def evo_node(name, pos, body_expr):
    n = json.loads(json.dumps(EVOLUTION_SEND))
    n["name"] = name
    n["position"] = pos
    n["parameters"]["jsonBody"] = body_expr
    return n


def set_agent_prompt(wf, node_name, text):
    for n in wf["nodes"]:
        if n.get("name") == node_name and "parameters" in n:
            n["parameters"]["text"] = "=" + text
            return True
    return False


def ensure_node(wf, node):
    names = {n["name"] for n in wf["nodes"]}
    if node["name"] not in names:
        wf["nodes"].append(node)
    else:
        for i, n in enumerate(wf["nodes"]):
            if n["name"] == node["name"]:
                node["id"] = n.get("id")
                wf["nodes"][i] = node
                break


def patch_inbox(wf):
    set_agent_prompt(wf, "AI Taslak Yanıt", WHATSAPP_INBOX_AGENT)


def patch_nps(wf):
    set_agent_prompt(wf, "AI NPS Mesajı", NPS_APPOINTMENT_SURVEY)

    ensure_node(
        wf,
        evo_node(
            "Evolution Yönetici NPS Alarm",
            [1320, 780],
            f'={{ JSON.stringify({{ number: String($env.CLINIC_MANAGER_WHATSAPP || \\'905491190819\\').replace(/\\\\D/g, \\'\\'), text: $(\\'Detractor Şikayet\\').item.json.alertMessage + \\'\\\\n\\\\nBu hasta Google\\\\\\'da olumsuz yorum yazmadan önce görüşmeniz önerilir. Panel: nefalixai.com/dashboard\\' }}) }}',
        ),
    )
    conns = wf.setdefault("connections", {})
    conns["Kriz Alarm Log"] = {
        "main": [[{"node": "Evolution Yönetici NPS Alarm", "type": "main", "index": 0}]]
    }
    conns["Evolution Yönetici NPS Alarm"] = {
        "main": [[{"node": "Evolution NPS Yanıt Gönder", "type": "main", "index": 0}]]
    }


def patch_sentinel(wf):
    set_agent_prompt(wf, "AI Duygu Analizi", SENTINEL_SENTIMENT)

    for n in wf["nodes"]:
        if n.get("name") == "Structured Output":
            schema = n["parameters"].get("jsonSchemaExample", "")
            if "managerBrief" not in schema:
                n["parameters"]["jsonSchemaExample"] = (
                    '{\n  "sentiment": "negative",\n  "riskScore": 8,\n'
                    '  "summary": "Şikayetvar\'da bekleme süresi şikayeti",\n'
                    '  "recommendedAction": "alert_urgent",\n'
                    '  "managerBrief": "Firmanızla ilgili olumsuz bir paylaşım tespit edildi. '
                    'Bekleme süresi eleştirisi var; hasta memnuniyetsizliği riski yüksek. '
                    'İncelemenizi öneririm."\n}'
                )
            break

    ensure_node(
        wf,
        {
            "parameters": {
                "assignments": {
                    "assignments": [
                        {
                            "id": "1",
                            "name": "managerAlertText",
                            "value": "=📊 *Nefalix Sentinel* — İtibar analizi\n\nFirma: {{ $('Mention Normalize').item.json.brandName }}\nKaynak: {{ $('Mention Normalize').item.json.source }}\nDuygu: {{ $json.output.sentiment }} | Risk: {{ $json.output.riskScore }}/10\n\n{{ $json.output.managerBrief || $json.output.summary }}\n\nÖneri: {{ $json.output.recommendedAction }}\n{{ $('Mention Normalize').item.json.url ? '🔗 ' + $('Mention Normalize').item.json.url : '' }}\n\nİncelemeniz önerilir → nefalixai.com/dashboard",
                            "type": "string",
                        }
                    ]
                },
                "options": {},
            },
            "name": "Yönetici Özet Mesajı",
            "type": "n8n-nodes-base.set",
            "typeVersion": 3.4,
            "position": [920, 520],
        },
    )
    ensure_node(
        wf,
        evo_node(
            "Evolution Yöneticiye Bildir",
            [1140, 520],
            f"={{ JSON.stringify({{ number: String($env.CLINIC_MANAGER_WHATSAPP || '905491190819').replace(/\\\\D/g, ''), text: $json.managerAlertText || '' }}) }}",
        ),
    )

    conns = wf.setdefault("connections", {})
    conns["AI Duygu Analizi"] = {
        "main": [[{"node": "Yönetici Özet Mesajı", "type": "main", "index": 0}]]
    }
    conns["Yönetici Özet Mesajı"] = {
        "main": [[{"node": "Evolution Yöneticiye Bildir", "type": "main", "index": 0}]]
    }
    conns["Evolution Yöneticiye Bildir"] = {
        "main": [[{"node": "Kritik mi?", "type": "main", "index": 0}]]
    }


def main():
    wf06 = json.loads((WORKFLOWS / "nefalix-06-inbox-routing.json").read_text())
    patch_inbox(wf06)
    (WORKFLOWS / "nefalix-06-inbox-routing.json").write_text(
        json.dumps(wf06, indent=2, ensure_ascii=False) + "\n"
    )

    wf01 = json.loads((WORKFLOWS / "nefalix-01-feedback-reviews-loop.json").read_text())
    patch_nps(wf01)
    (WORKFLOWS / "nefalix-01-feedback-reviews-loop.json").write_text(
        json.dumps(wf01, indent=2, ensure_ascii=False) + "\n"
    )

    wf04 = json.loads((WORKFLOWS / "nefalix-04-sentinel-reputation.json").read_text())
    patch_sentinel(wf04)
    (WORKFLOWS / "nefalix-04-sentinel-reputation.json").write_text(
        json.dumps(wf04, indent=2, ensure_ascii=False) + "\n"
    )

    print("✓ Prompt + yönetici WhatsApp yamaları uygulandı (01, 04, 06)")


if __name__ == "__main__":
    main()
