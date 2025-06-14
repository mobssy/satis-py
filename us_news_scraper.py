import requests
from bs4 import BeautifulSoup
import logging
import time

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def get_nj_hot_news():
    """구글 뉴스에서 뉴저지 관련 핫뉴스 5개 크롤링"""
    news_list = []
    try:
        url = 'https://news.google.com/rss/search?q=new+jersey&hl=en-US&gl=US&ceid=US:en'
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
                    'title': f"[뉴저지] {title}",
                    'url': link,
                    'content': summary
                })
                
                time.sleep(0.5)  # 요청 간격 조절
                
            except Exception as e:
                logger.error(f"뉴저지 뉴스 항목 처리 중 오류: {e}")
                continue
                
    except Exception as e:
        logger.error(f"뉴저지 뉴스 크롤링 중 오류: {e}")
    
    logger.info(f"뉴저지: {len(news_list)} articles found")
    return news_list

def get_ny_hot_news():
    """구글 뉴스에서 뉴욕 관련 핫뉴스 5개 크롤링"""
    news_list = []
    try:
        url = 'https://news.google.com/rss/search?q=new+york&hl=en-US&gl=US&ceid=US:en'
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
                    'title': f"[뉴욕] {title}",
                    'url': link,
                    'content': summary
                })
                
                time.sleep(0.5)  # 요청 간격 조절
                
            except Exception as e:
                logger.error(f"뉴욕 뉴스 항목 처리 중 오류: {e}")
                continue
                
    except Exception as e:
        logger.error(f"뉴욕 뉴스 크롤링 중 오류: {e}")
    
    logger.info(f"뉴욕: {len(news_list)} articles found")
    return news_list 