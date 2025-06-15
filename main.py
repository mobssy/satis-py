import asyncio
import logging
from datetime import datetime
from news_scraper import fetch_9to5mac_news, fetch_macrumors_news
from korean_news_scraper import get_naver_news, get_nate_news, get_google_world_news
from us_news_scraper import get_nj_hot_news, get_ny_hot_news
from telegram_sender import send_telegram_message
from summarizer import summarize_article

# 로깅 설정: 프로그램 실행 중 발생하는 정보나 오류를 기록하기 위한 설정입니다.
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def escape_markdown_v2(text):
    """Telegram MarkdownV2에서 특수 문자를 이스케이프 처리합니다.
    Telegram 메시지에서 특수 문자가 제대로 표시되도록 앞에 백슬래시를 붙입니다."""
    # 이스케이프해야 할 특수 문자 목록입니다.
    escape_chars = '_*[]()~`>#+-=|{}.!'
    escaped_text = ""
    for char in text:
        if char in escape_chars:
            escaped_text += '\\' + char  # 특수 문자 앞에 '\' 추가
        else:
            escaped_text += char
    return escaped_text

async def main():
    try:
        # 1. 뉴스 수집 시작
        logger.info("뉴스 수집 시작...")
        
        # 애플 관련 뉴스 수집: 9to5mac에서 3개, MacRumors에서 2개 뉴스 가져오기
        apple_news = []
        apple_news.extend(fetch_9to5mac_news()[:3])  # 9to5mac 뉴스 3개 수집
        apple_news.extend(fetch_macrumors_news()[:2])  # MacRumors 뉴스 2개 수집
        logger.info(f"애플 뉴스 {len(apple_news)}개 수집 완료")
        
        # 한국 뉴스 수집: 네이버와 네이트에서 뉴스 수집 후 총 5개로 제한
        korean_news = []
        korean_news.extend(get_naver_news())  # 네이버 뉴스 수집
        korean_news.extend(get_nate_news())   # 네이트 뉴스 수집
        korean_news = korean_news[:5]         # 상위 5개 뉴스만 사용
        logger.info(f"한국 뉴스 {len(korean_news)}개 수집 완료")
        
        # 세계 뉴스 수집: 구글 월드 뉴스 수집
        world_news = get_google_world_news()
        logger.info(f"세계 뉴스 {len(world_news)}개 수집 완료")
        
        # 미국 뉴스 수집: 뉴저지와 뉴욕 핫뉴스 수집
        us_news = []
        us_news.extend(get_nj_hot_news())  # 뉴저지 뉴스 수집
        us_news.extend(get_ny_hot_news())  # 뉴욕 뉴스 수집
        logger.info(f"미국 뉴스 {len(us_news)}개 수집 완료")
        
        # 2. 텔레그램으로 뉴스 전송 준비
        current_time = datetime.now().strftime("%Y년 %m월 %d일 %H시 %M분")  # 현재 시간 문자열 생성
        # 헤더 메시지에 포함된 괄호를 MarkdownV2 형식에 맞게 이스케이프 처리
        escaped_time_for_header = escape_markdown_v2(f"({current_time})")

        # --- 애플 뉴스 전송 처리 ---
        apple_message = f"📱 애플 뉴스 업데이트 {escaped_time_for_header}\n\n"
        seen_titles = set()  # 중복 뉴스 제목을 걸러내기 위한 집합
        filtered_apple_news = []
        for article in apple_news:
            if article['title'] not in seen_titles:
                seen_titles.add(article['title'])
                filtered_apple_news.append(article)
        logger.info(f"전송될 애플 뉴스: {len(filtered_apple_news)}개")
        
        # 각 뉴스 기사에 대해 요약 생성 및 메시지 작성
        for article in filtered_apple_news:
            summary = summarize_article(article['content'])  # 기사 내용을 요약하는 함수 호출
            # 제목, 요약, URL을 MarkdownV2 형식에 맞게 이스케이프 처리
            escaped_title = escape_markdown_v2(article['title'])
            escaped_summary = escape_markdown_v2(summary)
            escaped_url = escape_markdown_v2(article['url'])
            # 메시지에 뉴스 제목, 요약, URL 추가
            apple_message += f"📌 *{escaped_title}*\n\n"
            apple_message += f"📝 {escaped_summary}\n\n"
            apple_message += f"🔗 {escaped_url}\n\n"
        await send_telegram_message(apple_message)  # 텔레그램으로 메시지 전송
        
        # --- 한국 뉴스 전송 처리 ---
        korean_message = f"🇰🇷 한국 뉴스 업데이트 {escaped_time_for_header}\n\n"
        seen_titles = set()  # 중복 뉴스 제거용 집합 초기화
        filtered_korean_news = []
        for article in korean_news:
            if article['title'] not in seen_titles:
                seen_titles.add(article['title'])
                filtered_korean_news.append(article)
        logger.info(f"전송될 한국 뉴스: {len(filtered_korean_news)}개")

        # 각 뉴스 기사 요약 및 메시지 구성
        for article in filtered_korean_news:
            summary = summarize_article(article['content'])  # 기사 요약
            escaped_title = escape_markdown_v2(article['title'])  # 제목 이스케이프
            escaped_summary = escape_markdown_v2(summary)         # 요약 이스케이프
            escaped_url = escape_markdown_v2(article['url'])      # URL 이스케이프
            korean_message += f"📌 *{escaped_title}*\n\n"
            korean_message += f"📝 {escaped_summary}\n\n"
            korean_message += f"🔗 {escaped_url}\n\n"
        await send_telegram_message(korean_message)  # 텔레그램으로 한국 뉴스 전송
        
        # --- 세계 뉴스 전송 처리 ---
        world_message = f"🌍 세계 핫뉴스 업데이트 {escaped_time_for_header}\n\n"
        seen_titles = set()  # 중복 뉴스 제거용 집합 초기화
        filtered_world_news = []
        for article in world_news:
            if article['title'] not in seen_titles:
                seen_titles.add(article['title'])
                filtered_world_news.append(article)
        logger.info(f"전송될 세계 뉴스: {len(filtered_world_news)}개")

        # 각 세계 뉴스 기사 요약 및 메시지 구성
        for article in filtered_world_news:
            summary = summarize_article(article['content'])  # 기사 요약
            escaped_title = escape_markdown_v2(article['title'])  # 제목 이스케이프
            escaped_summary = escape_markdown_v2(summary)         # 요약 이스케이프
            escaped_url = escape_markdown_v2(article['url'])      # URL 이스케이프
            world_message += f"📌 *{escaped_title}*\n\n"
            world_message += f"📝 {escaped_summary}\n\n"
            world_message += f"🔗 {escaped_url}\n\n"
        await send_telegram_message(world_message)  # 텔레그램으로 세계 뉴스 전송
        
        # --- 미국 뉴스 전송 처리 ---
        us_message = f"🇺🇸 미국 뉴스 업데이트 {escaped_time_for_header}\n\n"
        seen_titles = set()  # 중복 뉴스 제거용 집합 초기화
        filtered_us_news = []
        for article in us_news:
            if article['title'] not in seen_titles:
                seen_titles.add(article['title'])
                filtered_us_news.append(article)
        logger.info(f"전송될 미국 뉴스: {len(filtered_us_news)}개")

        # 각 미국 뉴스 기사 요약 및 메시지 구성
        for article in filtered_us_news:
            summary = summarize_article(article['content'])  # 기사 요약
            escaped_title = escape_markdown_v2(article['title'])  # 제목 이스케이프
            escaped_summary = escape_markdown_v2(summary)         # 요약 이스케이프
            escaped_url = escape_markdown_v2(article['url'])      # URL 이스케이프
            us_message += f"📌 *{escaped_title}*\n\n"
            us_message += f"📝 {escaped_summary}\n\n"
            us_message += f"🔗 {escaped_url}\n\n"
        await send_telegram_message(us_message)  # 텔레그램으로 미국 뉴스 전송
        
        logger.info("모든 뉴스 전송 완료!")  # 모든 뉴스 전송 완료 로그 출력
        
    except Exception as e:
        # 실행 중 예외 발생 시 에러 로그 출력
        logger.error(f"오류 발생: {e}")

if __name__ == "__main__":
    # 비동기 main 함수 실행
    asyncio.run(main())