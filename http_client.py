import requests
import time
import random
import logging

logger = logging.getLogger(__name__)

DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
}

def safe_request(url: str, headers: dict = None, delay: float = 1, timeout: int = 30):
    """안전한 HTTP GET 요청. 실패 시 None 반환."""
    try:
        request_headers = DEFAULT_HEADERS.copy()
        if headers:
            request_headers.update(headers)

        response = requests.get(url, headers=request_headers, timeout=timeout)
        response.raise_for_status()

        if delay > 0:
            time.sleep(delay)

        return response

    except requests.exceptions.Timeout:
        logger.error(f"요청 타임아웃: {url}")
    except requests.exceptions.ConnectionError:
        logger.error(f"연결 오류: {url}")
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP 오류 ({e.response.status_code}): {url}")
    except Exception as e:
        logger.error(f"예상치 못한 오류: {url} - {e}")

    return None

def fetch_with_retry(url: str, max_retries: int = 3, headers: dict = None, delay: float = 1, timeout: int = 30):
    """재시도 로직 포함 HTTP 요청. jitter 적용으로 thundering herd 방지."""
    for attempt in range(max_retries + 1):
        response = safe_request(url, headers, delay, timeout)
        if response is not None:
            return response

        if attempt < max_retries:
            wait_time = (attempt + 1) * 2 + random.uniform(0, 1)
            logger.info(f"요청 실패, {wait_time:.1f}초 후 재시도... ({attempt + 1}/{max_retries})")
            time.sleep(wait_time)

    logger.error(f"모든 재시도 실패: {url}")
    return None
