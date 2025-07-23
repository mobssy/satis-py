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
        logging.FileHandler('news_bot.log'),  # 로그를 파일에 저장
        logging.StreamHandler()               # 로그를 콘솔에도 출력
    ]
)

def job():
    """실행할 작업"""
    try:
        logging.info("뉴스 수집 및 전송 작업 시작")  # 작업 시작 로그 기록
        import asyncio
        asyncio.run(main())  # 비동기 함수를 올바르게 호출
        logging.info("작업 완료")  # 작업 완료 로그 기록
    except Exception as e:
        logging.error(f"작업 중 오류 발생: {e}")  # 예외 발생 시 오류 로그 기록

def run_scheduler():
    """스케줄러 실행"""
    # EST 시간대 설정 (pytz는 다양한 시간대를 다룰 수 있게 해줌)
    est = pytz.timezone('US/Eastern')
    
    # 매일 오전 11시 EST 기준으로 job() 함수를 실행하도록 예약
    # schedule 라이브러리는 기본적으로 시스템 시간 기준이지만, 여기서는 주석으로 시간대 명시
    schedule.every().day.at("11:00").do(job)
    
    logging.info("스케줄러가 시작되었습니다.")
    # 한국 시간으로 변환하여 다음 실행 예정 시간 표시
    logging.info(f"다음 실행 예정 시간: 매일 오전 11시 EST (한국 시간 {datetime.now(pytz.timezone('Asia/Seoul')).strftime('%H:%M')})")
    
    while True:
        try:
            schedule.run_pending()  # 예약된 작업이 있으면 실행
            time.sleep(60)  # 1분마다 예약 작업 확인 (sleep은 CPU 사용량을 줄이기 위함)
        except Exception as e:
            logging.error(f"스케줄러 실행 중 오류 발생: {e}")  # 오류 발생 시 로그 기록
            time.sleep(300)  # 오류 발생 시 5분 대기 후 재시도

if __name__ == "__main__":
    run_scheduler()