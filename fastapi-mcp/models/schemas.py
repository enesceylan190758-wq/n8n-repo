from pydantic import BaseModel, Field
from typing import Any
from datetime import datetime


class AuditRequest(BaseModel):
    website_url: str
    location_id: str | None = None
    save_to_db: bool = True


class AuditCheckResult(BaseModel):
    name: str
    passed: bool
    score: int = Field(ge=0, le=100)
    detail: str | None = None


class AuditResult(BaseModel):
    website_url: str
    overall_score: int = Field(ge=0, le=100)
    discoverability_score: int
    answer_readiness_score: int
    trust_signals_score: int
    grade: str
    llm_txt_present: bool
    schema_markup_valid: bool
    nap_consistent: bool
    robots_allows_ai: bool
    page_speed_score: int | None
    faq_schema_present: bool
    checks: list[AuditCheckResult]
    recommendations: list[str]
    audit_date: datetime = Field(default_factory=datetime.utcnow)


class ScoreRequest(BaseModel):
    location_id: str
    website_url: str


class SummaryRequest(BaseModel):
    clinic_id: str
    period: str
    location_id: str | None = None
    enps_data: list[dict[str, Any]] = []
    review_data: list[dict[str, Any]] = []


class CorrelateRequest(BaseModel):
    location_id: str
    period: str


class MCPContextResponse(BaseModel):
    clinic: dict[str, Any]
    recent_reviews: list[dict[str, Any]]
    nps_summary: dict[str, Any]
    ai_readiness: dict[str, Any] | None
    open_complaints: list[dict[str, Any]]
    executive_alerts: list[dict[str, Any]]
    metadata: dict[str, Any]


class N8nWebhookPayload(BaseModel):
    event_type: str
    clinic_id: str | None = None
    location_id: str | None = None
    payload: dict[str, Any] = {}


class HealthResponse(BaseModel):
    status: str
    version: str
    supabase: str
