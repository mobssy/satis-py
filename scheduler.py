import schedule
import time
from datetime import datetime
import pytz
from main import main
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('news_bot.log'),
        logging.StreamHandler()
    ]
)

def job():
    """실행할 작업"""
    try:
        logging.info("뉴스 수집 및 전송 작업 시작")
        main()
        logging.info("작업 완료")
    except Exception as e:
        logging.error(f"작업 중 오류 발생: {e}")

def run_scheduler():
    """스케줄러 실행"""
    # EST 시간대 설정
    est = pytz.timezone('US/Eastern')
    
    # 매일 오전 11시 EST에 실행
    schedule.every().day.at("11:00").do(job)
    
    logging.info("스케줄러가 시작되었습니다.")
    logging.info(f"다음 실행 예정 시간: 매일 오전 11시 EST (한국 시간 {datetime.now(pytz.timezone('Asia/Seoul')).strftime('%H:%M')})")
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # 1분마다 체크
        except Exception as e:
            logging.error(f"스케줄러 실행 중 오류 발생: {e}")
            time.sleep(300)  # 오류 발생 시 5분 대기 후 재시도

if __name__ == "__main__":
    run_scheduler() 