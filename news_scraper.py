import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def fetch_9to5mac_news():
    """9to5Mac에서 애플 관련 뉴스 수집"""
    articles = []
    try:
        url = "https://9to5mac.com"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 최신 기사 찾기 (여러 가능한 선택자 시도)
        news_items = []
        for selector in ['article', '.post', '.article', '.entry']:
            items = soup.select(selector)
            if items:
                news_items = items[:5]  # 상위 5개 기사만
                break
        
        for item in news_items:
            try:
                # 제목 찾기 (여러 가능한 선택자 시도)
                title_elem = None
                for title_selector in ['h2', 'h3', '.title', '.entry-title']:
                    title_elem = item.select_one(title_selector)
                    if title_elem:
                        break
                
                if not title_elem:
                    continue
                    
                title = title_elem.text.strip()
                
                # 링크 찾기
                link_elem = item.select_one('a')
                if not link_elem or 'href' not in link_elem.attrs:
                    continue
                    
                link = link_elem['href']
                if not link.startswith('http'):
                    link = 'https://9to5mac.com' + link
                
                # 기사 내용 가져오기
                article_response = requests.get(link, headers=headers)
                article_response.raise_for_status()
                article_soup = BeautifulSoup(article_response.text, 'html.parser')
                
                # 본문 내용 추출 (여러 가능한 선택자 시도)
                content = None
                for content_selector in ['article', '.post-content', '.entry-content', '.article-content']:
                    content_elem = article_soup.select_one(content_selector)
                    if content_elem:
                        # 불필요한 요소 제거
                        for tag in content_elem.select('.advertisement, .related-posts, .comments, .social-share'):
                            tag.decompose()
                        content = content_elem.text.strip()
                        break
                
                if not content:
                    content = f"제목: {title}\n\n내용을 가져올 수 없습니다."
                
                articles.append({
                    'title': title,
                    'content': content,
                    'url': link,
                    'source': '9to5mac'
                })
                
                time.sleep(1)  # 요청 간격 조절
                
            except Exception as e:
                logger.error(f"9to5mac 기사 처리 중 오류: {e}")
                continue
                
    except Exception as e:
        logger.error(f"9to5mac 크롤링 중 오류: {e}")
    
    logger.info(f"9to5mac: {len(articles)} articles found")
    return articles

def fetch_macrumors_news():
    """MacRumors에서 애플 관련 뉴스 수집"""
    articles = []
    try:
        url = "https://www.macrumors.com"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 최신 기사 찾기 (여러 가능한 선택자 시도)
        news_items = []
        for selector in ['article', '.post', '.article', '.entry']:
            items = soup.select(selector)
            if items:
                news_items = items[:5]  # 상위 5개 기사만
                break
        
        for item in news_items:
            try:
                # 제목 찾기 (여러 가능한 선택자 시도)
                title_elem = None
                for title_selector in ['h2', 'h3', '.title', '.entry-title']:
                    title_elem = item.select_one(title_selector)
                    if title_elem:
                        break
                
                if not title_elem:
                    continue
                    
                title = title_elem.text.strip()
                
                # 링크 찾기
                link_elem = item.select_one('a')
                if not link_elem or 'href' not in link_elem.attrs:
                    continue
                    
                link = link_elem['href']
                if not link.startswith('http'):
                    link = 'https://www.macrumors.com' + link
                
                # 기사 내용 가져오기
                article_response = requests.get(link, headers=headers)
                article_response.raise_for_status()
                article_soup = BeautifulSoup(article_response.text, 'html.parser')
                
                # 본문 내용 추출 (여러 가능한 선택자 시도)
                content = None
                for content_selector in ['article', '.post-content', '.entry-content', '.article-content']:
                    content_elem = article_soup.select_one(content_selector)
                    if content_elem:
                        # 불필요한 요소 제거
                        for tag in content_elem.select('.advertisement, .related-posts, .comments, .social-share'):
                            tag.decompose()
                        content = content_elem.text.strip()
                        break
                
                if not content:
                    content = f"제목: {title}\n\n내용을 가져올 수 없습니다."
                
                articles.append({
                    'title': title,
                    'content': content,
                    'url': link,
                    'source': 'macrumors'
                })
                
                time.sleep(1)  # 요청 간격 조절
                
            except Exception as e:
                logger.error(f"MacRumors 기사 처리 중 오류: {e}")
                continue
                
    except Exception as e:
        logger.error(f"MacRumors 크롤링 중 오류: {e}")
    
    logger.info(f"MacRumors: {len(articles)} articles found")
    return articles