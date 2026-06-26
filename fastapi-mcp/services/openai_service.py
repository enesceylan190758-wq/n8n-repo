import os
import json
from openai import AsyncOpenAI

_client: AsyncOpenAI | None = None


def get_openai() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])
    return _client


BOARD_SUMMARY_PROMPT = """
Sen Nefalix AI'ın yönetici özet motorusun. Sağlık kliniklerine özel bir İş Zekası uzmanısın.

Aşağıdaki verileri analiz et ve JSON formatında yönetici raporu üret:
- Hasta NPS verileri
- Çalışan eNPS verileri  
- Google yorum istatistikleri

Dönem: {period}
Klinik: {clinic_name}

Veri:
{data_json}

JSON formatında şu alanları doldur:
{{
  "executive_headline": "tek cümle özet",
  "key_findings": ["bulgu 1", "bulgu 2", "bulgu 3"],
  "correlation_insight": "iç-dış korelasyon yorumu",
  "risk_level": "low|normal|elevated|critical",
  "immediate_actions": ["aksiyon 1", "aksiyon 2"],
  "30_day_forecast": "kısa tahmin"
}}
"""


async def generate_board_summary(
    clinic_name: str,
    period: str,
    enps_data: list[dict],
    review_data: list[dict],
    nps_data: dict,
) -> dict:
    data = {
        "nps": nps_data,
        "enps_responses": enps_data[:20],
        "recent_reviews": review_data[:10],
    }
    prompt = BOARD_SUMMARY_PROMPT.format(
        period=period,
        clinic_name=clinic_name,
        data_json=json.dumps(data, ensure_ascii=False, indent=2),
    )

    client = get_openai()
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        max_tokens=1000,
    )
    return json.loads(response.choices[0].message.content)


async def calculate_correlation(
    enps_scores: list[int],
    star_ratings: list[float],
) -> float | None:
    if len(enps_scores) < 3 or len(star_ratings) < 3:
        return None

    n = min(len(enps_scores), len(star_ratings))
    x = enps_scores[:n]
    y = star_ratings[:n]

    mean_x = sum(x) / n
    mean_y = sum(y) / n

    numerator = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
    denom_x = sum((xi - mean_x) ** 2 for xi in x) ** 0.5
    denom_y = sum((yi - mean_y) ** 2 for yi in y) ** 0.5

    if denom_x == 0 or denom_y == 0:
        return 0.0

    return round(numerator / (denom_x * denom_y), 4)
