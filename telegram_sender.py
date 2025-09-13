import os
os.environ["TZ"] = "Asia/Seoul"
from telegram import Bot
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
import asyncio
import logging
from typing import List

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# 텔레그램 메시지 최대 길이 (4096자)
MAX_MESSAGE_LENGTH = 4096

async def send_telegram_message(message: str) -> None:
    """텔레그램으로 메시지 전송"""
    try:
        logger.info("📨 Telegram 메시지 전송 중...")
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        
        # 텔레그램 메시지는 최대 4096자까지 보낼 수 있습니다.
        # 만약 메시지가 이 길이를 초과하면 여러 개로 나누어 보내야 합니다.
        if len(message) > MAX_MESSAGE_LENGTH:
            # 메시지를 여러 부분으로 나누기 위해 리스트를 만듭니다.
            parts = []
            current_part = ""
            
            # 메시지를 줄 단위로 나누는 이유:
            # 줄 단위로 나누면 메시지의 가독성을 유지할 수 있고,
            # 중간에 단어가 잘리거나 내용이 어색하게 끊기지 않도록 할 수 있습니다.
            for line in message.split('\n'):
                # 현재 부분에 이 줄을 추가해도 최대 길이 이내라면 추가합니다.
                if len(current_part) + len(line) + 1 <= MAX_MESSAGE_LENGTH:
                    current_part += line + '\n'
                else:
                    # 현재 부분이 꽉 찼으면 리스트에 추가하고 새 부분을 시작합니다.
                    parts.append(current_part)
                    current_part = line + '\n'
            
            # 마지막 부분이 남아 있으면 리스트에 추가합니다.
            if current_part:
                parts.append(current_part)
            
            # 나누어진 각 부분을 순서대로 전송합니다.
            for i, part in enumerate(parts, 1):
                # 만약 메시지가 여러 부분이라면, 각 부분 앞에 [몇 번째/전체] 표시를 붙여서
                # 받는 사람이 메시지 순서를 쉽게 알 수 있도록 합니다.
                if len(parts) > 1:
                    part = f"[{i}/{len(parts)}]\n\n{part}"
                # parse_mode='MarkdownV2'는 메시지에 마크다운 형식을 적용하기 위한 설정입니다.
                # 이를 통해 텔레그램에서 텍스트를 굵게, 기울임꼴 등으로 꾸밀 수 있습니다.
                await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=part, parse_mode='MarkdownV2')
                # 메시지를 연속해서 너무 빠르게 보내면 텔레그램 서버가 차단할 수 있으므로,
                # 1초씩 잠시 쉬면서 메시지를 보냅니다.
                await asyncio.sleep(1)  # 메시지 간 딜레이
        else:
            # 메시지가 최대 길이 이내라면 바로 전송합니다.
            await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode='MarkdownV2')
        
        logger.info("✅ 메시지 전송 완료!")
        
    except Exception as e:
        logger.error(f"❌ Telegram 전송 실패: {e}")

async def test_bot() -> None:
    """텔레그램 봇 테스트"""
    try:
        logger.info("🤖 봇 테스트 시작...")
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        
        # 봇 정보 가져오기:
        # 봇의 이름과 사용자명을 확인하여 봇이 정상적으로 동작하는지 확인합니다.
        bot_info = await bot.get_me()
        logger.info(f"봇 이름: {bot_info.first_name}")
        logger.info(f"봇 사용자명: @{bot_info.username}")
        
        # 최근 업데이트(대화 내역) 가져오기:
        # 봇이 실제로 메시지를 받고 있는지 확인하기 위해 최근 대화 내역을 조회합니다.
        updates = await bot.get_updates()
        if updates:
            logger.info("\n최근 대화 내역:")
            for update in updates:
                if update.message:
                    # 각 메시지의 채팅 ID와 텍스트 내용을 출력하여
                    # 봇이 어떤 메시지를 받았는지 알 수 있습니다.
                    logger.info(f"Chat ID: {update.message.chat_id}")
                    logger.info(f"메시지: {update.message.text}")
        else:
            # 최근 대화 내역이 없으면 봇이 메시지를 받지 못한 상태이므로,
            # 사용자에게 봇에게 /start 명령어를 보내도록 안내합니다.
            logger.info("\n❌ 최근 대화 내역이 없습니다.")
            logger.info("텔레그램에서 봇을 찾아 /start 명령어를 보내주세요!")
            
    except Exception as e:
        logger.error(f"❌ 에러 발생: {e}")

if __name__ == "__main__":
    asyncio.run(test_bot())