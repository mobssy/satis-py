import openai
from config import OPENAI_API_KEY
import logging
from typing import Optional

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

openai.api_key = OPENAI_API_KEY

def summarize_article(text: str) -> str:
    """
    주어진 뉴스 기사 텍스트를 한국어로 간결하게 요약하는 함수입니다.
    OpenAI의 GPT-3.5 Turbo 모델을 사용하여 요약을 생성합니다.
    """
    # 요약을 요청하기 위한 프롬프트를 만듭니다.
    # 프롬프트는 모델에게 무엇을 해야 하는지 지시하는 문장입니다.
    # 여기서는 뉴스 기사를 최대 10문장으로 한국어로 요약해달라는 요청을 포함합니다.
    prompt = (
        "다음 뉴스 기사를 한국어로 간결하게 요약해줘. (최대 10문장, 반드시 한글로 답변해줘)\n\n"
        f"{text}\n\n"
        "요약:"
    )
    
    try:
        # OpenAI의 chat completions API를 호출하여 요약을 생성합니다.
        # model: 사용할 언어 모델을 지정합니다. 여기서는 'gpt-3.5-turbo'를 사용합니다.
        # messages: 대화 형식으로 모델에 전달할 메시지 리스트입니다.
        #           system 역할은 모델에게 역할과 행동 지침을 주고,
        #           user 역할은 실제 요약 요청 내용을 담습니다.
        # max_tokens: 생성할 최대 토큰 수를 지정합니다. 토큰은 문장 부호, 단어 단위 등으로 분할된 텍스트 단위입니다.
        #             이 값을 높이면 더 긴 답변을 받을 수 있습니다.
        # temperature: 생성되는 텍스트의 창의성 정도를 조절하는 값입니다.
        #              0에 가까울수록 더 결정적이고 일관된 답변을 생성하며,
        #              1에 가까울수록 다양하고 창의적인 답변을 생성합니다.
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "너는 뉴스 요약 전문가야. 반드시 한글로만 답변해."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500, # 최대 500 토큰까지 답변을 생성하도록 설정
            temperature=0.7 # 적당한 창의성을 가진 답변 생성
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