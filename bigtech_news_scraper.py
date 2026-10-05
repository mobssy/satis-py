import re
from google_rss_scraper import fetch_google_rss_news

_BIGTECH_KEYWORDS = "Apple OR Google OR Microsoft OR Amazon OR Meta OR Tesla OR NVIDIA OR OpenAI"

_COMPANY_TAGS: dict[str, str] = {
    "apple": "[Apple]",
    "google": "[Google]",
    "alphabet": "[Google]",
    "microsoft": "[Microsoft]",
    "amazon": "[Amazon]",
    "meta": "[Meta]",
    "facebook": "[Meta]",
    "tesla": "[Tesla]",
    "nvidia": "[NVIDIA]",
    "openai": "[OpenAI]",
}


# 부분 문자열이 아니라 단어 단위로 매칭 ("meta"가 "metal"에 걸리지 않도록)
_COMPANY_PATTERNS = [
    (re.compile(rf"\b{re.escape(keyword)}\b", re.IGNORECASE), tag)
    for keyword, tag in _COMPANY_TAGS.items()
]
# 회사가 아닌 뜻으로 자주 쓰이는 표현 (예: 아마존 열대우림)
_NON_COMPANY_PATTERN = re.compile(r"\b(the amazon|amazon rainforest|amazon river)\b", re.IGNORECASE)


def _format_bigtech_title(title: str) -> str:
    text = _NON_COMPANY_PATTERN.sub("", title)
    for pattern, tag in _COMPANY_PATTERNS:
        if pattern.search(text):
            return f"{tag} {title}"
    return f"[BigTech] {title}"


def get_bigtech_news() -> list[dict]:
    """구글 뉴스에서 빅테크 회사 관련 뉴스 5개 수집"""
    return fetch_google_rss_news(_BIGTECH_KEYWORDS, "빅테크", title_formatter=_format_bigtech_title)
