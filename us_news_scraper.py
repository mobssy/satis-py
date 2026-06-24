from bs4 import BeautifulSoup
import logging
from http_client import safe_request

logger = logging.getLogger(__name__)


def _fetch_google_rss_news(query: str, label: str) -> list[dict]:
    """구글 뉴스 RSS에서 특정 쿼리의 핫뉴스 5개 크롤링"""
    news_list = []
    try:
        url = f'https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en'
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
                    'title': f"[{label}] {title}",
                    'url': link,
                    'content': summary,
                })

            except Exception as e:
                logger.error(f"{label} 뉴스 항목 처리 중 오류: {e}")

    except Exception as e:
        logger.error(f"{label} 뉴스 크롤링 중 오류: {e}")

    logger.info(f"{label}: {len(news_list)} articles found")
    return news_list


def get_nj_hot_news() -> list[dict]:
    return _fetch_google_rss_news("new+jersey", "뉴저지")


def get_ny_hot_news() -> list[dict]:
    return _fetch_google_rss_news("new+york", "뉴욕")
