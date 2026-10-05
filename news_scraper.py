import logging
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from http_client import safe_request

logger = logging.getLogger(__name__)

_LIST_SELECTORS = ['article', '.post', '.article', '.entry']
_TITLE_SELECTORS = ['h2', 'h3', '.title', '.entry-title']
_NOISE_SELECTORS = '.advertisement, .related-posts, .comments, .social-share'


def _resolve_link(title_elem, item, base_url: str) -> str | None:
    """제목에 걸린 링크를 우선 사용 (카드의 첫 링크는 태그/카테고리일 수 있음)"""
    link_elem = title_elem.find('a') or title_elem.find_parent('a') or item.select_one('a')
    if not link_elem or not link_elem.get('href'):
        return None
    # 일부 href에 따옴표가 섞여 있어 제거한 뒤 상대 경로를 합친다
    return urljoin(base_url, link_elem['href'].strip().strip('"\''))


def _fetch_apple_site_news(
    url: str,
    source: str,
    base_url: str,
    content_selectors: list[str],
    max_items: int = 5,
) -> list[dict]:
    """애플 뉴스 사이트 공통 스크래핑 로직

    같은 기사가 큰 카드와 사이드바 카드로 중복 노출되므로 URL 기준으로 중복을 제거한다.
    """
    articles = []
    try:
        response = safe_request(url)
        if not response:
            return articles

        soup = BeautifulSoup(response.text, 'html.parser')
        news_items = []
        for selector in _LIST_SELECTORS:
            news_items = soup.select(selector)
            if news_items:
                break

        seen_links = set()
        for item in news_items:
            if len(articles) >= max_items:
                break
            try:
                title_elem = next(
                    (item.select_one(s) for s in _TITLE_SELECTORS if item.select_one(s)),
                    None
                )
                if not title_elem:
                    continue

                title = title_elem.get_text(' ', strip=True)
                link = _resolve_link(title_elem, item, base_url)
                if not title or not link or link in seen_links:
                    continue
                seen_links.add(link)

                article_response = safe_request(link)
                if not article_response:
                    continue

                article_soup = BeautifulSoup(article_response.text, 'html.parser')
                content = None
                for content_selector in content_selectors:
                    content_elem = article_soup.select_one(content_selector)
                    if content_elem:
                        for tag in content_elem.select(_NOISE_SELECTORS):
                            tag.decompose()
                        content = content_elem.get_text(' ', strip=True)
                        break

                articles.append({
                    'title': title,
                    'content': content,
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
    return _fetch_apple_site_news(
        "https://9to5mac.com", "9to5mac", "https://9to5mac.com",
        content_selectors=['.post-content', '.entry-content'],
    )


def fetch_macrumors_news() -> list[dict]:
    return _fetch_apple_site_news(
        "https://www.macrumors.com", "macrumors", "https://www.macrumors.com",
        content_selectors=['.js-content', '[class*=ugc]'],
    )
