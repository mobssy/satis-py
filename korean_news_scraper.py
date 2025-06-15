import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def get_naver_news():
    """네이버 실시간 인기 뉴스 수집"""
    articles = []
    try:
        # 네이버 뉴스 메인 페이지
        url = "https://news.naver.com/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 실시간 인기 뉴스 섹션 찾기 (여러 가능한 선택자 시도)
        news_items = []
        for selector in ['.cc_text_list li', '.newsnow_txarea li', '.newsnow_cont li', '.newsnow_cont a']:
            items = soup.select(selector)
            if items:
                news_items = items[:5]  # 상위 5개 기사만
                break
        
        for item in news_items:
            try:
                link_elem = item.find('a')
                if not link_elem or 'href' not in link_elem.attrs:
                    continue
                    
                link = link_elem['href']
                if not link.startswith('http'):
                    link = 'https://news.naver.com' + link
                    
                title = link_elem.text.strip()
                if not title:
                    continue
                
                # 기사 내용 가져오기
                article_response = requests.get(link, headers=headers)
                article_response.raise_for_status()
                article_soup = BeautifulSoup(article_response.text, 'html.parser')
                
                # 본문 내용 추출 (여러 가능한 선택자 시도)
                content = None
                for selector in ['#articeBody', '#articleBodyContents', '.article_body', '.article_view', '#newsEndContents']:
                    content_elem = article_soup.select_one(selector)
                    if content_elem:
                        # 불필요한 요소 제거
                        for tag in content_elem.select('.end_photo_org, .source, .copyright, .reporter_area, .article_info'):
                            tag.decompose()
                        content = content_elem.text.strip()
                        break
                
                # content가 없어도 기본값 설정
                if not content:
                    content = f"제목: {title}\n\n내용을 가져올 수 없습니다."
                
                articles.append({
                    'title': title,
                    'content': content,
                    'url': link,
                    'source': 'naver'
                })
                
                time.sleep(1)  # 요청 간격 조절
                
            except Exception as e:
                logger.error(f"네이버 기사 처리 중 오류: {e}")
                continue
                
    except Exception as e:
        logger.error(f"네이버 크롤링 중 오류: {e}")
    
    return articles

def get_nate_news():
    """네이트 실시간 인기 뉴스 수집"""
    articles = []
    try:
        # 네이트 뉴스 메인 페이지
        url = "https://news.nate.com/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 실시간 인기 뉴스 섹션 찾기 (여러 가능한 선택자 시도)
        news_items = []
        for selector in ['.mlt01', '.mlt02', '.mlt03', '.newsCont', '.mlt01 a', '.mlt02 a', '.mlt03 a']:
            items = soup.select(selector)
            if items:
                news_items = items[:5]  # 상위 5개 기사만
                break
        
        for item in news_items:
            try:
                link_elem = item.find('a')
                if not link_elem or 'href' not in link_elem.attrs:
                    continue
                    
                link = link_elem['href']
                if not link.startswith('http'):
                    link = 'https:' + link
                    
                title = link_elem.text.strip()
                if not title:
                    continue
                
                # 기사 내용 가져오기
                article_response = requests.get(link, headers=headers)
                article_response.raise_for_status()
                article_soup = BeautifulSoup(article_response.text, 'html.parser')
                
                # 본문 내용 추출 (여러 가능한 선택자 시도)
                content = None
                for selector in ['#articleCont', '.articleCont', '.article_view', '.article_body', '#newsEndContents']:
                    content_elem = article_soup.select_one(selector)
                    if content_elem:
                        # 불필요한 요소 제거
                        for tag in content_elem.select('.end_photo_org, .source, .copyright, .reporter_area, .article_info'):
                            tag.decompose()
                        content = content_elem.text.strip()
                        break
                
                # content가 없어도 기본값 설정
                if not content:
                    content = f"제목: {title}\n\n내용을 가져올 수 없습니다."
                
                articles.append({
                    'title': title,
                    'content': content,
                    'url': link,
                    'source': 'nate'
                })
                
                time.sleep(1)  # 요청 간격 조절
                
            except Exception as e:
                logger.error(f"네이트 기사 처리 중 오류: {e}")
                continue
                
    except Exception as e:
        logger.error(f"네이트 크롤링 중 오류: {e}")
    
    return articles

def get_google_world_news():
    """구글 뉴스에서 세계 핫뉴스 5개 크롤링"""
    news_list = []
    try:
        # Google News RSS for World News
        url = 'https://news.google.com/rss/search?q=world+news&hl=en-US&gl=US&ceid=US:en'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'xml')
        
        items = soup.find_all('item')[:5]
        for item in items:
            try:
                if not item.title or not item.link or not item.description:
                    continue
                    
                title = item.title.text.strip()
                link = item.link.text.strip()
                summary = item.description.text.strip()
                
                if not title or not link or not summary:
                    continue
                
                news_list.append({
                    'title': f"[세계] {title}",
                    'url': link,
                    'content': summary
                })
                
                time.sleep(0.5)  # 요청 간격 조절
                
            except Exception as e:
                logger.error(f"구글 세계 뉴스 항목 처리 중 오류: {e}")
                continue
                
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