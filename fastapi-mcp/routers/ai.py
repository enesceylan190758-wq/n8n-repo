from fastapi import APIRouter, HTTPException, UploadFile, File
from models.schemas import AuditRequest, AuditResult, ScoreRequest, SummaryRequest, CorrelateRequest
from services.audit_service import run_technical_audit
from services.supabase_client import (
    get_supabase,
    get_clinic,
    get_nps_summary,
    save_ai_score,
    save_executive_summary,
)
from services.openai_service import generate_board_summary, calculate_correlation
import csv
import io

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/audit", response_model=AuditResult)
async def audit_website(req: AuditRequest):
    """
    Web sitesi GEO/AEO teknik denetimi.
    llms.txt · Schema.org · robots.txt · FAQ schema · içerik kalitesi kontrol edilir.
    """
    result = await run_technical_audit(req.website_url)

    if req.save_to_db and req.location_id:
        await save_ai_score(
            req.location_id,
            {
                "location_id": req.location_id,
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
                "audit_details": {c.name: c.model_dump() for c in result.checks},
                "recommendations": result.recommendations,
            },
        )

    return result


@router.post("/score")
async def compute_score(req: ScoreRequest):
    """
    Lokasyon için AI Readiness skoru hesaplar ve DB'ye yazar.
    """
    audit = await run_technical_audit(req.website_url)
    saved = await save_ai_score(
        req.location_id,
        {
            "location_id": req.location_id,
            "overall_score": audit.overall_score,
            "discoverability_score": audit.discoverability_score,
            "answer_readiness_score": audit.answer_readiness_score,
            "trust_signals_score": audit.trust_signals_score,
            "grade": audit.grade,
            "llm_txt_present": audit.llm_txt_present,
            "schema_markup_valid": audit.schema_markup_valid,
            "nap_consistent": audit.nap_consistent,
            "robots_allows_ai": audit.robots_allows_ai,
            "faq_schema_present": audit.faq_schema_present,
            "recommendations": audit.recommendations,
        },
    )
    return {"status": "saved", "grade": audit.grade, "overall_score": audit.overall_score, "record": saved}


@router.post("/summary")
async def generate_summary(req: SummaryRequest):
    """
    Board-ready yönetici özeti üretir (Claude/GPT-4o ile).
    eNPS + hasta NPS + Google yorum verileri çapraz analiz edilir.
    """
    clinic = await get_clinic(req.clinic_id)
    if not clinic:
        raise HTTPException(status_code=404, detail="Klinik bulunamadı")

    nps_summary = await get_nps_summary(req.clinic_id, days=90)

    summary_dict = await generate_board_summary(
        clinic_name=clinic.get("name", ""),
        period=req.period,
        enps_data=req.enps_data,
        review_data=req.review_data,
        nps_data=nps_summary,
    )

    location_id = req.location_id
    if location_id:
        await save_executive_summary(
            location_id=location_id,
            period=req.period,
            summary=str(summary_dict),
        )

    return {"status": "generated", "period": req.period, "summary": summary_dict}


@router.post("/correlate")
async def correlate_sentiment(req: CorrelateRequest):
    """
    Çalışan eNPS ↔ hasta yıldız derecelendirmesi korelasyonu hesaplar.
    """
    sb = get_supabase()

    enps_r = (
        sb.table("enps_responses")
        .select("score")
        .execute()
    )
    reviews_r = (
        sb.table("google_reviews")
        .select("rating")
        .execute()
    )

    enps_scores = [r["score"] for r in (enps_r.data or [])]
    star_ratings = [r["rating"] for r in (reviews_r.data or [])]

    correlation = await calculate_correlation(enps_scores, star_ratings)

    if correlation is not None:
        await save_executive_summary(
            location_id=req.location_id,
            period=req.period,
            summary="",
            correlation=correlation,
        )

    return {
        "location_id": req.location_id,
        "period": req.period,
        "correlation_score": correlation,
        "enps_count": len(enps_scores),
        "review_count": len(star_ratings),
        "interpretation": _interpret_correlation(correlation),
    }


@router.get("/executive/{clinic_id}")
async def get_executive_summary(clinic_id: str, period: str | None = None):
    """
    Kaydedilmiş yönetici özetini getirir.
    """
    sb = get_supabase()
    query = (
        sb.table("operational_sentiment")
        .select("*, locations(business_name, branch_name)")
        .eq("locations.clinic_id", clinic_id)
        .order("period", desc=True)
        .limit(4)
    )
    if period:
        query = query.eq("period", period)

    r = query.execute()
    return {"summaries": r.data or []}


@router.post("/upload/enps")
async def upload_enps_csv(file: UploadFile = File(...), clinic_id: str = ""):
    """
    eNPS CSV yükle → parse et → DB'ye kaydet.
    Beklenen sütunlar: department, score, feedback
    """
    content = await file.read()
    reader = csv.DictReader(io.StringIO(content.decode("utf-8-sig")))

    rows = []
    for row in reader:
        try:
            score = int(row.get("score", 0))
            rows.append({
                "clinic_id": clinic_id or row.get("clinic_id"),
                "department": row.get("department"),
                "score": score,
                "feedback": row.get("feedback"),
                "flow": "promoter" if score >= 8 else "detractor" if score <= 6 else None,
            })
        except (ValueError, KeyError):
            continue

    if rows:
        sb = get_supabase()
        sb.table("enps_responses").insert(rows).execute()

    return {"status": "imported", "count": len(rows)}


def _interpret_correlation(r: float | None) -> str:
    if r is None:
        return "Yetersiz veri — korelasyon hesaplanamadı"
    if r >= 0.7:
        return "Güçlü pozitif ilişki: Çalışan mutluluğu hasta memnuniyetini doğrudan etkiliyor"
    if r >= 0.4:
        return "Orta pozitif ilişki: Personel iyileştirmeleri hasta skoruna yansıyacaktır"
    if r >= 0.0:
        return "Zayıf pozitif ilişki: Diğer faktörler de incelenmeli"
    return "Negatif ilişki: Beklenmedik bir örüntü — veri kalitesi kontrol edilmeli"
