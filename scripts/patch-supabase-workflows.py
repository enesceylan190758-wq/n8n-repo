#!/usr/bin/env python3
"""Add Supabase save nodes to Nefalix workflows."""
import json
import copy
from pathlib import Path

WORKFLOWS = Path(__file__).resolve().parent.parent / "workflows"
CRED = {"supabaseApi": {"id": "UYVzTr3Rfadp18iR", "name": "Nefalix Supabase Local"}}
CLINIC_ID = "51738ea8-c12e-40ce-a0e2-42869496d76b"


def supabase_node(name, table, fields, position):
    return {
        "parameters": {
            "useCustomSchema": False,
            "resource": "row",
            "operation": "create",
            "tableId": table,
            "dataToSend": "defineBelow",
            "fieldsUi": {
                "fieldValues": [
                    {"fieldId": fid, "fieldValue": val} for fid, val in fields
                ]
            },
        },
        "name": name,
        "type": "n8n-nodes-base.supabase",
        "typeVersion": 1,
        "position": position,
        "credentials": copy.deepcopy(CRED),
    }


def event_node(workflow_name, event_type, expr_payload, position):
    return supabase_node(
        "Supabase Event Log",
        "automation_events",
        [
            ("workflow_name", workflow_name),
            ("event_type", event_type),
            ("payload", expr_payload),
            ("status", "success"),
        ],
        position,
    )


def patch_feedback(wf):
    node = supabase_node(
        "Supabase NPS Kaydet",
        "nps_responses",
        [
            ("clinic_id", CLINIC_ID),
            ("score", "={{ $('NPS Skor Parse').item.json.score }}"),
            ("flow", "={{ $json.flow }}"),
            ("message_sent", "={{ $json.message }}"),
        ],
        [1320, 680],
    )
    wf["nodes"].append(node)
    c = wf["connections"]
    c["Promoter Google Link"] = {"main": [[{"node": "Supabase NPS Kaydet", "type": "main", "index": 0}]]}
    c["Kriz Alarm Log"] = {"main": [[{"node": "Supabase NPS Kaydet", "type": "main", "index": 0}]]}
    c["Supabase NPS Kaydet"] = {"main": [[{"node": "NPS Yanıt Dön", "type": "main", "index": 0}]]}


def patch_google_review(wf):
    node = supabase_node(
        "Supabase Yorum Kaydet",
        "google_reviews",
        [
            ("clinic_id", CLINIC_ID),
            ("author_name", "={{ $('Yorumu Normalize Et').item.json.authorName }}"),
            ("rating", "={{ $('Yorumu Normalize Et').item.json.rating }}"),
            ("review_text", "={{ $('Yorumu Normalize Et').item.json.reviewText }}"),
            ("sentiment", "={{ $json.output.sentiment }}"),
            ("themes", "={{ JSON.stringify($json.output.themes) }}"),
            ("draft_reply", "={{ $json.output.draftReply }}"),
            ("urgency", "={{ $json.output.urgency }}"),
            ("status", "pending_approval"),
        ],
        [1120, 380],
    )
    wf["nodes"].append(node)
    wf["connections"]["Onay Kuyruğu Log"] = {
        "main": [[{"node": "Supabase Yorum Kaydet", "type": "main", "index": 0}]]
    }


def patch_enps(wf):
    node = supabase_node(
        "Supabase eNPS Kaydet",
        "enps_responses",
        [
            ("clinic_id", CLINIC_ID),
            ("department", "={{ $('eNPS Parse').item.json.department }}"),
            ("score", "={{ $('eNPS Parse').item.json.score }}"),
            ("feedback", "={{ $('eNPS Parse').item.json.feedback }}"),
            ("flow", "={{ $json.flow }}"),
        ],
        [1320, 520],
    )
    wf["nodes"].append(node)
    c = wf["connections"]
    c["Glassdoor Teşviki"] = {"main": [[{"node": "Supabase eNPS Kaydet", "type": "main", "index": 0}]]}
    c["Yönetim Raporu"] = {"main": [[{"node": "Supabase eNPS Kaydet", "type": "main", "index": 0}]]}
    c["Supabase eNPS Kaydet"] = {"main": [[{"node": "Yanıt Dön", "type": "main", "index": 0}]]}


def patch_sentinel(wf):
    node = supabase_node(
        "Supabase Mention Kaydet",
        "reputation_mentions",
        [
            ("clinic_id", CLINIC_ID),
            ("source", "={{ $('Mention Normalize').item.json.source }}"),
            ("url", "={{ $('Mention Normalize').item.json.url }}"),
            ("content", "={{ $('Mention Normalize').item.json.content }}"),
            ("sentiment", "={{ $json.output.sentiment }}"),
            ("risk_score", "={{ $json.output.riskScore }}"),
            ("recommended_action", "={{ $json.output.recommendedAction }}"),
            ("is_critical", "={{ $json.output.recommendedAction === 'alert_urgent' }}"),
        ],
        [1320, 380],
    )
    wf["nodes"].append(node)
    c = wf["connections"]
    c["Kritik Alarm Log"] = {"main": [[{"node": "Supabase Mention Kaydet", "type": "main", "index": 0}]]}
    c["Haftalık Rapora Ekle"] = {"main": [[{"node": "Supabase Mention Kaydet", "type": "main", "index": 0}]]}


def patch_recall(wf):
    node = supabase_node(
        "Supabase Recall Kaydet",
        "recall_campaigns",
        [
            ("clinic_id", CLINIC_ID),
            ("last_treatment", "={{ $('Hasta Normalize').item.json.lastTreatment }}"),
            ("months_since_visit", "={{ $('Hasta Normalize').item.json.monthsSinceVisit }}"),
            ("message_sent", "={{ $json.output }}"),
            ("booking_url", "={{ $('Hasta Normalize').item.json.bookingUrl }}"),
            ("status", "sent"),
        ],
        [1320, 300],
    )
    wf["nodes"].append(node)
    wf["connections"]["WhatsApp Hatırlatma"] = {
        "main": [[{"node": "Supabase Recall Kaydet", "type": "main", "index": 0}]]
    }


def patch_inbox(wf):
    node = supabase_node(
        "Supabase Inbox Kaydet",
        "inbox_messages",
        [
            ("clinic_id", CLINIC_ID),
            ("channel", "={{ $('Mesaj Normalize').item.json.channel }}"),
            ("direction", "inbound"),
            ("body", "={{ $('Mesaj Normalize').item.json.message }}"),
            ("ai_draft_reply", "={{ $json.output }}"),
            ("status", "draft_ready"),
        ],
        [1120, 300],
    )
    wf["nodes"].append(node)
    wf["connections"]["Inbox Log"] = {
        "main": [[{"node": "Supabase Inbox Kaydet", "type": "main", "index": 0}]]
    }


PATCHERS = {
    "nefalix-01-feedback-reviews-loop.json": patch_feedback,
    "nefalix-02-google-review-ai-agent.json": patch_google_review,
    "nefalix-03-inside-enps.json": patch_enps,
    "nefalix-04-sentinel-reputation.json": patch_sentinel,
    "nefalix-05-recall-patient.json": patch_recall,
    "nefalix-06-inbox-routing.json": patch_inbox,
}


def main():
    for fname, patcher in PATCHERS.items():
        path = WORKFLOWS / fname
        wf = json.loads(path.read_text())
        wf["nodes"] = [n for n in wf["nodes"] if not n.get("name", "").startswith("Supabase ")]
        patcher(wf)
        path.write_text(json.dumps(wf, indent=2, ensure_ascii=False) + "\n")
        print(f"patched {fname}")


if __name__ == "__main__":
    main()
