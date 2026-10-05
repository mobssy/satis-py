import asyncio
import logging
from telegram import Bot, LinkPreviewOptions
from telegram.constants import ParseMode
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from message_splitter import split_message, visible_length

logger = logging.getLogger(__name__)

MAX_MESSAGE_LENGTH = 4096
# 파트 접두사 "[nn/nn]\n\n" 공간을 미리 확보해 분할 후 한도 초과를 방지
_PART_PREFIX_RESERVE = 16

_bot = Bot(token=TELEGRAM_BOT_TOKEN)
_NO_PREVIEW = LinkPreviewOptions(is_disabled=True)


async def _send(text: str) -> None:
    await _bot.send_message(
        chat_id=TELEGRAM_CHAT_ID,
        text=text,
        parse_mode=ParseMode.HTML,
        link_preview_options=_NO_PREVIEW,
    )


async def send_telegram_message(message: str) -> None:
    """텔레그램으로 HTML 메시지 전송. 실패 시 예외를 호출자에게 전파한다.

    링크 URL은 길이 제한에 포함되지 않으므로 보이는 글자 수로 분할 여부를 판단한다.
    분할할 때는 원문 길이 기준으로 잘라 각 파트가 확실히 제한 안에 들도록 한다.
    """
    logger.info("Telegram 메시지 전송 중...")

    if visible_length(message) <= MAX_MESSAGE_LENGTH:
        await _send(message)
        logger.info("메시지 전송 완료")
        return

    parts = split_message(message, MAX_MESSAGE_LENGTH - _PART_PREFIX_RESERVE)
    for i, part in enumerate(parts, 1):
        text = f"[{i}/{len(parts)}]\n\n{part}" if len(parts) > 1 else part
        await _send(text)
        await asyncio.sleep(1)

    logger.info(f"메시지 전송 완료 ({len(parts)}파트)")
