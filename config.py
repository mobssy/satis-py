# config.py
import os
from pathlib import Path

# .env 파일 로드
def load_env():
    """현재 디렉토리의 .env 파일을 로드합니다."""
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

# .env 파일 로드
load_env()

# Telegram Bot 설정 - 환경변수에서 가져오기
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# OpenAI API Key - 환경변수에서 가져오기
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# 필수 환경변수 확인
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN 환경변수가 설정되지 않았습니다.")
if not TELEGRAM_CHAT_ID:
    raise ValueError("TELEGRAM_CHAT_ID 환경변수가 설정되지 않았습니다.")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")