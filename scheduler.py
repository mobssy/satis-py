import schedule
import time
import asyncio
import logging
from main import main

logger = logging.getLogger(__name__)

def job():
    """실행할 작업"""
    try:
        logger.info("뉴스 수집 및 전송 작업 시작")
        asyncio.run(main())
        logger.info("작업 완료")
    except Exception as e:
        logger.error(f"작업 중 오류 발생: {e}")

def run_scheduler():
    """스케줄러 실행 (시스템 시간 기준 매일 11:00 EST)"""
    schedule.every().day.at("12:00").do(job)
    logger.info("스케줄러 시작: 매일 12:00 뉴욕 시간 실행")

    while True:
        try:
            schedule.run_pending()
            time.sleep(60)
        except Exception as e:
            logger.error(f"스케줄러 실행 중 오류 발생: {e}")
            time.sleep(300)

if __name__ == "__main__":
    run_scheduler()
