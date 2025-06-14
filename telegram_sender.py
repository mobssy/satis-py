import os
os.environ["TZ"] = "Asia/Seoul"
from telegram import Bot
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
import asyncio
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# 텔레그램 메시지 최대 길이 (4096자)
MAX_MESSAGE_LENGTH = 4096

async def send_telegram_message(message):
    """텔레그램으로 메시지 전송"""
    try:
        logger.info("📨 Telegram 메시지 전송 중...")
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        
        # 메시지가 최대 길이를 초과하는 경우 분할
        if len(message) > MAX_MESSAGE_LENGTH:
            # 메시지를 최대 길이로 분할
            parts = []
            current_part = ""
            
            # 줄 단위로 분할
            for line in message.split('\n'):
                if len(current_part) + len(line) + 1 <= MAX_MESSAGE_LENGTH:
                    current_part += line + '\n'
                else:
                    parts.append(current_part)
                    current_part = line + '\n'
            
            if current_part:
                parts.append(current_part)
            
            # 각 부분을 순차적으로 전송
            for i, part in enumerate(parts, 1):
                if len(parts) > 1:
                    part = f"[{i}/{len(parts)}]\n\n{part}"
                await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=part)
                await asyncio.sleep(1)  # 메시지 간 딜레이
        else:
            await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        
        logger.info("✅ 메시지 전송 완료!")
        
    except Exception as e:
        logger.error(f"❌ Telegram 전송 실패: {e}")

async def test_bot():
    """텔레그램 봇 테스트"""
    try:
        logger.info("🤖 봇 테스트 시작...")
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        
        # 봇 정보 가져오기
        bot_info = await bot.get_me()
        logger.info(f"봇 이름: {bot_info.first_name}")
        logger.info(f"봇 사용자명: @{bot_info.username}")
        
        # 최근 업데이트 가져오기
        updates = await bot.get_updates()
        if updates:
            logger.info("\n최근 대화 내역:")
            for update in updates:
                if update.message:
                    logger.info(f"Chat ID: {update.message.chat_id}")
                    logger.info(f"메시지: {update.message.text}")
        else:
            logger.info("\n❌ 최근 대화 내역이 없습니다.")
            logger.info("텔레그램에서 봇을 찾아 /start 명령어를 보내주세요!")
            
    except Exception as e:
        logger.error(f"❌ 에러 발생: {e}")

if __name__ == "__main__":
    asyncio.run(test_bot())