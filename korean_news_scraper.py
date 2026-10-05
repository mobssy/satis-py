import logging
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from http_client import safe_request
from google_rss_scraper import fetch_google_rss_news
from article import Article

logger = logging.getLogger(__name__)

_NOISE_SELECTORS = '.end_photo_org, .source, .copyright, .reporter_area, .article_info'

def _fetch_korean_news(
    url: str,
    source: str,
    base_url: str,
    list_selectors: list[str],
    content_selectors: list[str],
    title_selectors: list[str],
    max_items: int = 10,
) -> list[Article]:
    """한국 뉴스 사이트 공통 스크래핑 로직

    목록 항목은 <a> 자체이거나 <a>를 포함하는 요소일 수 있다.
    제목은 title_selectors로 찾고, 없으면 링크 텍스트를 사용한다.
    """
    articles = []
    try:
        response = safe_request(url)
        if not response:
            return articles

        soup = BeautifulSoup(response.text, 'html.parser')
        news_items = []
        for selector in list_selectors:
            items = soup.select(selector)
            if items:
                news_items = items[:max_items]
                break

        for item in news_items:
            try:
                link_elem = item if item.name == 'a' else item.find('a')
                if not link_elem or 'href' not in link_elem.attrs:
                    continue

                # "//host/path" 같은 프로토콜 상대 경로도 올바르게 합친다
                link = urljoin(base_url, link_elem['href'])

                title_elem = next(
                    (item.select_one(s) for s in title_selectors if item.select_one(s)),
                    link_elem,
                )
                title = title_elem.get_text(' ', strip=True)
                if not title:
                    continue

                article_response = safe_request(link)
                if not article_response:
                    continue

                article_soup = BeautifulSoup(article_response.text, 'html.parser')
                content = None
                for selector in content_selectors:
                    content_elem = article_soup.select_one(selector)
                    if content_elem:
                        for tag in content_elem.select(_NOISE_SELECTORS):
                            tag.decompose()
                        content = content_elem.text.strip()
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


def get_naver_news() -> list[Article]:
    return _fetch_korean_news(
        url="https://news.naver.com/",
        source="naver",
        base_url="https://news.naver.com",
        list_selectors=['.cjs_nf_list a.cjs_nf_a'],
        content_selectors=['#dic_area', '#newsct_article'],
        title_selectors=['.cn_title'],
    )


def get_nate_news() -> list[Article]:
    return _fetch_korean_news(
        url="https://news.nate.com/",
        source="nate",
        base_url="https://news.nate.com",
        list_selectors=['.mlt01'],
        content_selectors=['#realArtcContents', '#articleCont'],
        title_selectors=['.tit'],
    )


def get_google_world_news() -> list[Article]:
    """구글 뉴스 RSS에서 세계 핫뉴스 수집"""
    return fetch_google_rss_news("world+news", "세계")


if __name__ == "__main__":
    news = get_naver_news() + get_nate_news() + get_google_world_news()
    for article in news:
        print(f"\n제목: {article['title']}")
        print(f"URL: {article['url']}")
        print("-" * 50)
