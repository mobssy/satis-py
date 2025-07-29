from bs4 import BeautifulSoup
import logging
from http_client import safe_request

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def get_bigtech_news():
    """구글 뉴스에서 빅테크 회사 관련 뉴스 5개 크롤링"""
    news_list = []
    try:
        # 빅테크 키워드: Apple, Google, Microsoft, Amazon, Meta, Tesla, NVIDIA
        bigtech_keywords = "Apple OR Google OR Microsoft OR Amazon OR Meta OR Tesla OR NVIDIA OR OpenAI"
        url = f'https://news.google.com/rss/search?q={bigtech_keywords}&hl=en-US&gl=US&ceid=US:en'
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        # safe_request: 공통 HTTP 클라이언트 사용
        response = safe_request(url, headers)
        if not response:
            return news_list
        
        # BeautifulSoup으로 XML 파싱
        soup = BeautifulSoup(response.content, 'xml')
        
        # RSS 피드 내 'item' 태그를 모두 찾아 상위 5개만 선택
        items = soup.find_all('item')[:5]
        for item in items:
            try:
                # 각 뉴스 항목에서 제목, 링크, 설명이 존재하는지 확인
                if not item.title or not item.link or not item.description:
                    continue
                    
                title = item.title.text.strip()
                link = item.link.text.strip()
                summary = item.description.text.strip()
                
                if not title or not link or not summary:
                    continue
                
                # 빅테크 회사명을 제목 앞에 태그로 추가
                company_tag = ""
                title_lower = title.lower()
                if "apple" in title_lower:
                    company_tag = "[Apple] "
                elif "google" in title_lower or "alphabet" in title_lower:
                    company_tag = "[Google] "
                elif "microsoft" in title_lower:
                    company_tag = "[Microsoft] "
                elif "amazon" in title_lower:
                    company_tag = "[Amazon] "
                elif "meta" in title_lower or "facebook" in title_lower:
                    company_tag = "[Meta] "
                elif "tesla" in title_lower:
                    company_tag = "[Tesla] "
                elif "nvidia" in title_lower:
                    company_tag = "[NVIDIA] "
                elif "openai" in title_lower:
                    company_tag = "[OpenAI] "
                else:
                    company_tag = "[BigTech] "
                
                news_list.append({
                    'title': f"{company_tag}{title}",
                    'url': link,
                    'content': summary
                })
                
            except Exception as e:
                logger.error(f"빅테크 뉴스 항목 처리 중 오류: {e}")
                continue
                
    except Exception as e:
        logger.error(f"빅테크 뉴스 크롤링 중 오류: {e}")
    
    logger.info(f"빅테크: {len(news_list)} articles found")
    return news_list