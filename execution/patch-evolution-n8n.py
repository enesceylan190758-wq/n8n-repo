#!/usr/bin/env python3
"""Replace WhatsApp log stubs with Evolution API HTTP nodes."""
import json
from pathlib import Path

WORKFLOWS = Path(__file__).resolve().parent.parent / "workflows"

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
        "jsonBody": "",  # set per node
        "options": {},
    },
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "onError": "continueRegularOutput",
}


def evolution_node(name, position, json_body_expr, node_id=None):
    node = json.loads(json.dumps(EVOLUTION_SEND))
    node["name"] = name
    node["position"] = position
    node["parameters"]["jsonBody"] = json_body_expr
    if node_id:
        node["id"] = node_id
    return node


def replace_node(wf, old_name, new_node):
    nodes = wf["nodes"]
    for i, n in enumerate(nodes):
        if n.get("name") == old_name:
            new_node["id"] = n.get("id", new_node.get("id"))
            nodes[i] = new_node
            break
    conns = wf.get("connections", {})
    if old_name in conns:
        conns[new_node["name"]] = conns.pop(old_name)
    for key, val in list(conns.items()):
        if isinstance(val, dict) and "main" in val:
            for branch in val["main"]:
                for link in branch:
                    if link.get("node") == old_name:
                        link["node"] = new_node["name"]


def patch_01(wf):
    replace_node(
        wf,
        "WhatsApp NPS Log",
        evolution_node(
            "Evolution NPS Gönder",
            [900, 320],
            '={{ JSON.stringify({ number: String($(\'Normalize HBYS\').item.json.patientPhone || \'\').replace(/\\D/g, \'\'), text: $json.output || \'\' }) }}',
        ),
    )
    # NPS yanıt mesajı (promoter/detractor) — Supabase öncesi
    nodes = wf["nodes"]
    names = {n["name"] for n in nodes}
    if "Evolution NPS Yanıt Gönder" not in names:
        nodes.append(
            evolution_node(
                "Evolution NPS Yanıt Gönder",
                [1140, 680],
                '={{ JSON.stringify({ number: String($(\'NPS Skor Parse\').item.json.patientPhone || \'\').replace(/\\D/g, \'\'), text: $json.message || \'\' }) }}',
            )
        )
    conns = wf["connections"]
    for src in ("Promoter Google Link", "Kriz Alarm Log"):
        if src in conns:
            conns[src] = {"main": [[{"node": "Evolution NPS Yanıt Gönder", "type": "main", "index": 0}]]}
    conns["Evolution NPS Yanıt Gönder"] = {
        "main": [[{"node": "Supabase NPS Kaydet", "type": "main", "index": 0}]]
    }


def patch_05(wf):
    replace_node(
        wf,
        "WhatsApp Hatırlatma Log",
        evolution_node(
            "Evolution Recall Gönder",
            [1120, 300],
            '={{ JSON.stringify({ number: String($(\'Hasta Normalize\').item.json.patientPhone || \'\').replace(/\\D/g, \'\'), text: $(\'AI Hatırlatma Mesajı\').item.json.output || \'\' }) }}',
        ),
    )


def main():
    wf01 = json.loads((WORKFLOWS / "nefalix-01-feedback-reviews-loop.json").read_text())
    patch_01(wf01)
    (WORKFLOWS / "nefalix-01-feedback-reviews-loop.json").write_text(
        json.dumps(wf01, indent=2, ensure_ascii=False) + "\n"
    )

    wf05 = json.loads((WORKFLOWS / "nefalix-05-recall-patient.json").read_text())
    patch_05(wf05)
    (WORKFLOWS / "nefalix-05-recall-patient.json").write_text(
        json.dumps(wf05, indent=2, ensure_ascii=False) + "\n"
    )
    print("✓ Patched 01 Feedback + 05 Recall")


if __name__ == "__main__":
    main()
