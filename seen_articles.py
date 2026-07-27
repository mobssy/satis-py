import json
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

_STORE_PATH = Path(__file__).parent / "sent_history.json"
_RETENTION_DAYS = 7


def _load() -> dict[str, str]:
    if not _STORE_PATH.exists():
        return {}
    try:
        with _STORE_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        logger.error(f"전송 이력 파일 로드 실패: {e}")
        return {}


def _prune(history: dict[str, str]) -> dict[str, str]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=_RETENTION_DAYS)
    pruned = {}
    for url, sent_at in history.items():
        try:
            if datetime.fromisoformat(sent_at) >= cutoff:
                pruned[url] = sent_at
        except ValueError:
            continue
    return pruned


def _save(history: dict[str, str]) -> None:
    try:
        with _STORE_PATH.open("w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except OSError as e:
        logger.error(f"전송 이력 파일 저장 실패: {e}")


def filter_unseen(articles: list[dict]) -> list[dict]:
    """최근 전송 이력에 없는(=아직 안 보낸) 기사만 반환"""
    history = _load()
    return [a for a in articles if a.get('url') not in history]


def mark_as_sent(articles: list[dict]) -> None:
    """전송한 기사들의 URL을 이력에 기록하고 오래된 항목은 정리"""
    history = _prune(_load())
    now = datetime.now(timezone.utc).isoformat()
    for article in articles:
        url = article.get('url')
        if url:
            history[url] = now
    _save(history)
