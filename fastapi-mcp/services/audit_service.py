import asyncio
import json
import httpx
from bs4 import BeautifulSoup
from models.schemas import AuditResult, AuditCheckResult


SCORE_WEIGHTS = {
    "discoverability": 0.35,
    "answer_readiness": 0.35,
    "trust_signals": 0.30,
}

GRADE_THRESHOLDS = [
    (80, "A"),
    (60, "B"),
    (40, "C"),
    (0,  "D"),
]


def score_to_grade(score: int) -> str:
    for threshold, grade in GRADE_THRESHOLDS:
        if score >= threshold:
            return grade
    return "D"


async def _fetch(url: str, timeout: float = 10.0) -> httpx.Response | None:
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=timeout) as client:
            return await client.get(url)
    except Exception:
        return None


async def check_llms_txt(base_url: str) -> AuditCheckResult:
    url = base_url.rstrip("/") + "/llms.txt"
    resp = await _fetch(url)
    passed = resp is not None and resp.status_code == 200
    return AuditCheckResult(
        name="llms_txt",
        passed=passed,
        score=25 if passed else 0,
        detail=f"GET {url} → {resp.status_code if resp else 'timeout'}",
    )


async def check_robots_txt(base_url: str) -> AuditCheckResult:
    url = base_url.rstrip("/") + "/robots.txt"
    resp = await _fetch(url)
    if resp is None or resp.status_code != 200:
        return AuditCheckResult(name="robots_txt", passed=False, score=0, detail="robots.txt erişilemiyor")
    body = resp.text.lower()
    blocks_ai = any(
        agent in body and "disallow: /" in body
        for agent in ["gptbot", "claudebot", "googlebot", "anthropic-ai"]
    )
    passed = not blocks_ai
    return AuditCheckResult(
        name="robots_allows_ai",
        passed=passed,
        score=15 if passed else 0,
        detail="AI bot'lar engellendi" if blocks_ai else "AI bot erişimi açık",
    )


async def check_schema_org(base_url: str) -> AuditCheckResult:
    resp = await _fetch(base_url)
    if resp is None or resp.status_code != 200:
        return AuditCheckResult(name="schema_markup", passed=False, score=0, detail="Sayfa erişilemiyor")

    soup = BeautifulSoup(resp.text, "html.parser")
    scripts = soup.find_all("script", type="application/ld+json")
    valid_schema = False
    for script in scripts:
        try:
            data = json.loads(script.string or "")
            schema_type = data.get("@type", "")
            if any(t in schema_type for t in ["LocalBusiness", "Dentist", "MedicalClinic", "Hospital"]):
                valid_schema = True
                break
        except (json.JSONDecodeError, AttributeError):
            continue

    return AuditCheckResult(
        name="schema_markup",
        passed=valid_schema,
        score=20 if valid_schema else 0,
        detail="LocalBusiness JSON-LD bulundu" if valid_schema else "Geçerli LocalBusiness schema yok",
    )


async def check_faq_schema(base_url: str) -> AuditCheckResult:
    resp = await _fetch(base_url)
    if resp is None:
        return AuditCheckResult(name="faq_schema", passed=False, score=0)

    soup = BeautifulSoup(resp.text, "html.parser")
    scripts = soup.find_all("script", type="application/ld+json")
    has_faq = any(
        "FAQPage" in (script.string or "")
        for script in scripts
    )
    return AuditCheckResult(
        name="faq_schema",
        passed=has_faq,
        score=15 if has_faq else 0,
        detail="FAQPage schema bulundu" if has_faq else "FAQPage schema eksik",
    )


async def check_quotable_content(base_url: str) -> AuditCheckResult:
    resp = await _fetch(base_url)
    if resp is None:
        return AuditCheckResult(name="quotable_content", passed=False, score=0)

    soup = BeautifulSoup(resp.text, "html.parser")
    text = soup.get_text()
    word_count = len(text.split())
    # LLM için alıntılanabilir yeterli metin var mı?
    passed = word_count > 500
    return AuditCheckResult(
        name="quotable_content",
        passed=passed,
        score=min(25, word_count // 40),
        detail=f"{word_count} kelime bulundu",
    )


def _build_recommendations(checks: list[AuditCheckResult]) -> list[str]:
    recs = []
    check_map = {c.name: c for c in checks}

    if not check_map.get("llms_txt", AuditCheckResult(name="", passed=True, score=0)).passed:
        recs.append("🔴 [Kritik] /llms.txt dosyası oluşturun — AI motorları bu dosyayı okur")
    if not check_map.get("schema_markup", AuditCheckResult(name="", passed=True, score=0)).passed:
        recs.append("🔴 [Kritik] LocalBusiness JSON-LD schema ekleyin")
    if not check_map.get("robots_allows_ai", AuditCheckResult(name="", passed=True, score=0)).passed:
        recs.append("🟠 [Yüksek] robots.txt'te AI bot'ları engelleyen kuralları kaldırın")
    if not check_map.get("faq_schema", AuditCheckResult(name="", passed=True, score=0)).passed:
        recs.append("🟡 [Orta] FAQPage schema ile sık sorulan soruları işaretleyin")
    if not check_map.get("quotable_content", AuditCheckResult(name="", passed=True, score=0)).passed:
        recs.append("🟡 [Orta] AI motorlarının alıntılayabileceği özgün içerik artırın (min. 500 kelime)")

    return recs


async def run_technical_audit(website_url: str) -> AuditResult:
    checks = await asyncio.gather(
        check_llms_txt(website_url),
        check_robots_txt(website_url),
        check_schema_org(website_url),
        check_faq_schema(website_url),
        check_quotable_content(website_url),
    )

    llms_check, robots_check, schema_check, faq_check, content_check = checks

    discoverability = (llms_check.score + robots_check.score) * 2
    answer_readiness = (faq_check.score + content_check.score) * 2
    trust_signals = schema_check.score * 2

    discoverability = min(100, discoverability)
    answer_readiness = min(100, answer_readiness)
    trust_signals = min(100, trust_signals)

    overall = int(
        discoverability * SCORE_WEIGHTS["discoverability"]
        + answer_readiness * SCORE_WEIGHTS["answer_readiness"]
        + trust_signals * SCORE_WEIGHTS["trust_signals"]
    )

    return AuditResult(
        website_url=website_url,
        overall_score=overall,
        discoverability_score=discoverability,
        answer_readiness_score=answer_readiness,
        trust_signals_score=trust_signals,
        grade=score_to_grade(overall),
        llm_txt_present=llms_check.passed,
        schema_markup_valid=schema_check.passed,
        nap_consistent=False,
        robots_allows_ai=robots_check.passed,
        page_speed_score=None,
        faq_schema_present=faq_check.passed,
        checks=list(checks),
        recommendations=_build_recommendations(list(checks)),
    )
