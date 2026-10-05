from typing import NotRequired, TypedDict


class Article(TypedDict):
    """스크래퍼가 반환하고 파이프라인 전체(필터 → 요약 → 전송 → 이력)가 주고받는 기사"""
    title: str
    url: str
    content: str | None  # 본문을 못 가져오면 None
    source: NotRequired[str]
