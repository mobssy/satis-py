from bs4 import BeautifulSoup
import logging
from http_client import safe_request

logger = logging.getLogger(__name__)

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


def _get_company_tag(title: str) -> str:
    title_lower = title.lower()
    for keyword, tag in _COMPANY_TAGS.items():
        if keyword in title_lower:
            return tag
    return "[BigTech]"


def get_bigtech_news() -> list[dict]:
    """구글 뉴스에서 빅테크 회사 관련 뉴스 5개 크롤링"""
    news_list = []
    try:
        url = f'https://news.google.com/rss/search?q={_BIGTECH_KEYWORDS}&hl=en-US&gl=US&ceid=US:en'
        response = safe_request(url)
        if not response:
            return news_list

        soup = BeautifulSoup(response.content, 'xml')
        for item in soup.find_all('item')[:5]:
            try:
                if not item.title or not item.link or not item.description:
                    continue

                title = item.title.text.strip()
                link = item.link.text.strip()
                summary = item.description.text.strip()

                if not title or not link or not summary:
                    continue

                news_list.append({
                    'title': f"{_get_company_tag(title)} {title}",
                    'url': link,
                    'content': summary,
                })

            except Exception as e:
                logger.error(f"빅테크 뉴스 항목 처리 중 오류: {e}")

    except Exception as e:
        logger.error(f"빅테크 뉴스 크롤링 중 오류: {e}")

    logger.info(f"빅테크: {len(news_list)} articles found")
    return news_list
