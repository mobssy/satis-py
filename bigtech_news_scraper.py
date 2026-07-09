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


def _format_bigtech_title(title: str) -> str:
    title_lower = title.lower()
    for keyword, tag in _COMPANY_TAGS.items():
        if keyword in title_lower:
            return f"{tag} {title}"
    return f"[BigTech] {title}"


def get_bigtech_news() -> list[dict]:
    """구글 뉴스에서 빅테크 회사 관련 뉴스 5개 수집"""
    return fetch_google_rss_news(_BIGTECH_KEYWORDS, "빅테크", title_formatter=_format_bigtech_title)
