import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Callable
from zoneinfo import ZoneInfo

from news_scraper import fetch_9to5mac_news, fetch_macrumors_news
from korean_news_scraper import get_naver_news, get_nate_news, get_google_world_news
from us_news_scraper import get_nj_hot_news, get_ny_hot_news
from bigtech_news_scraper import get_bigtech_news

logger = logging.getLogger(__name__)

Article = dict
ArticleFilter = Callable[[list[Article]], list[Article]]


@dataclass(frozen=True)
class NewsSource:
    fetch: Callable[[], list[Article]]
    limit: int


@dataclass(frozen=True)
class NewsCategory:
    name: str
    emoji: str
    sources: tuple[NewsSource, ...]
    limit: int
    is_active: Callable[[], bool] = lambda: True


def is_tuesday() -> bool:
    """오늘이 화요일(뉴욕 시간 기준)인지 확인"""
    return datetime.now(ZoneInfo('America/New_York')).weekday() == 1


def collect_unseen_articles(category: NewsCategory, filter_unseen: ArticleFilter) -> list[Article]:
    """카테고리의 소스들에서 아직 보내지 않은 기사를 limit만큼 수집

    이미 보낸 기사를 먼저 걸러낸 뒤 개수를 자르므로, 상위 기사가 겹쳐도
    다음 순위 기사로 채워진다. limit이 차면 남은 소스는 호출하지 않는다.
    """
    collected: list[Article] = []
    for source in category.sources:
        if len(collected) >= category.limit:
            break
        try:
            candidates = source.fetch()
        except Exception as e:
            logger.error(f"{category.name} 뉴스 소스 수집 중 오류 발생: {e}")
            continue

        unseen = filter_unseen(candidates)
        skipped = len(candidates) - len(unseen)
        if skipped:
            logger.info(f"{category.name}: 최근에 이미 보낸 기사 {skipped}개 제외")
        collected.extend(unseen[:source.limit])

    return collected[:category.limit]


CATEGORIES: tuple[NewsCategory, ...] = (
    NewsCategory(
        name="애플",
        emoji="📱",
        sources=(NewsSource(fetch_9to5mac_news, 3), NewsSource(fetch_macrumors_news, 2)),
        limit=5,
        is_active=is_tuesday,
    ),
    NewsCategory(
        name="한국",
        emoji="🇰🇷",
        sources=(NewsSource(get_naver_news, 5), NewsSource(get_nate_news, 5)),
        limit=5,
    ),
    NewsCategory(
        name="세계",
        emoji="🌍",
        sources=(NewsSource(get_google_world_news, 5),),
        limit=5,
    ),
    NewsCategory(
        name="미국",
        emoji="🇺🇸",
        sources=(NewsSource(get_nj_hot_news, 5), NewsSource(get_ny_hot_news, 5)),
        limit=10,
    ),
    NewsCategory(
        name="빅테크",
        emoji="🏢",
        sources=(NewsSource(get_bigtech_news, 5),),
        limit=5,
    ),
)
