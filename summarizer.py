import openai
from config import OPENAI_API_KEY
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

openai.api_key = OPENAI_API_KEY

def summarize_article(text):
    """
    주어진 뉴스 기사 텍스트를 한국어로 간결하게 요약하는 함수입니다.
    OpenAI의 GPT-3.5 Turbo 모델을 사용하여 요약을 생성합니다.
    """
    # 요약을 요청하기 위한 프롬프트를 만듭니다.
    # 프롬프트는 모델에게 무엇을 해야 하는지 지시하는 문장입니다.
    # 여기서는 뉴스 기사를 최대 10문장으로 한국어로 요약해달라는 요청을 포함합니다.
    prompt = (
        "다음 뉴스 기사를 한국어로 한 문장으로만 요약해줘. "
        "반드시 한 문장, 한글로만 답변해. 앞에 '요약:' 같은 접두사 없이 바로 내용만 써줘.\n\n"
        f"{text}"
    )

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "너는 뉴스 요약 전문가야. 반드시 한 문장, 한글로만 답변해."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.5,
        )
        # API 응답에서 생성된 요약 텍스트를 추출하고 앞뒤 공백을 제거합니다.
        summary = response.choices[0].message.content.strip()
        # 요약이 성공적으로 생성되었음을 로그에 기록합니다.
        logger.info("기사 요약 성공")
        # 생성된 요약을 반환합니다.
        return summary
    except Exception as e:
        # 요약 생성 중 오류가 발생하면 오류 내용을 로그에 기록합니다.
        logger.error(f"[요약 실패] {e}")
        # 사용자에게 기본 오류 메시지를 반환합니다.
        return "요약 중 오류가 발생했습니다."