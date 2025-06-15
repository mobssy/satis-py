import asyncio
import logging
from datetime import datetime
from news_scraper import fetch_9to5mac_news, fetch_macrumors_news
from korean_news_scraper import get_naver_news, get_nate_news, get_google_world_news
from us_news_scraper import get_nj_hot_news, get_ny_hot_news
from telegram_sender import send_telegram_message
from summarizer import summarize_article

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def escape_markdown_v2(text):
    """Telegram MarkdownV2에서 특수 문자를 이스케이프 처리합니다."""
    # 이스케이프해야 할 문자들
    escape_chars = '_*[]()~`>#+-=|{}.!'
    escaped_text = ""
    for char in text:
        if char in escape_chars:
            escaped_text += '\\' + char
        else:
            escaped_text += char
    return escaped_text

async def main():
    try:
        # 1. 뉴스 수집
        logger.info("뉴스 수집 시작...")
        
        # 9to5mac과 MacRumors 뉴스 수집 (5개로 제한)
        apple_news = []
        apple_news.extend(fetch_9to5mac_news()[:3])  # 9to5mac에서 3개
        apple_news.extend(fetch_macrumors_news()[:2])  # MacRumors에서 2개
        logger.info(f"애플 뉴스 {len(apple_news)}개 수집 완료")
        
        # 한국 뉴스 수집
        korean_news = []
        korean_news.extend(get_naver_news())
        korean_news.extend(get_nate_news())
        # 한국 뉴스 총 5개로 제한
        korean_news = korean_news[:5]
        logger.info(f"한국 뉴스 {len(korean_news)}개 수집 완료")
        
        # 세계 뉴스 수집
        world_news = get_google_world_news()
        logger.info(f"세계 뉴스 {len(world_news)}개 수집 완료")
        
        # 미국 뉴스 수집
        us_news = []
        us_news.extend(get_nj_hot_news())
        us_news.extend(get_ny_hot_news())
        logger.info(f"미국 뉴스 {len(us_news)}개 수집 완료")
        
        # 2. 텔레그램으로 전송
        current_time = datetime.now().strftime("%Y년 %m월 %d일 %H시 %M분")
        # 헤더 메시지에서 괄호를 포함한 시간 부분을 MarkdownV2 이스케이프 처리
        escaped_time_for_header = escape_markdown_v2(f"({current_time})")

        # 애플 뉴스 전송
        apple_message = f"📱 애플 뉴스 업데이트 {escaped_time_for_header}\n\n"
        seen_titles = set()
        filtered_apple_news = []
        for article in apple_news:
            if article['title'] not in seen_titles:
                seen_titles.add(article['title'])
                filtered_apple_news.append(article)
        logger.info(f"전송될 애플 뉴스: {len(filtered_apple_news)}개")
        
        for article in filtered_apple_news:
            summary = summarize_article(article['content'])
            escaped_title = escape_markdown_v2(article['title'])
            escaped_summary = escape_markdown_v2(summary)
            escaped_url = escape_markdown_v2(article['url'])
            apple_message += f"📌 *{escaped_title}*\n\n"
            apple_message += f"📝 {escaped_summary}\n\n"
            apple_message += f"🔗 {escaped_url}\n\n"
        await send_telegram_message(apple_message)
        
        # 한국 뉴스 전송
        korean_message = f"🇰🇷 한국 뉴스 업데이트 {escaped_time_for_header}\n\n"
        seen_titles = set()
        filtered_korean_news = []
        for article in korean_news:
            if article['title'] not in seen_titles:
                seen_titles.add(article['title'])
                filtered_korean_news.append(article)
        logger.info(f"전송될 한국 뉴스: {len(filtered_korean_news)}개")

        for article in filtered_korean_news:
            summary = summarize_article(article['content'])
            escaped_title = escape_markdown_v2(article['title'])
            escaped_summary = escape_markdown_v2(summary)
            escaped_url = escape_markdown_v2(article['url'])
            korean_message += f"📌 *{escaped_title}*\n\n"
            korean_message += f"📝 {escaped_summary}\n\n"
            korean_message += f"🔗 {escaped_url}\n\n"
        await send_telegram_message(korean_message)
        
        # 세계 뉴스 전송
        world_message = f"🌍 세계 핫뉴스 업데이트 {escaped_time_for_header}\n\n"
        seen_titles = set()
        filtered_world_news = []
        for article in world_news:
            if article['title'] not in seen_titles:
                seen_titles.add(article['title'])
                filtered_world_news.append(article)
        logger.info(f"전송될 세계 뉴스: {len(filtered_world_news)}개")

        for article in filtered_world_news:
            summary = summarize_article(article['content'])
            escaped_title = escape_markdown_v2(article['title'])
            escaped_summary = escape_markdown_v2(summary)
            escaped_url = escape_markdown_v2(article['url'])
            world_message += f"📌 *{escaped_title}*\n\n"
            world_message += f"📝 {escaped_summary}\n\n"
            world_message += f"🔗 {escaped_url}\n\n"
        await send_telegram_message(world_message)
        
        # 미국 뉴스 전송
        us_message = f"🇺🇸 미국 뉴스 업데이트 {escaped_time_for_header}\n\n"
        seen_titles = set()
        filtered_us_news = []
        for article in us_news:
            if article['title'] not in seen_titles:
                seen_titles.add(article['title'])
                filtered_us_news.append(article)
        logger.info(f"전송될 미국 뉴스: {len(filtered_us_news)}개")

        for article in filtered_us_news:
            summary = summarize_article(article['content'])
            escaped_title = escape_markdown_v2(article['title'])
            escaped_summary = escape_markdown_v2(summary)
            escaped_url = escape_markdown_v2(article['url'])
            us_message += f"📌 *{escaped_title}*\n\n"
            us_message += f"📝 {escaped_summary}\n\n"
            us_message += f"🔗 {escaped_url}\n\n"
        await send_telegram_message(us_message)
        
        logger.info("모든 뉴스 전송 완료!")
        
    except Exception as e:
        logger.error(f"오류 발생: {e}")

if __name__ == "__main__":
    asyncio.run(main())