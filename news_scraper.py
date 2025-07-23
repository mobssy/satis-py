from bs4 import BeautifulSoup
from datetime import datetime
import logging
from http_client import safe_request

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
        # 9to5Mac 메인 페이지 URL 설정
        url = "https://9to5mac.com"
        
        # 공통 HTTP 클라이언트 사용
        response = safe_request(url)
        if not response:
            return articles
        
        # BeautifulSoup: HTML 파싱을 통해 문서 구조를 탐색할 수 있게 함
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 여러 선택자를 사용하는 이유:
        # 웹사이트 구조가 변경될 수 있으므로 다양한 CSS 선택자를 시도하여 최신 기사 요소를 찾음
        news_items = []
        for selector in ['article', '.post', '.article', '.entry']:
            # select: CSS 선택자를 사용해 여러 요소를 선택
            items = soup.select(selector)
            if items:
                news_items = items[:5]  # 상위 5개 기사만 선택
                break
        
        for item in news_items:
            try:
                # 제목 요소 찾기: 여러 선택자를 시도하여 제목을 찾음
                title_elem = None
                for title_selector in ['h2', 'h3', '.title', '.entry-title']:
                    # select_one: CSS 선택자로 단일 요소 선택
                    title_elem = item.select_one(title_selector)
                    if title_elem:
                        break
                
                if not title_elem:
                    continue  # 제목이 없으면 다음 기사로 넘어감
                    
                title = title_elem.text.strip()
                
                # 링크 요소 찾기
                link_elem = item.select_one('a')
                if not link_elem or 'href' not in link_elem.attrs:
                    continue  # 링크가 없으면 다음 기사로
                
                link = link_elem['href']
                if not link.startswith('http'):
                    # 상대경로인 경우 절대경로로 변환
                    link = 'https://9to5mac.com' + link
                
                # 기사 상세 페이지 요청 및 파싱
                article_response = safe_request(link)
                if not article_response:
                    continue
                article_soup = BeautifulSoup(article_response.text, 'html.parser')
                
                # 본문 내용 추출: 여러 선택자를 시도하여 본문을 찾음
                content = None
                for content_selector in ['article', '.post-content', '.entry-content', '.article-content']:
                    content_elem = article_soup.select_one(content_selector)
                    if content_elem:
                        # 불필요한 요소 제거 (광고, 관련 게시물 등)
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
                
                # 서버 과부하 방지는 safe_request에서 처리됨
                
            except Exception as e:
                # try-except: 개별 기사 처리 중 오류 발생시 로그 기록 후 다음 기사로 진행
                logger.error(f"9to5mac 기사 처리 중 오류: {e}")
                continue
                
    except Exception as e:
        # 전체 크롤링 과정에서 오류 발생시 로그 기록
        logger.error(f"9to5mac 크롤링 중 오류: {e}")
    
    # 수집된 기사 수 로그 출력
    logger.info(f"9to5mac: {len(articles)} articles found")
    return articles

def fetch_macrumors_news():
    """MacRumors에서 애플 관련 뉴스 수집"""
    articles = []
    try:
        # MacRumors 메인 페이지 URL 설정
        url = "https://www.macrumors.com"
        
        # 공통 HTTP 클라이언트 사용
        response = safe_request(url)
        if not response:
            return articles
        
        # BeautifulSoup: HTML 파싱을 통해 문서 구조를 탐색할 수 있게 함
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 여러 선택자를 사용하는 이유:
        # 웹사이트 구조가 변경될 수 있으므로 다양한 CSS 선택자를 시도하여 최신 기사 요소를 찾음
        news_items = []
        for selector in ['article', '.post', '.article', '.entry']:
            # select: CSS 선택자를 사용해 여러 요소를 선택
            items = soup.select(selector)
            if items:
                news_items = items[:5]  # 상위 5개 기사만 선택
                break
        
        for item in news_items:
            try:
                # 제목 요소 찾기: 여러 선택자를 시도하여 제목을 찾음
                title_elem = None
                for title_selector in ['h2', 'h3', '.title', '.entry-title']:
                    # select_one: CSS 선택자로 단일 요소 선택
                    title_elem = item.select_one(title_selector)
                    if title_elem:
                        break
                
                if not title_elem:
                    continue  # 제목이 없으면 다음 기사로 넘어감
                    
                title = title_elem.text.strip()
                
                # 링크 요소 찾기
                link_elem = item.select_one('a')
                if not link_elem or 'href' not in link_elem.attrs:
                    continue  # 링크가 없으면 다음 기사로
                
                link = link_elem['href']
                if not link.startswith('http'):
                    # 상대경로인 경우 절대경로로 변환
                    link = 'https://www.macrumors.com' + link
                
                # 기사 상세 페이지 요청 및 파싱
                article_response = safe_request(link)
                if not article_response:
                    continue
                article_soup = BeautifulSoup(article_response.text, 'html.parser')
                
                # 본문 내용 추출: 여러 선택자를 시도하여 본문을 찾음
                content = None
                for content_selector in ['article', '.post-content', '.entry-content', '.article-content']:
                    content_elem = article_soup.select_one(content_selector)
                    if content_elem:
                        # 불필요한 요소 제거 (광고, 관련 게시물 등)
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
                
                # 서버 과부하 방지는 safe_request에서 처리됨
                
            except Exception as e:
                # try-except: 개별 기사 처리 중 오류 발생시 로그 기록 후 다음 기사로 진행
                logger.error(f"MacRumors 기사 처리 중 오류: {e}")
                continue
                
    except Exception as e:
        # 전체 크롤링 과정에서 오류 발생시 로그 기록
        logger.error(f"MacRumors 크롤링 중 오류: {e}")
    
    # 수집된 기사 수 로그 출력
    logger.info(f"MacRumors: {len(articles)} articles found")
    return articles