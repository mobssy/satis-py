import asyncio
import logging
from datetime import datetime
import pytz
from news_scraper import fetch_9to5mac_news, fetch_macrumors_news
from korean_news_scraper import get_naver_news, get_nate_news, get_google_world_news
from us_news_scraper import get_nj_hot_news, get_ny_hot_news
from telegram_sender import send_telegram_message
from summarizer import summarize_article

# 로깅 설정: 프로그램 실행 중 발생하는 정보나 오류를 기록하기 위한 설정입니다.
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('news_bot.log'),
        logging.StreamHandler()  # 콘솔에도 로그 출력
    ]
)
logger = logging.getLogger(__name__)

def get_current_time():
    """현재 시간을 EST 시간대로 반환하는 함수"""
    try:
        est = pytz.timezone('US/Eastern')
        return datetime.now(est)
    except Exception as e:
        logger.error(f"시간대 변환 중 오류 발생: {e}")
        return datetime.now()  # 오류 발생시 시스템 시간 반환

def is_tuesday():
    """오늘이 화요일인지 확인하는 함수"""
    current_time = get_current_time()
    return current_time.weekday() == 1  # 1은 화요일을 의미

def escape_markdown_v2(text):
    """Telegram MarkdownV2에서 특수 문자를 이스케이프 처리합니다."""
    if not text:  # text가 None이거나 빈 문자열인 경우 처리
        return ""
    escape_chars = '_*[]()~`>#+-=|{}.!'
    escaped_text = ""
    for char in text:
        if char in escape_chars:
            escaped_text += '\\' + char
        else:
            escaped_text += char
    return escaped_text

async def send_news_safely(message, news_type):
    """뉴스 전송을 안전하게 처리하는 함수"""
    try:
        if message:
            await send_telegram_message(message)
            logger.info(f"{news_type} 뉴스 전송 완료")
        else:
            logger.warning(f"{news_type} 뉴스 메시지가 비어있습니다.")
    except Exception as e:
        logger.error(f"{news_type} 뉴스 전송 중 오류 발생: {e}")

def create_news_message(news_list, news_type, emoji, escaped_time_for_header):
    """뉴스 메시지를 생성하는 공통 함수"""
    if not news_list:
        return None
    
    try:
        message = f"{emoji} {news_type} 뉴스 업데이트 {escaped_time_for_header}\n\n"
        seen_titles = set()
        filtered_news = []
        
        # 중복 제목 필터링
        for article in news_list:
            if article['title'] not in seen_titles:
                seen_titles.add(article['title'])
                filtered_news.append(article)
        
        logger.info(f"전송될 {news_type} 뉴스: {len(filtered_news)}개")
        
        # 각 기사를 메시지에 추가
        for article in filtered_news:
            try:
                summary = summarize_article(article['content'])
                escaped_title = escape_markdown_v2(article['title'])
                escaped_summary = escape_markdown_v2(summary)
                escaped_url = escape_markdown_v2(article['url'])
                message += f"📌 *{escaped_title}*\n\n"
                message += f"📝 {escaped_summary}\n\n"
                message += f"🔗 {escaped_url}\n\n"
            except Exception as e:
                logger.error(f"{news_type} 뉴스 기사 처리 중 오류 발생: {e}")
                continue
        
        return message
    except Exception as e:
        logger.error(f"{news_type} 뉴스 메시지 생성 중 오류 발생: {e}")
        return None

async def main():
    try:
        # 1. 뉴스 수집 시작
        logger.info("뉴스 수집 시작...")
        
        # 애플 관련 뉴스 수집
        apple_news = []
        if is_tuesday():
            try:
                apple_news.extend(fetch_9to5mac_news()[:3])
                apple_news.extend(fetch_macrumors_news()[:2])
                logger.info(f"애플 뉴스 {len(apple_news)}개 수집 완료")
            except Exception as e:
                logger.error(f"애플 뉴스 수집 중 오류 발생: {e}")
        else:
            logger.info("오늘은 화요일이 아니므로 애플 뉴스를 보내지 않습니다.")
        
        # 한국 뉴스 수집
        korean_news = []
        try:
            korean_news.extend(get_naver_news())
            korean_news.extend(get_nate_news())
            korean_news = korean_news[:5]
            logger.info(f"한국 뉴스 {len(korean_news)}개 수집 완료")
        except Exception as e:
            logger.error(f"한국 뉴스 수집 중 오류 발생: {e}")
        
        # 세계 뉴스 수집
        world_news = []
        try:
            world_news = get_google_world_news()
            logger.info(f"세계 뉴스 {len(world_news)}개 수집 완료")
        except Exception as e:
            logger.error(f"세계 뉴스 수집 중 오류 발생: {e}")
        
        # 미국 뉴스 수집
        us_news = []
        try:
            us_news.extend(get_nj_hot_news())
            us_news.extend(get_ny_hot_news())
            logger.info(f"미국 뉴스 {len(us_news)}개 수집 완료")
        except Exception as e:
            logger.error(f"미국 뉴스 수집 중 오류 발생: {e}")
        
        # 2. 텔레그램으로 뉴스 전송 준비
        current_time = get_current_time().strftime("%Y년 %m월 %d일 %H시 %M분")
        escaped_time_for_header = escape_markdown_v2(f"({current_time})")

        # --- 각 뉴스 타입별 메시지 생성 및 전송 ---
        news_configs = [
            (apple_news, "애플", "📱"),
            (korean_news, "한국", "🇰🇷"),
            (world_news, "세계", "🌍"),
            (us_news, "미국", "🇺🇸")
        ]
        
        for news_list, news_type, emoji in news_configs:
            if news_list:
                message = create_news_message(news_list, news_type, emoji, escaped_time_for_header)
                await send_news_safely(message, news_type)
        
        logger.info("모든 뉴스 전송 완료!")
        
    except Exception as e:
        logger.error(f"프로그램 실행 중 오류 발생: {e}")
        raise  # 상위 레벨에서도 오류를 처리할 수 있도록 예외를 다시 발생시킴

if __name__ == "__main__":
    # 비동기 main 함수 실행
    asyncio.run(main())