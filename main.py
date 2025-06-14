import schedule
import time
import asyncio
import logging
from datetime import datetime
from news_scraper import fetch_9to5mac_news, fetch_macrumors_news
from korean_news_scraper import get_naver_news, get_nate_news
from us_news_scraper import get_nj_hot_news, get_ny_hot_news
from telegram_sender import send_telegram_message

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

async def main():
    try:
        # 1. 뉴스 수집
        logger.info("뉴스 수집 시작...")
        
        # 9to5mac과 MacRumors 뉴스 수집
        apple_news = []
        apple_news.extend(fetch_9to5mac_news())
        apple_news.extend(fetch_macrumors_news())
        logger.info(f"애플 뉴스 {len(apple_news)}개 수집 완료")
        
        # 한국 뉴스 수집
        korean_news = []
        korean_news.extend(get_naver_news())
        korean_news.extend(get_nate_news())
        logger.info(f"한국 뉴스 {len(korean_news)}개 수집 완료")
        
        # 미국 뉴스 수집
        us_news = []
        us_news.extend(get_nj_hot_news())
        us_news.extend(get_ny_hot_news())
        logger.info(f"미국 뉴스 {len(us_news)}개 수집 완료")
        
        # 2. 텔레그램으로 전송
        current_time = datetime.now().strftime("%Y년 %m월 %d일 %H시 %M분")
        
        # 애플 뉴스 전송
        apple_message = f"📱 애플 뉴스 업데이트 ({current_time})\n\n"
        for article in apple_news:
            apple_message += f"📌 {article['title']}\n"
            apple_message += f"📝 {article['content']}\n"
            apple_message += f"🔗 {article['url']}\n\n"
        await send_telegram_message(apple_message)
        
        # 한국 뉴스 전송
        korean_message = f"🇰🇷 한국 뉴스 업데이트 ({current_time})\n\n"
        for article in korean_news:
            korean_message += f"📌 {article['title']}\n"
            korean_message += f"📝 {article['content']}\n"
            korean_message += f"🔗 {article['url']}\n\n"
        await send_telegram_message(korean_message)
        
        # 미국 뉴스 전송
        us_message = f"🇺🇸 미국 뉴스 업데이트 ({current_time})\n\n"
        for article in us_news:
            us_message += f"📌 {article['title']}\n"
            us_message += f"📝 {article['content']}\n"
            us_message += f"🔗 {article['url']}\n\n"
        await send_telegram_message(us_message)
        
        logger.info("모든 뉴스 전송 완료!")
        
    except Exception as e:
        logger.error(f"오류 발생: {e}")

if __name__ == "__main__":
    def job():
        asyncio.run(main())

    schedule.every().day.at("11:00").do(job)
    logger.info("뉴스 봇 스케줄 시작됨 - 매일 오전 11시")

    while True:
        schedule.run_pending()
        time.sleep(60)