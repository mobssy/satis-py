import logging
from dataclasses import dataclass
from typing import Callable
from bs4 import BeautifulSoup
from http_client import fetch_with_retry
from article import Article

logger = logging.getLogger(__name__)

_RSS_BASE_URL = "https://news.google.com/rss"


@dataclass(frozen=True)
class RssLocale:
    """구글 뉴스 RSS의 언어/지역 설정"""
    hl: str
    gl: str
    ceid: str

    def query_string(self) -> str:
        return f"hl={self.hl}&gl={self.gl}&ceid={self.ceid}"


US_ENGLISH = RssLocale(hl="en-US", gl="US", ceid="US:en")
KOREA_KOREAN = RssLocale(hl="ko", gl="KR", ceid="KR:ko")


def _build_url(query: str | None, locale: RssLocale) -> str:
    """query가 있으면 검색 결과, 없으면 해당 지역의 주요 뉴스(top stories) 피드"""
    if query:
        return f"{_RSS_BASE_URL}/search?q={query}&{locale.query_string()}"
    return f"{_RSS_BASE_URL}?{locale.query_string()}"


def fetch_google_rss_news(
    query: str | None,
    label: str,
    title_formatter: Callable[[str], str] | None = None,
    max_items: int = 15,
    locale: RssLocale = US_ENGLISH,
) -> list[Article]:
    """구글 뉴스 RSS에서 뉴스 수집 (query가 None이면 주요 뉴스 피드)

    title_formatter를 지정하면 제목 포맷을 커스터마이징할 수 있고,
    지정하지 않으면 "[label] 제목" 형식을 사용한다.
    이미 보낸 기사를 걸러낸 뒤에도 채울 수 있도록 넉넉하게 후보를 반환한다.
    """
    if title_formatter is None:
        title_formatter = lambda title: f"[{label}] {title}"

    news_list = []
    try:
        url = _build_url(query, locale)
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
                # description은 이스케이프된 HTML 조각이라 태그를 벗겨 텍스트만 사용
                summary = BeautifulSoup(item.description.text, 'html.parser').get_text(' ', strip=True)

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
