import asyncio
import logging
from telegram import Bot
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

logger = logging.getLogger(__name__)

MAX_MESSAGE_LENGTH = 4096
# 파트 접두사 "[nn/nn]\n\n" 공간을 미리 확보해 분할 후 한도 초과를 방지
_PART_PREFIX_RESERVE = 16

_bot = Bot(token=TELEGRAM_BOT_TOKEN)


def _split_message(message: str, limit: int) -> list[str]:
    """메시지를 limit자 이하의 파트로 분할"""
    parts = []
    current_part = ""

    for line in message.split('\n'):
        while len(line) > limit:
            if current_part:
                parts.append(current_part)
                current_part = ""
            parts.append(line[:limit])
            line = line[limit:]

        if len(current_part) + len(line) + 1 > limit:
            parts.append(current_part)
            current_part = ""

        current_part += line + '\n'

    if current_part.strip():
        parts.append(current_part)

    return parts


async def send_telegram_message(message: str) -> None:
    """텔레그램으로 메시지 전송. 실패 시 예외를 호출자에게 전파한다."""
    logger.info("Telegram 메시지 전송 중...")

    if len(message) <= MAX_MESSAGE_LENGTH:
        await _bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode=None)
        logger.info("메시지 전송 완료")
        return

    parts = _split_message(message, MAX_MESSAGE_LENGTH - _PART_PREFIX_RESERVE)
    for i, part in enumerate(parts, 1):
        text = f"[{i}/{len(parts)}]\n\n{part}" if len(parts) > 1 else part
        await _bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=text, parse_mode=None)
        await asyncio.sleep(1)

    logger.info(f"메시지 전송 완료 ({len(parts)}파트)")
