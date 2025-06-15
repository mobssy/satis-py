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
        # 뉴스 RSS 피드 URL 설정
        url = 'https://news.google.com/rss/search?q=new+jersey&hl=en-US&gl=US&ceid=US:en'
        # User-Agent 헤더는 서버에 요청하는 클라이언트 정보를 알려주는 역할로,
        # 봇 차단을 우회하기 위해 일반 브라우저처럼 가장함
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        # requests.get은 해당 URL에 HTTP GET 요청을 보내고 응답을 받음
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 요청 실패 시 예외 발생
        
        # BeautifulSoup은 HTML/XML 문서를 파싱하여 데이터를 쉽게 추출할 수 있게 도와줌
        soup = BeautifulSoup(response.content, 'xml')
        
        # RSS 피드 내 'item' 태그를 모두 찾아 리스트로 반환, 상위 5개만 선택
        items = soup.find_all('item')[:5]
        for item in items:
            try:
                # 각 뉴스 항목에서 제목, 링크, 설명이 존재하는지 확인
                if not item.title or not item.link or not item.description:
                    continue
                    
                # .text.strip()은 태그 안의 텍스트를 가져와 공백을 제거함
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
                
                # time.sleep(0.5)은 서버에 과도한 요청을 보내지 않도록 잠시 대기하는 역할
                time.sleep(0.5)
                
            except Exception as e:
                # 예외가 발생해도 프로그램이 멈추지 않고 계속 실행되도록 처리
                logger.error(f"뉴저지 뉴스 항목 처리 중 오류: {e}")
                continue
                
    except Exception as e:
        # 네트워크 오류 등 요청 단계에서 문제가 생겨도 프로그램 종료 방지
        logger.error(f"뉴저지 뉴스 크롤링 중 오류: {e}")
    
    logger.info(f"뉴저지: {len(news_list)} articles found")
    return news_list

def get_ny_hot_news():
    """구글 뉴스에서 뉴욕 관련 핫뉴스 5개 크롤링"""
    news_list = []
    try:
        # 뉴욕 뉴스 RSS 피드 URL 설정
        url = 'https://news.google.com/rss/search?q=new+york&hl=en-US&gl=US&ceid=US:en'
        # User-Agent 헤더는 서버에 요청하는 클라이언트 정보를 알려주는 역할로,
        # 봇 차단을 우회하기 위해 일반 브라우저처럼 가장함
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        # requests.get은 해당 URL에 HTTP GET 요청을 보내고 응답을 받음
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 요청 실패 시 예외 발생
        
        # BeautifulSoup은 HTML/XML 문서를 파싱하여 데이터를 쉽게 추출할 수 있게 도와줌
        soup = BeautifulSoup(response.content, 'xml')
        
        # RSS 피드 내 'item' 태그를 모두 찾아 리스트로 반환, 상위 5개만 선택
        items = soup.find_all('item')[:5]
        for item in items:
            try:
                # 각 뉴스 항목에서 제목, 링크, 설명이 존재하는지 확인
                if not item.title or not item.link or not item.description:
                    continue
                    
                # .text.strip()은 태그 안의 텍스트를 가져와 공백을 제거함
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
                
                # time.sleep(0.5)은 서버에 과도한 요청을 보내지 않도록 잠시 대기하는 역할
                time.sleep(0.5)
                
            except Exception as e:
                # 예외가 발생해도 프로그램이 멈추지 않고 계속 실행되도록 처리
                logger.error(f"뉴욕 뉴스 항목 처리 중 오류: {e}")
                continue
                
    except Exception as e:
        # 네트워크 오류 등 요청 단계에서 문제가 생겨도 프로그램 종료 방지
        logger.error(f"뉴욕 뉴스 크롤링 중 오류: {e}")
    
    logger.info(f"뉴욕: {len(news_list)} articles found")
    return news_list 