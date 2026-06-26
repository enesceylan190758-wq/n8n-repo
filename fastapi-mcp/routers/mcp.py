from datetime import datetime
from fastapi import APIRouter, HTTPException
from models.schemas import MCPContextResponse
from services.supabase_client import (
    get_clinic,
    get_recent_reviews,
    get_nps_summary,
    get_latest_ai_score,
    get_open_inbox,
    get_alerts,
)

router = APIRouter(prefix="/mcp", tags=["mcp"])


@router.get("/context/{clinic_id}", response_model=MCPContextResponse)
async def get_mcp_context(clinic_id: str):
    """
    LLM ve voice/chat agent'larına beslenecek yapılandırılmış klinik bağlamı.
    Web chatbot, WhatsApp bot ve Cursor MCP bağlantısı bu endpoint'i kullanır.
    """
    clinic = await get_clinic(clinic_id)
    if not clinic:
        raise HTTPException(status_code=404, detail="Klinik bulunamadı")

    recent_reviews, nps_summary, ai_readiness, open_complaints, alerts = await _gather_context(clinic_id)

    return MCPContextResponse(
        clinic=clinic,
        recent_reviews=recent_reviews,
        nps_summary=nps_summary,
        ai_readiness=ai_readiness,
        open_complaints=open_complaints,
        executive_alerts=alerts,
        metadata={
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "context_version": "1.0",
            "clinic_id": clinic_id,
        },
    )


async def _gather_context(clinic_id: str):
    import asyncio
    return await asyncio.gather(
        get_recent_reviews(clinic_id, limit=5),
        get_nps_summary(clinic_id, days=30),
        get_latest_ai_score(clinic_id),
        get_open_inbox(clinic_id, limit=10),
        get_alerts(clinic_id),
    )
