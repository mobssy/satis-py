import openai
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def summarize_article(text):
    prompt = (
        "다음 뉴스 기사를 한국어로 간결하게 요약해줘. (최대 10문장, 반드시 한글로 답변해줘)\n\n"
        f"{text}\n\n"
        "요약:"
    )
    
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "너는 뉴스 요약 전문가야. 반드시 한글로만 답변해."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )
        summary = response.choices[0].message.content.strip()
        return summary
    except Exception as e:
        print(f"[요약 실패] {e}")
        return "요약 중 오류가 발생했습니다."