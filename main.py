import asyncio
import logging
from html import escape
from news_categories import CATEGORIES, collect_unseen_articles
from telegram_sender import send_telegram_message
from summarizer import SummarizationError, fallback_summary, summarize_article
from seen_articles import filter_unseen, mark_as_sent
from health_report import HealthReport

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

_NUMBER_EMOJIS = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']

async def send_news_safely(message: str, news_type: str) -> bool:
    """뉴스 전송을 안전하게 처리하는 함수. 전송 성공 여부를 반환한다."""
    try:
        if message:
            await send_telegram_message(message)
            logger.info(f"{news_type} 뉴스 전송 완료")
            return True
        else:
            logger.warning(f"{news_type} 뉴스 메시지가 비어있습니다.")
            return False
    except Exception as e:
        logger.error(f"{news_type} 뉴스 전송 중 오류 발생: {e}")
        return False

def _format_title(article: dict) -> str:
    """제목에 기사 링크를 건다 (텔레그램 HTML 모드)"""
    title = escape(article['title'])
    url = article.get('url')
    return f'<a href="{escape(url, quote=True)}">{title}</a>' if url else title

def _summarize(text: str, report: HealthReport | None) -> str:
    """요약에 실패하면 본문 앞부분으로 대체하고, 결과를 report에 기록한다"""
    try:
        summary = summarize_article(text)
        failure_reason = None
    except SummarizationError as e:
        summary = fallback_summary(text)
        failure_reason = e.reason
    if report:
        report.record_summary(failure_reason)
    return summary

def create_news_message(
    news_list: list,
    news_type: str,
    emoji: str,
    report: HealthReport | None = None,
) -> str | None:
    """뉴스 메시지를 텔레그램 HTML 포맷으로 생성"""
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

        lines = [f"{emoji} 오늘의 뉴스 브리핑\n"]

        for i, article in enumerate(filtered_news):
            try:
                number_emoji = _NUMBER_EMOJIS[i] if i < len(_NUMBER_EMOJIS) else f"{i + 1}."
                # 본문을 못 가져온 기사는 제목을 대신 요약한다
                summary = _summarize(article.get('content') or article['title'], report)
                lines.append(f"{number_emoji} {_format_title(article)}")
                lines.append(f"→ {escape(summary)}")
                lines.append("")
            except Exception as e:
                logger.error(f"{news_type} 뉴스 기사 처리 중 오류 발생: {e}")
                continue

        return "\n".join(lines)

    except Exception as e:
        logger.error(f"{news_type} 뉴스 메시지 생성 중 오류 발생: {e}")
        return None

async def main():
    try:
        logger.info("뉴스 수집 시작...")
        report = HealthReport()

        for category in CATEGORIES:
            if not category.is_active():
                logger.info(f"{category.name}: 오늘은 전송 대상이 아니므로 건너뜁니다.")
                continue

            articles = collect_unseen_articles(category, filter_unseen, report)
            logger.info(f"{category.name} 뉴스 {len(articles)}개 수집 완료")
            if not articles:
                logger.info(f"{category.name}: 새로 보낼 기사가 없습니다.")
                continue

            message = create_news_message(articles, category.name, category.emoji, report)
            if await send_news_safely(message, category.name):
                mark_as_sent(articles)

        alert = report.format_alert()
        if alert:
            logger.warning(alert)
            await send_news_safely(alert, "점검 알림")

        logger.info("모든 뉴스 전송 완료!")

    except Exception as e:
        logger.error(f"프로그램 실행 중 오류 발생: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
