from fastapi import APIRouter, BackgroundTasks
from models.schemas import N8nWebhookPayload
from services.supabase_client import get_supabase
from services.audit_service import run_technical_audit
from services.supabase_client import save_ai_score
from datetime import datetime

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/n8n")
async def receive_n8n_event(payload: N8nWebhookPayload, background: BackgroundTasks):
    """
    n8n workflow'larından gelen event'leri alır ve işler.
    Örnek: audit tetikleme, alarm işleme, özet talepleri.
    """
    event_type = payload.event_type

    if payload.clinic_id:
        sb = get_supabase()
        sb.table("automation_events").insert({
            "clinic_id": payload.clinic_id,
            "workflow_name": "n8n-webhook",
            "event_type": event_type,
            "payload": payload.payload,
            "status": "received",
        }).execute()

    if event_type == "trigger_audit" and payload.location_id:
        website_url = payload.payload.get("website_url")
        if website_url:
            background.add_task(_run_audit_background, payload.location_id, website_url)
            return {"status": "audit_queued", "location_id": payload.location_id}

    if event_type == "grade_alert":
        grade = payload.payload.get("grade")
        return {
            "status": "alert_processed",
            "grade": grade,
            "priority": "CRITICAL" if grade == "D" else "TOP_PRIORITY",
        }

    return {"status": "received", "event_type": event_type}


async def _run_audit_background(location_id: str, website_url: str):
    result = await run_technical_audit(website_url)
    await save_ai_score(location_id, {
        "location_id": location_id,
        "overall_score": result.overall_score,
        "discoverability_score": result.discoverability_score,
        "answer_readiness_score": result.answer_readiness_score,
        "trust_signals_score": result.trust_signals_score,
        "grade": result.grade,
        "llm_txt_present": result.llm_txt_present,
        "schema_markup_valid": result.schema_markup_valid,
        "nap_consistent": result.nap_consistent,
        "robots_allows_ai": result.robots_allows_ai,
        "faq_schema_present": result.faq_schema_present,
        "recommendations": result.recommendations,
        "audit_date": datetime.utcnow().isoformat(),
    })
