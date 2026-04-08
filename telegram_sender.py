import logging
from telegram import Bot
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
import asyncio

logger = logging.getLogger(__name__)

MAX_MESSAGE_LENGTH = 4096

def _split_message(message: str) -> list[str]:
    """메시지를 4096자 이하의 파트로 분할"""
    parts = []
    current_part = ""

    for line in message.split('\n'):
        # 단일 줄이 최대 길이를 초과하면 문자 단위로 분할
        if len(line) + 1 > MAX_MESSAGE_LENGTH:
            if current_part:
                parts.append(current_part)
                current_part = ""
            for i in range(0, len(line), MAX_MESSAGE_LENGTH - 1):
                parts.append(line[i:i + MAX_MESSAGE_LENGTH - 1] + '\n')
        elif len(current_part) + len(line) + 1 <= MAX_MESSAGE_LENGTH:
            current_part += line + '\n'
        else:
            parts.append(current_part)
            current_part = line + '\n'

    if current_part:
        parts.append(current_part)

    return parts

async def send_telegram_message(message: str) -> None:
    """텔레그램으로 메시지 전송"""
    try:
        logger.info("Telegram 메시지 전송 중...")
        bot = Bot(token=TELEGRAM_BOT_TOKEN)

        if len(message) <= MAX_MESSAGE_LENGTH:
            await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode=None)
            logger.info("메시지 전송 완료")
            return

        parts = _split_message(message)
        for i, part in enumerate(parts, 1):
            text = f"[{i}/{len(parts)}]\n\n{part}" if len(parts) > 1 else part
            await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=text, parse_mode=None)
            await asyncio.sleep(1)

        logger.info(f"메시지 전송 완료 ({len(parts)}파트)")

    except Exception as e:
        logger.error(f"Telegram 전송 실패: {e}")

async def test_bot() -> None:
    """텔레그램 봇 연결 테스트"""
    try:
        logger.info("봇 테스트 시작...")
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        bot_info = await bot.get_me()
        logger.info(f"봇 이름: {bot_info.first_name} (@{bot_info.username})")

        updates = await bot.get_updates()
        if updates:
            for update in updates:
                if update.message:
                    logger.info(f"Chat ID: {update.message.chat_id}")
        else:
            logger.info("대화 내역 없음. 봇에 /start를 보내주세요.")

    except Exception as e:
        logger.error(f"봇 테스트 실패: {e}")

if __name__ == "__main__":
    asyncio.run(test_bot())
