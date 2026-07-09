import logging
import openai
from config import OPENAI_API_KEY

logger = logging.getLogger(__name__)

_client = openai.OpenAI(api_key=OPENAI_API_KEY)


def summarize_article(text: str) -> str:
    """뉴스 기사를 한국어 한 문장으로 요약"""
    prompt = (
        "다음 뉴스 기사를 한국어로 한 문장으로만 요약해줘. "
        "반드시 한 문장, 한글로만 답변해. 앞에 '요약:' 같은 접두사 없이 바로 내용만 써줘.\n\n"
        f"{text}"
    )

    try:
        response = _client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "너는 뉴스 요약 전문가야. 반드시 한 문장, 한글로만 답변해."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=100,
            temperature=0.5,
        )
        summary = response.choices[0].message.content.strip()
        logger.info("기사 요약 성공")
        return summary
    except Exception as e:
        logger.error(f"[요약 실패] {e}")
        fallback = " ".join(text.split())[:150]
        return f"{fallback}..." if len(fallback) == 150 else fallback
