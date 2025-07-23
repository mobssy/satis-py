from bs4 import BeautifulSoup
from datetime import datetime
import logging
from http_client import safe_request

# 로깅 설정: 프로그램 실행 중 발생하는 정보를 기록하기 위한 설정입니다.
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def get_naver_news():
    """네이버 실시간 인기 뉴스 수집 함수입니다."""
    articles = []
    try:
        # 네이버 뉴스 메인 페이지 URL입니다.
        url = "https://news.naver.com/"
        # 웹사이트에 접속할 때 사용하는 헤더 정보입니다. 브라우저를 흉내냅니다.
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        
        # requests.get: URL에 접속하여 웹 페이지 내용을 가져옵니다.
        response = requests.get(url, headers=headers)
        # 접속에 문제가 있으면 예외를 발생시킵니다.
        response.raise_for_status()
        
        # BeautifulSoup: 가져온 HTML 문서를 파이썬에서 다루기 쉽게 변환합니다.
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 실시간 인기 뉴스 섹션을 찾기 위해 여러 CSS 선택자를 시도합니다.
        # 웹 페이지 구조가 바뀔 수 있어 여러 선택자를 시도하는 것입니다.
        news_items = []
        for selector in ['.cc_text_list li', '.newsnow_txarea li', '.newsnow_cont li', '.newsnow_cont a']:
            # soup.select: CSS 선택자를 사용해 원하는 요소들을 찾습니다.
            items = soup.select(selector)
            if items:
                # 상위 5개 뉴스만 가져옵니다.
                news_items = items[:5]
                break
        
        # 찾은 뉴스 항목들을 하나씩 처리합니다.
        for item in news_items:
            try:
                # item.find('a'): 뉴스 제목과 링크가 있는 <a> 태그를 찾습니다.
                link_elem = item.find('a')
                if not link_elem or 'href' not in link_elem.attrs:
                    # 링크가 없으면 다음 항목으로 넘어갑니다.
                    continue
                    
                link = link_elem['href']
                if not link.startswith('http'):
                    # 상대경로인 경우 절대경로로 변환합니다.
                    link = 'https://news.naver.com' + link
                    
                title = link_elem.text.strip()
                if not title:
                    # 제목이 없으면 다음 항목으로 넘어갑니다.
                    continue
                
                # 뉴스 기사 본문 내용을 가져오기 위해 다시 요청합니다.
                article_response = requests.get(link, headers=headers)
                article_response.raise_for_status()
                article_soup = BeautifulSoup(article_response.text, 'html.parser')
                
                # 본문 내용 추출을 위해 여러 선택자를 시도합니다.
                content = None
                for selector in ['#articeBody', '#articleBodyContents', '.article_body', '.article_view', '#newsEndContents']:
                    content_elem = article_soup.select_one(selector)
                    if content_elem:
                        # 본문 내 불필요한 요소를 제거합니다.
                        for tag in content_elem.select('.end_photo_org, .source, .copyright, .reporter_area, .article_info'):
                            tag.decompose()
                        content = content_elem.text.strip()
                        break
                
                # 본문 내용이 없으면 기본 메시지를 설정합니다.
                if not content:
                    content = f"제목: {title}\n\n내용을 가져올 수 없습니다."
                
                # 수집한 정보를 리스트에 저장합니다.
                articles.append({
                    'title': title,
                    'content': content,
                    'url': link,
                    'source': 'naver'
                })
                
                # time.sleep: 서버에 부담을 주지 않기 위해 잠시 멈춥니다.
                time.sleep(1)
                
            except Exception as e:
                # 개별 뉴스 처리 중 오류가 발생해도 전체 크롤링은 계속 진행합니다.
                logger.error(f"네이버 기사 처리 중 오류: {e}")
                continue
                
    except Exception as e:
        # 네이버 뉴스 페이지 접속이나 파싱 중 오류가 발생하면 기록합니다.
        logger.error(f"네이버 크롤링 중 오류: {e}")
    
    return articles

