import logging
from bs4 import BeautifulSoup
from http_client import safe_request

logger = logging.getLogger(__name__)

_LIST_SELECTORS = ['article', '.post', '.article', '.entry']
_TITLE_SELECTORS = ['h2', 'h3', '.title', '.entry-title']
_CONTENT_SELECTORS = ['article', '.post-content', '.entry-content', '.article-content']
_NOISE_SELECTORS = '.advertisement, .related-posts, .comments, .social-share'

def _fetch_apple_site_news(url: str, source: str, base_url: str) -> list[dict]:
    """애플 뉴스 사이트 공통 스크래핑 로직"""
    articles = []
    try:
        response = safe_request(url)
        if not response:
            return articles

        soup = BeautifulSoup(response.text, 'html.parser')
        news_items = []
        for selector in _LIST_SELECTORS:
            items = soup.select(selector)
            if items:
                news_items = items[:5]
                break

        for item in news_items:
            try:
                title_elem = next(
                    (item.select_one(s) for s in _TITLE_SELECTORS if item.select_one(s)),
                    None
                )
                if not title_elem:
                    continue

                title = title_elem.text.strip()
                link_elem = item.select_one('a')
                if not link_elem or 'href' not in link_elem.attrs:
                    continue

                link = link_elem['href']
                if not link.startswith('http'):
                    link = base_url + link

                article_response = safe_request(link)
                if not article_response:
                    continue

                article_soup = BeautifulSoup(article_response.text, 'html.parser')
                content = None
                for content_selector in _CONTENT_SELECTORS:
                    content_elem = article_soup.select_one(content_selector)
                    if content_elem:
                        for tag in content_elem.select(_NOISE_SELECTORS):
                            tag.decompose()
                        content = content_elem.text.strip()
                        break

                articles.append({
                    'title': title,
                    'content': content or f"제목: {title}\n\n내용을 가져올 수 없습니다.",
                    'url': link,
                    'source': source,
                })

            except Exception as e:
                logger.error(f"{source} 기사 처리 중 오류: {e}")

    except Exception as e:
        logger.error(f"{source} 크롤링 중 오류: {e}")

    logger.info(f"{source}: {len(articles)} articles found")
    return articles


def fetch_9to5mac_news() -> list[dict]:
    return _fetch_apple_site_news("https://9to5mac.com", "9to5mac", "https://9to5mac.com")


def fetch_macrumors_news() -> list[dict]:
    return _fetch_apple_site_news("https://www.macrumors.com", "macrumors", "https://www.macrumors.com")
