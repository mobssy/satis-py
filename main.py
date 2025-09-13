import asyncio
import logging
from datetime import datetime
import pytz
from typing import List, Dict, Optional
from news_scraper import fetch_9to5mac_news, fetch_macrumors_news, fetch_9to5mac_news_async, fetch_macrumors_news_async
from korean_news_scraper import get_naver_news, get_nate_news, get_google_world_news
from us_news_scraper import get_nj_hot_news, get_ny_hot_news
from bigtech_news_scraper import get_bigtech_news
from telegram_sender import send_telegram_message
from summarizer import summarize_article


class Logger:
    @staticmethod
    def setup() -> logging.Logger:
        logging.basicConfig(
            level=logging.INFO,
            format='[%(asctime)s] %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            handlers=[
                logging.FileHandler('news_bot.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)


class TimeManager:
    @staticmethod
    def get_current_time() -> datetime:
        try:
            est = pytz.timezone('US/Eastern')
            return datetime.now(est)
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"시간대 변환 중 오류 발생: {e}")
            return datetime.now()
    
    @staticmethod
    def is_tuesday() -> bool:
        current_time = TimeManager.get_current_time()
        return current_time.weekday() == 1


class MessageFormatter:
    @staticmethod
    def escape_markdown_v2(text: Optional[str]) -> str:
        if not text:
            return ""
        escape_chars = '_*[]()~`>#+-=|{}.!'
        escaped_text = ""
        for char in text:
            if char in escape_chars:
                escaped_text += '\\' + char
            else:
                escaped_text += char
        return escaped_text
    
    @staticmethod
    def create_news_message(news_list: List[Dict[str, str]], news_type: str, emoji: str, escaped_time_for_header: str) -> Optional[str]:
        if not news_list:
            return None
        
        logger = logging.getLogger(__name__)
        try:
            message = f"{emoji} {news_type} 뉴스 업데이트 {escaped_time_for_header}\n\n"
            seen_titles = set()
            filtered_news = []
            
            for article in news_list:
                if article['title'] not in seen_titles:
                    seen_titles.add(article['title'])
                    filtered_news.append(article)
            
            logger.info(f"전송될 {news_type} 뉴스: {len(filtered_news)}개")
            
            for article in filtered_news:
                try:
                    summary = summarize_article(article['content'])
                    escaped_title = MessageFormatter.escape_markdown_v2(article['title'])
                    escaped_summary = MessageFormatter.escape_markdown_v2(summary)
                    escaped_url = MessageFormatter.escape_markdown_v2(article['url'])
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


class NewsCollector:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def collect_apple_news(self) -> List[Dict[str, str]]:
        apple_news = []
        if TimeManager.is_tuesday():
            try:
                # 병렬 애플 뉴스 수집
                mac9to5_task = fetch_9to5mac_news_async()
                macrumors_task = fetch_macrumors_news_async()
                
                results = await asyncio.gather(mac9to5_task, macrumors_task, return_exceptions=True)
                
                if not isinstance(results[0], Exception):
                    apple_news.extend(results[0][:3])
                if not isinstance(results[1], Exception):
                    apple_news.extend(results[1][:2])
                    
                self.logger.info(f"애플 뉴스 {len(apple_news)}개 수집 완료")
            except Exception as e:
                self.logger.error(f"애플 뉴스 수집 중 오류 발생: {e}")
        else:
            self.logger.info("오늘은 화요일이 아니므로 애플 뉴스를 보내지 않습니다.")
        return apple_news
    
    async def collect_korean_news(self) -> List[Dict[str, str]]:
        korean_news = []
        try:
            korean_news.extend(get_naver_news())
            korean_news.extend(get_nate_news())
            korean_news = korean_news[:5]
            self.logger.info(f"한국 뉴스 {len(korean_news)}개 수집 완료")
        except Exception as e:
            self.logger.error(f"한국 뉴스 수집 중 오류 발생: {e}")
        return korean_news
    
    async def collect_world_news(self) -> List[Dict[str, str]]:
        world_news = []
        try:
            world_news = get_google_world_news()
            self.logger.info(f"세계 뉴스 {len(world_news)}개 수집 완료")
        except Exception as e:
            self.logger.error(f"세계 뉴스 수집 중 오류 발생: {e}")
        return world_news
    
    async def collect_us_news(self) -> List[Dict[str, str]]:
        us_news = []
        try:
            us_news.extend(get_nj_hot_news())
            us_news.extend(get_ny_hot_news())
            self.logger.info(f"미국 뉴스 {len(us_news)}개 수집 완료")
        except Exception as e:
            self.logger.error(f"미국 뉴스 수집 중 오류 발생: {e}")
        return us_news
    
    async def collect_bigtech_news(self) -> List[Dict[str, str]]:
        bigtech_news = []
        try:
            bigtech_news = get_bigtech_news()
            self.logger.info(f"빅테크 뉴스 {len(bigtech_news)}개 수집 완료")
        except Exception as e:
            self.logger.error(f"빅테크 뉴스 수집 중 오류 발생: {e}")
        return bigtech_news


class NewsDistributor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def send_news_safely(self, message: Optional[str], news_type: str) -> None:
        try:
            if message:
                await send_telegram_message(message)
                self.logger.info(f"{news_type} 뉴스 전송 완료")
            else:
                self.logger.warning(f"{news_type} 뉴스 메시지가 비어있습니다.")
        except Exception as e:
            self.logger.error(f"{news_type} 뉴스 전송 중 오류 발생: {e}")
    
    async def distribute_news(self, news_data: Dict[str, List[Dict[str, str]]]) -> None:
        current_time = TimeManager.get_current_time().strftime("%Y년 %m월 %d일 %H시 %M분")
        escaped_time_for_header = MessageFormatter.escape_markdown_v2(f"({current_time})")
        
        news_configs = [
            (news_data['apple'], "애플", "📱"),
            (news_data['korean'], "한국", "🇰🇷"),
            (news_data['world'], "세계", "🌍"),
            (news_data['us'], "미국", "🇺🇸"),
            (news_data['bigtech'], "빅테크", "🏢")
        ]
        
        for news_list, news_type, emoji in news_configs:
            if news_list:
                message = MessageFormatter.create_news_message(
                    news_list, news_type, emoji, escaped_time_for_header
                )
                await self.send_news_safely(message, news_type)


class NewsOrchestrator:
    def __init__(self):
        self.logger = Logger.setup()
        self.collector = NewsCollector()
        self.distributor = NewsDistributor()
    
    async def run(self) -> None:
        try:
            self.logger.info("뉴스 수집 시작...")
            
            # 병렬 뉴스 수집으로 성능 개선
            apple_task = self.collector.collect_apple_news()
            korean_task = self.collector.collect_korean_news()
            world_task = self.collector.collect_world_news()
            us_task = self.collector.collect_us_news()
            bigtech_task = self.collector.collect_bigtech_news()
            
            # 모든 뉴스 수집 작업을 동시에 실행
            results = await asyncio.gather(
                apple_task,
                korean_task,
                world_task,
                us_task,
                bigtech_task,
                return_exceptions=True
            )
            
            # 결과 정리 (예외 발생시 빈 리스트 반환)
            news_data = {
                'apple': results[0] if not isinstance(results[0], Exception) else [],
                'korean': results[1] if not isinstance(results[1], Exception) else [],
                'world': results[2] if not isinstance(results[2], Exception) else [],
                'us': results[3] if not isinstance(results[3], Exception) else [],
                'bigtech': results[4] if not isinstance(results[4], Exception) else []
            }
            
            # 예외 로깅
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    news_types = ['apple', 'korean', 'world', 'us', 'bigtech']
                    self.logger.error(f"{news_types[i]} 뉴스 수집 중 오류: {result}")
            
            await self.distributor.distribute_news(news_data)
            
            self.logger.info("모든 뉴스 전송 완료!")
            
        except Exception as e:
            self.logger.error(f"프로그램 실행 중 오류 발생: {e}")
            raise


logger = logging.getLogger(__name__)

async def main() -> None:
    orchestrator = NewsOrchestrator()
    await orchestrator.run()

if __name__ == "__main__":
    asyncio.run(main())