def get_nate_news():
    """네이트 실시간 인기 뉴스 수집 함수입니다."""
    articles = []
    try:
        # 네이트 뉴스 메인 페이지 URL입니다.
        url = "https://news.nate.com/"
        # 접속 시 사용하는 헤더 정보입니다.
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        
        # requests.get: 네이트 뉴스 페이지 내용을 가져옵니다.
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # BeautifulSoup으로 HTML 파싱
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 여러 CSS 선택자를 시도해 실시간 인기 뉴스 영역을 찾습니다.
        news_items = []
        for selector in ['.mlt01', '.mlt02', '.mlt03', '.newsCont', '.mlt01 a', '.mlt02 a', '.mlt03 a']:
            items = soup.select(selector)
            if items:
                news_items = items[:5]
                break
        
        # 찾은 뉴스 항목들을 하나씩 처리합니다.
        for item in news_items:
            try:
                # 뉴스 링크와 제목이 있는 <a> 태그를 찾습니다.
                link_elem = item.find('a')
                if not link_elem or 'href' not in link_elem.attrs:
                    continue
                    
                link = link_elem['href']
                if not link.startswith('http'):
                    # 상대경로를 절대경로로 변환합니다.
                    link = 'https:' + link
                    
                title = link_elem.text.strip()
                if not title:
                    continue
                
                # 뉴스 기사 본문 내용 요청 및 파싱
                article_response = requests.get(link, headers=headers)
                article_response.raise_for_status()
                article_soup = BeautifulSoup(article_response.text, 'html.parser')
                
                # 본문 내용 추출 시도
                content = None
                for selector in ['#articleCont', '.articleCont', '.article_view', '.article_body', '#newsEndContents']:
                    content_elem = article_soup.select_one(selector)
                    if content_elem:
                        # 불필요한 요소 제거
                        for tag in content_elem.select('.end_photo_org, .source, .copyright, .reporter_area, .article_info'):
                            tag.decompose()
                        content = content_elem.text.strip()
                        break
                
                if not content:
                    content = f"제목: {title}\n\n내용을 가져올 수 없습니다."
                
                # 수집한 뉴스 정보를 리스트에 저장
                articles.append({
                    'title': title,
                    'content': content,
                    'url': link,
                    'source': 'nate'
                })
                
                # 서버 부담 방지를 위해 잠시 대기
                time.sleep(1)
                
            except Exception as e:
                # 개별 뉴스 처리 중 오류 발생 시 로그 기록 후 계속 진행
                logger.error(f"네이트 기사 처리 중 오류: {e}")
                continue
                
    except Exception as e:
        # 전체 크롤링 중 오류 발생 시 로그 기록
        logger.error(f"네이트 크롤링 중 오류: {e}")
    
    return articles

def get_google_world_news():
    """구글 뉴스에서 세계 핫뉴스 5개를 크롤링하는 함수입니다."""
    news_list = []
    try:
        # 구글 뉴스 세계 뉴스 RSS 주소입니다.
        url = 'https://news.google.com/rss/search?q=world+news&hl=en-US&gl=US&ceid=US:en'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        # RSS 피드를 요청합니다.
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # XML 형식의 RSS를 파싱합니다.
        soup = BeautifulSoup(response.content, 'xml')
        
        # <item> 태그는 각각의 뉴스 기사 정보를 담고 있습니다. 상위 5개만 선택합니다.
        items = soup.find_all('item')[:5]
        for item in items:
            try:
                # 제목, 링크, 설명이 모두 있어야 처리합니다.
                if not item.title or not item.link or not item.description:
                    continue
                    
                title = item.title.text.strip()
                link = item.link.text.strip()
                summary = item.description.text.strip()
                
                if not title or not link or not summary:
                    continue
                
                # 수집한 뉴스 정보를 리스트에 저장합니다.
                news_list.append({
                    'title': f"[세계] {title}",
                    'url': link,
                    'content': summary
                })
                
                # 서버에 부담을 주지 않도록 짧게 대기합니다.
                time.sleep(0.5)
                
            except Exception as e:
                # 개별 뉴스 항목 처리 중 오류 발생 시 로그 기록 후 계속 진행
                logger.error(f"구글 세계 뉴스 항목 처리 중 오류: {e}")
                continue
                
    except Exception as e:
        # 전체 크롤링 중 오류 발생 시 로그 기록
        logger.error(f"구글 세계 뉴스 크롤링 중 오류: {e}")
    
    # 수집된 뉴스 개수를 로그로 출력합니다.
    logger.info(f"세계: {len(news_list)} articles found")
    return news_list

if __name__ == "__main__":
    # 세 개의 함수에서 수집한 뉴스들을 합칩니다.
    news = get_naver_news() + get_nate_news() + get_google_world_news()
    # 수집한 뉴스 목록을 출력합니다.
    for article in news:
        print(f"\n제목: {article['title']}")
        print(f"URL: {article['url']}")
        print("-" * 50)