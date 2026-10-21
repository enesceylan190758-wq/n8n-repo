import os
from fastapi import APIRouter
from models.schemas import HealthResponse
from services.supabase_client import get_supabase

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    supabase_status = "ok"
    try:
        sb = get_supabase()
        sb.table("clinics").select("id").limit(1).execute()
    except Exception as e:
        supabase_status = f"error: {str(e)[:80]}"

    return HealthResponse(
        status="ok",
        version="0.1.0",
        supabase=supabase_status,
    )
