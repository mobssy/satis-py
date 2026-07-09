import logging
from typing import Callable
from bs4 import BeautifulSoup
from http_client import fetch_with_retry

logger = logging.getLogger(__name__)

_RSS_URL_TEMPLATE = "https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"


def fetch_google_rss_news(
    query: str,
    label: str,
    title_formatter: Callable[[str], str] | None = None,
    max_items: int = 5,
) -> list[dict]:
    """구글 뉴스 RSS에서 특정 쿼리의 뉴스 수집

    title_formatter를 지정하면 제목 포맷을 커스터마이징할 수 있고,
    지정하지 않으면 "[label] 제목" 형식을 사용한다.
    """
    if title_formatter is None:
        title_formatter = lambda title: f"[{label}] {title}"

    news_list = []
    try:
        url = _RSS_URL_TEMPLATE.format(query=query)
        response = fetch_with_retry(url, delay=0)
        if not response:
            return news_list

        soup = BeautifulSoup(response.content, 'xml')
        for item in soup.find_all('item')[:max_items]:
            try:
                if not item.title or not item.link or not item.description:
                    continue

                title = item.title.text.strip()
                link = item.link.text.strip()
                summary = item.description.text.strip()

                if not (title and link and summary):
                    continue

                news_list.append({
                    'title': title_formatter(title),
                    'url': link,
                    'content': summary,
                })

            except Exception as e:
                logger.error(f"{label} 뉴스 항목 처리 중 오류: {e}")

    except Exception as e:
        logger.error(f"{label} 뉴스 크롤링 중 오류: {e}")

    logger.info(f"{label}: {len(news_list)} articles found")
    return news_list
