from telegram.ext import Application
from config import TELEGRAM_BOT_TOKEN
import asyncio

async def test_bot():
    try:
        print("🤖 봇 테스트 시작...")

        # 텔레그램 봇 애플리케이션을 생성합니다.
        # Application.builder()는 새로운 봇 애플리케이션을 만들기 위한 빌더 객체를 반환합니다.
        # token(TELEGRAM_BOT_TOKEN)은 봇의 인증 토큰을 설정하는 메서드로, 이 토큰을 통해 텔레그램 서버와 통신합니다.
        # build()는 설정된 빌더를 바탕으로 실제 Application 객체를 생성합니다.
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        
        # 봇 자신의 정보를 가져옵니다.
        # get_me() 메서드는 봇의 사용자명, 이름 등 기본 정보를 비동기적으로 받아옵니다.
        bot = await application.bot.get_me()
        print(f"봇 이름: {bot.first_name}")
        print(f"봇 사용자명: @{bot.username}")
        
        # 봇으로 들어온 최근 업데이트(메시지 등)를 가져옵니다.
        # get_updates()는 봇이 받은 최신 메시지나 명령어 등의 업데이트 목록을 비동기적으로 반환합니다.
        updates = await application.bot.get_updates()
        if updates:
            print("\n최근 대화 내역:")
            for update in updates:
                if update.message:
                    # 각 메시지의 채팅 ID와 텍스트 내용을 출력합니다.
                    print(f"Chat ID: {update.message.chat_id}")
                    print(f"메시지: {update.message.text}")
        else:
            # 업데이트가 없으면 안내 메시지를 출력합니다.
            print("\n❌ 최근 대화 내역이 없습니다.")
            print("텔레그램에서 봇을 찾아 /start 명령어를 보내주세요!")
            
    except Exception as e:
        # 코드 실행 중 에러가 발생하면 에러 메시지를 출력합니다.
        # 예외 처리를 통해 프로그램이 갑자기 종료되지 않고 적절한 안내를 할 수 있습니다.
        print(f"❌ 에러 발생: {e}")

# 이 파일이 직접 실행될 때만 아래 코드가 실행됩니다.
# asyncio.run()은 비동기 함수인 test_bot()을 실행시키기 위한 함수로,
# 비동기 루프를 생성하고 실행을 관리합니다.
if __name__ == "__main__":
    asyncio.run(test_bot()) 