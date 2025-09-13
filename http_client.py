# http_client.py
import requests
import aiohttp
import asyncio
import time
import logging
from typing import Optional

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# 공통 헤더 설정
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
}

def safe_request(url, headers=None, delay=1, timeout=30):
    """
    안전한 HTTP 요청을 수행하는 공통 함수
    
    Args:
        url (str): 요청할 URL
        headers (dict, optional): 추가 헤더. 기본 헤더와 병합됨
        delay (float): 요청 후 대기 시간 (초)
        timeout (int): 요청 타임아웃 (초)
    
    Returns:
        requests.Response: 응답 객체 또는 None (오류 시)
    """
    try:
        # 기본 헤더와 사용자 헤더 병합
        request_headers = DEFAULT_HEADERS.copy()
        if headers:
            request_headers.update(headers)
        
        # HTTP 요청 실행
        response = requests.get(url, headers=request_headers, timeout=timeout)
        response.raise_for_status()  # 4xx, 5xx 상태 코드 시 예외 발생
        
        # 서버 부담 방지를 위한 대기
        if delay > 0:
            time.sleep(delay)
        
        logger.debug(f"성공적으로 요청: {url}")
        return response
        
    except requests.exceptions.Timeout:
        logger.error(f"요청 타임아웃: {url}")
        return None
    except requests.exceptions.ConnectionError:
        logger.error(f"연결 오류: {url}")
        return None
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP 오류 ({e.response.status_code}): {url}")
        return None
    except Exception as e:
        logger.error(f"요청 중 예상치 못한 오류: {url} - {e}")
        return None

def fetch_with_retry(url, max_retries=3, headers=None, delay=1, timeout=30):
    """
    재시도 로직이 포함된 HTTP 요청 함수
    
    Args:
        url (str): 요청할 URL
        max_retries (int): 최대 재시도 횟수
        headers (dict, optional): 추가 헤더
        delay (float): 요청 후 대기 시간 (초)
        timeout (int): 요청 타임아웃 (초)
    
    Returns:
        requests.Response: 응답 객체 또는 None (모든 재시도 실패 시)
    """
    for attempt in range(max_retries + 1):
        response = safe_request(url, headers, delay, timeout)
        if response is not None:
            return response
        
        if attempt < max_retries:
            wait_time = (attempt + 1) * 2  # 지수적 백오프
            logger.info(f"요청 실패, {wait_time}초 후 재시도... ({attempt + 1}/{max_retries})")
            time.sleep(wait_time)
    
    logger.error(f"모든 재시도 실패: {url}")
    return None


async def safe_request_async(url: str, headers: Optional[dict] = None, delay: float = 1, timeout: int = 30) -> Optional[str]:
    """
    비동기 HTTP 요청을 수행하는 함수
    
    Args:
        url (str): 요청할 URL
        headers (dict, optional): 추가 헤더. 기본 헤더와 병합됨
        delay (float): 요청 후 대기 시간 (초)
        timeout (int): 요청 타임아웃 (초)
    
    Returns:
        str: 응답 텍스트 또는 None (오류 시)
    """
    try:
        # 기본 헤더와 사용자 헤더 병합
        request_headers = DEFAULT_HEADERS.copy()
        if headers:
            request_headers.update(headers)
        
        # 비동기 HTTP 요청 실행
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
            async with session.get(url, headers=request_headers) as response:
                response.raise_for_status()
                content = await response.text()
                
                # 서버 부담 방지를 위한 대기
                if delay > 0:
                    await asyncio.sleep(delay)
                
                logger.debug(f"성공적으로 요청: {url}")
                return content
                
    except aiohttp.ClientResponseError as e:
        logger.error(f"HTTP 오류 ({e.status}): {url}")
        return None
    except asyncio.TimeoutError:
        logger.error(f"요청 타임아웃: {url}")
        return None
    except aiohttp.ClientError:
        logger.error(f"연결 오류: {url}")
        return None
    except Exception as e:
        logger.error(f"요청 중 예상치 못한 오류: {url} - {e}")
        return None


async def fetch_with_retry_async(url: str, max_retries: int = 3, headers: Optional[dict] = None, delay: float = 1, timeout: int = 30) -> Optional[str]:
    """
    재시도 로직이 포함된 비동기 HTTP 요청 함수
    
    Args:
        url (str): 요청할 URL
        max_retries (int): 최대 재시도 횟수
        headers (dict, optional): 추가 헤더
        delay (float): 요청 후 대기 시간 (초)
        timeout (int): 요청 타임아웃 (초)
    
    Returns:
        str: 응답 텍스트 또는 None (모든 재시도 실패 시)
    """
    for attempt in range(max_retries + 1):
        content = await safe_request_async(url, headers, delay, timeout)
        if content is not None:
            return content
        
        if attempt < max_retries:
            wait_time = (attempt + 1) * 2  # 지수적 백오프
            logger.info(f"요청 실패, {wait_time}초 후 재시도... ({attempt + 1}/{max_retries})")
            await asyncio.sleep(wait_time)
    
    logger.error(f"모든 재시도 실패: {url}")
    return None