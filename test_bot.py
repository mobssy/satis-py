import asyncio
from telegram.ext import Application
from config import TELEGRAM_BOT_TOKEN


async def test_bot() -> None:
    try:
        print("봇 테스트 시작...")
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

        bot = await application.bot.get_me()
        print(f"봇 이름: {bot.first_name}")
        print(f"봇 사용자명: @{bot.username}")

        updates = await application.bot.get_updates()
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
