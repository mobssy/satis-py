from telegram.ext import Application
from config import TELEGRAM_BOT_TOKEN
import asyncio

async def test_bot():
    try:
        print("🤖 봇 테스트 시작...")
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        
        # 봇 정보 가져오기
        bot = await application.bot.get_me()
        print(f"봇 이름: {bot.first_name}")
        print(f"봇 사용자명: @{bot.username}")
        
        # 최근 업데이트 가져오기
        updates = await application.bot.get_updates()
        if updates:
            print("\n최근 대화 내역:")
            for update in updates:
                if update.message:
                    print(f"Chat ID: {update.message.chat_id}")
                    print(f"메시지: {update.message.text}")
        else:
            print("\n❌ 최근 대화 내역이 없습니다.")
            print("텔레그램에서 봇을 찾아 /start 명령어를 보내주세요!")
            
    except Exception as e:
        print(f"❌ 에러 발생: {e}")

if __name__ == "__main__":
    asyncio.run(test_bot()) 