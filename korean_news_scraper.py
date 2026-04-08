import logging
from bs4 import BeautifulSoup
from http_client import safe_request

logger = logging.getLogger(__name__)

_NOISE_SELECTORS = '.end_photo_org, .source, .copyright, .reporter_area, .article_info'

def _fetch_korean_news(
    url: str,
    source: str,
    base_url: str,
    list_selectors: list[str],
    content_selectors: list[str],
) -> list[dict]:
    """한국 뉴스 사이트 공통 스크래핑 로직"""
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
                news_items = items[:5]
                break

        for item in news_items:
            try:
                link_elem = item.find('a')
                if not link_elem or 'href' not in link_elem.attrs:
                    continue

                link = link_elem['href']
                if not link.startswith('http'):
                    link = base_url + link

                title = link_elem.text.strip()
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
                    'content': content or f"제목: {title}\n\n내용을 가져올 수 없습니다.",
                    'url': link,
                    'source': source,
                })

            except Exception as e:
                logger.error(f"{source} 기사 처리 중 오류: {e}")

    except Exception as e:
        logger.error(f"{source} 크롤링 중 오류: {e}")

    return articles


def get_naver_news() -> list[dict]:
    return _fetch_korean_news(
        url="https://news.naver.com/",
        source="naver",
        base_url="https://news.naver.com",
        list_selectors=['.cc_text_list li', '.newsnow_txarea li', '.newsnow_cont li', '.newsnow_cont a'],
        content_selectors=['#articeBody', '#articleBodyContents', '.article_body', '.article_view', '#newsEndContents'],
    )


def get_nate_news() -> list[dict]:
    return _fetch_korean_news(
        url="https://news.nate.com/",
        source="nate",
        base_url="https:",
        list_selectors=['.mlt01', '.mlt02', '.mlt03', '.newsCont', '.mlt01 a', '.mlt02 a', '.mlt03 a'],
        content_selectors=['#articleCont', '.articleCont', '.article_view', '.article_body', '#newsEndContents'],
    )


def get_google_world_news() -> list[dict]:
    """구글 뉴스 RSS에서 세계 핫뉴스 수집"""
    news_list = []
    try:
        url = 'https://news.google.com/rss/search?q=world+news&hl=en-US&gl=US&ceid=US:en'
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

                if not (title and link and summary):
                    continue

                news_list.append({
                    'title': f"[세계] {title}",
                    'url': link,
                    'content': summary,
                })

            except Exception as e:
                logger.error(f"구글 세계 뉴스 항목 처리 중 오류: {e}")

    except Exception as e:
        logger.error(f"구글 세계 뉴스 크롤링 중 오류: {e}")

    logger.info(f"세계: {len(news_list)} articles found")
    return news_list


if __name__ == "__main__":
    news = get_naver_news() + get_nate_news() + get_google_world_news()
    for article in news:
        print(f"\n제목: {article['title']}")
        print(f"URL: {article['url']}")
        print("-" * 50)
