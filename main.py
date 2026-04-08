import asyncio
import logging
from datetime import datetime
from zoneinfo import ZoneInfo
from news_scraper import fetch_9to5mac_news, fetch_macrumors_news
from korean_news_scraper import get_naver_news, get_nate_news, get_google_world_news
from us_news_scraper import get_nj_hot_news, get_ny_hot_news
from bigtech_news_scraper import get_bigtech_news
from telegram_sender import send_telegram_message
from summarizer import summarize_article

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('news_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

_NUMBER_EMOJIS = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']

def _format_kst_time() -> str:
    """KST 기준 현재 시간을 오전/오후 형식으로 반환"""
    kst = datetime.now(ZoneInfo('Asia/Seoul'))
    period = "오전" if kst.hour < 12 else "오후"
    hour = kst.hour % 12 or 12
    return kst.strftime(f"%Y.%m.%d ") + f"{period} {hour}:{kst.minute:02d}"

def is_tuesday() -> bool:
    """오늘이 화요일(EST 기준)인지 확인"""
    return datetime.now(ZoneInfo('US/Eastern')).weekday() == 1

async def send_news_safely(message: str, news_type: str) -> None:
    """뉴스 전송을 안전하게 처리하는 함수"""
    try:
        if message:
            await send_telegram_message(message)
            logger.info(f"{news_type} 뉴스 전송 완료")
        else:
            logger.warning(f"{news_type} 뉴스 메시지가 비어있습니다.")
    except Exception as e:
        logger.error(f"{news_type} 뉴스 전송 중 오류 발생: {e}")

def create_news_message(news_list: list, news_type: str, emoji: str) -> str | None:
    """뉴스 메시지를 새 포맷으로 생성"""
    if not news_list:
        return None

    try:
        seen_titles = set()
        filtered_news = []
        for article in news_list:
            if article['title'] not in seen_titles:
                seen_titles.add(article['title'])
                filtered_news.append(article)

        logger.info(f"전송될 {news_type} 뉴스: {len(filtered_news)}개")

        lines = [f"📰 {emoji} {news_type} 뉴스 브리핑\n"]

        for i, article in enumerate(filtered_news):
            try:
                number_emoji = _NUMBER_EMOJIS[i] if i < len(_NUMBER_EMOJIS) else f"{i + 1}."
                summary = summarize_article(article['content'])
                lines.append(f"{number_emoji} {article['title']}")
                lines.append(f"→ {summary}\n")
            except Exception as e:
                logger.error(f"{news_type} 뉴스 기사 처리 중 오류 발생: {e}")
                continue

        lines.append(f"🕐 {_format_kst_time()}")
        return "\n".join(lines)

    except Exception as e:
        logger.error(f"{news_type} 뉴스 메시지 생성 중 오류 발생: {e}")
        return None

async def main():
    try:
        logger.info("뉴스 수집 시작...")

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

        korean_news = []
        try:
            korean_news.extend(get_naver_news())
            korean_news.extend(get_nate_news())
            korean_news = korean_news[:5]
            logger.info(f"한국 뉴스 {len(korean_news)}개 수집 완료")
        except Exception as e:
            logger.error(f"한국 뉴스 수집 중 오류 발생: {e}")

        world_news = []
        try:
            world_news = get_google_world_news()
            logger.info(f"세계 뉴스 {len(world_news)}개 수집 완료")
        except Exception as e:
            logger.error(f"세계 뉴스 수집 중 오류 발생: {e}")

        us_news = []
        try:
            us_news.extend(get_nj_hot_news())
            us_news.extend(get_ny_hot_news())
            logger.info(f"미국 뉴스 {len(us_news)}개 수집 완료")
        except Exception as e:
            logger.error(f"미국 뉴스 수집 중 오류 발생: {e}")

        bigtech_news = []
        try:
            bigtech_news = get_bigtech_news()
            logger.info(f"빅테크 뉴스 {len(bigtech_news)}개 수집 완료")
        except Exception as e:
            logger.error(f"빅테크 뉴스 수집 중 오류 발생: {e}")

        news_configs = [
            (apple_news, "애플", "📱"),
            (korean_news, "한국", "🇰🇷"),
            (world_news, "세계", "🌍"),
            (us_news, "미국", "🇺🇸"),
            (bigtech_news, "빅테크", "🏢"),
        ]

        for news_list, news_type, emoji in news_configs:
            if news_list:
                message = create_news_message(news_list, news_type, emoji)
                await send_news_safely(message, news_type)

        logger.info("모든 뉴스 전송 완료!")

    except Exception as e:
        logger.error(f"프로그램 실행 중 오류 발생: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
