import logging
import openai
from config import OPENAI_API_KEY

logger = logging.getLogger(__name__)

_client = openai.OpenAI(api_key=OPENAI_API_KEY)


class SummarizationError(Exception):
    """요약 API 호출 실패. reason에는 짧은 원인(예: credit_balance_exhausted)을 담는다."""

    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


def summarize_article(text: str) -> str:
    """뉴스 기사를 한국어 한 문장으로 요약. 실패하면 SummarizationError를 던진다."""
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
        raise SummarizationError(getattr(e, 'code', None) or type(e).__name__) from e


def fallback_summary(text: str, max_length: int = 150) -> str:
    """요약에 실패했을 때 쓰는 대체 문구: 본문 앞부분을 잘라 사용"""
    flattened = " ".join(text.split())
    return f"{flattened[:max_length]}..." if len(flattened) > max_length else flattened
