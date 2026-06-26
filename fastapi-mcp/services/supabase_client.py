import os
from supabase import create_client, Client
from datetime import datetime, timedelta

_client: Client | None = None


def get_supabase() -> Client:
    global _client
    if _client is None:
        url = os.environ["SUPABASE_URL"]
        key = os.environ["SUPABASE_SERVICE_KEY"]
        _client = create_client(url, key)
    return _client


async def get_clinic(clinic_id: str) -> dict:
    sb = get_supabase()
    r = sb.table("clinics").select("*").eq("id", clinic_id).single().execute()
    return r.data or {}


async def get_recent_reviews(clinic_id: str, limit: int = 5) -> list[dict]:
    sb = get_supabase()
    r = (
        sb.table("google_reviews")
        .select("author_name, rating, review_text, sentiment, status, created_at")
        .eq("clinic_id", clinic_id)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return r.data or []


async def get_nps_summary(clinic_id: str, days: int = 30) -> dict:
    sb = get_supabase()
    since = (datetime.utcnow() - timedelta(days=days)).isoformat()
    r = (
        sb.table("nps_responses")
        .select("score, flow")
        .eq("clinic_id", clinic_id)
        .gte("created_at", since)
        .execute()
    )
    rows = r.data or []
    if not rows:
        return {"avg_score": None, "count": 0, "promoter_pct": 0, "detractor_pct": 0}
    scores = [row["score"] for row in rows]
    promoters = sum(1 for s in scores if s >= 8)
    detractors = sum(1 for s in scores if s <= 6)
    return {
        "avg_score": round(sum(scores) / len(scores), 2),
        "count": len(scores),
        "promoter_pct": round(promoters / len(scores) * 100),
        "detractor_pct": round(detractors / len(scores) * 100),
    }


async def get_latest_ai_score(clinic_id: str) -> dict | None:
    sb = get_supabase()
    r = (
        sb.table("v_latest_ai_scores")
        .select("*")
        .eq("clinic_id", clinic_id)
        .limit(1)
        .execute()
    )
    return (r.data or [None])[0]


async def get_open_inbox(clinic_id: str, limit: int = 10) -> list[dict]:
    sb = get_supabase()
    r = (
        sb.table("inbox_messages")
        .select("id, channel, body, status, created_at")
        .eq("clinic_id", clinic_id)
        .in_("status", ["open", "draft_ready"])
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return r.data or []


async def get_alerts(clinic_id: str) -> list[dict]:
    sb = get_supabase()
    r = (
        sb.table("reputation_mentions")
        .select("source, sentiment, risk_score, recommended_action, is_critical, created_at")
        .eq("clinic_id", clinic_id)
        .eq("is_critical", True)
        .order("created_at", desc=True)
        .limit(5)
        .execute()
    )
    return r.data or []


async def save_ai_score(location_id: str, result: dict) -> dict:
    sb = get_supabase()
    r = sb.table("ai_readiness_scores").insert(result).execute()
    return (r.data or [{}])[0]


async def save_executive_summary(location_id: str, period: str, summary: str, correlation: float | None = None) -> dict:
    sb = get_supabase()
    r = (
        sb.table("operational_sentiment")
        .upsert(
            {
                "location_id": location_id,
                "period": period,
                "executive_summary": summary,
                "correlation_score": correlation,
                "updated_at": datetime.utcnow().isoformat(),
            },
            on_conflict="location_id,period",
        )
        .execute()
    )
    return (r.data or [{}])[0]
