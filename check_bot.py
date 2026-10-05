import asyncio
from telegram import Bot
from config import TELEGRAM_BOT_TOKEN


async def test_bot() -> None:
    """텔레그램 봇 연결 확인 및 Chat ID 조회용 진단 스크립트"""
    try:
        print("봇 테스트 시작...")
        bot = Bot(token=TELEGRAM_BOT_TOKEN)

        bot_info = await bot.get_me()
        print(f"봇 이름: {bot_info.first_name}")
        print(f"봇 사용자명: @{bot_info.username}")

        updates = await bot.get_updates()
        if updates:
            print("\n최근 대화 내역:")
            for update in updates:
                if update.message:
                    print(f"Chat ID: {update.message.chat_id}")
                    print(f"메시지: {update.message.text}")
        else:
            print("\n최근 대화 내역이 없습니다. 봇에 /start를 보내주세요.")

    except Exception as e:
        print(f"에러 발생: {e}")


if __name__ == "__main__":
    asyncio.run(test_bot())
