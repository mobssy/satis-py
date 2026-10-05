import unittest
from unittest.mock import MagicMock

from health_report import HealthReport
from news_categories import NewsCategory, NewsSource, collect_unseen_articles


def _articles(*urls: str) -> list[dict]:
    return [{"title": url, "url": url} for url in urls]


def _filter_out(*seen_urls: str):
    return lambda articles: [a for a in articles if a["url"] not in seen_urls]


class CollectUnseenArticlesTest(unittest.TestCase):
    def test_filters_seen_articles_before_applying_limit(self):
        source = NewsSource(lambda: _articles("a", "b", "c", "d"), limit=2)
        category = NewsCategory("테스트", "📰", (source,), limit=2)

        result = collect_unseen_articles(category, _filter_out("a", "b"))

        self.assertEqual([a["url"] for a in result], ["c", "d"])

    def test_applies_per_source_limit(self):
        first = NewsSource(lambda: _articles("a1", "a2", "a3"), limit=1)
        second = NewsSource(lambda: _articles("b1", "b2"), limit=2)
        category = NewsCategory("테스트", "📰", (first, second), limit=10)

        result = collect_unseen_articles(category, _filter_out())

        self.assertEqual([a["url"] for a in result], ["a1", "b1", "b2"])

    def test_skips_remaining_sources_once_category_limit_reached(self):
        backup_fetch = MagicMock(return_value=_articles("b1"))
        first = NewsSource(lambda: _articles("a1", "a2"), limit=5)
        category = NewsCategory("테스트", "📰", (first, NewsSource(backup_fetch, 5)), limit=2)

        result = collect_unseen_articles(category, _filter_out())

        self.assertEqual([a["url"] for a in result], ["a1", "a2"])
        backup_fetch.assert_not_called()

    def test_falls_back_to_next_source_when_first_is_exhausted(self):
        first = NewsSource(lambda: _articles("a1", "a2"), limit=5)
        second = NewsSource(lambda: _articles("b1", "b2"), limit=5)
        category = NewsCategory("테스트", "📰", (first, second), limit=3)

        result = collect_unseen_articles(category, _filter_out("a1"))

        self.assertEqual([a["url"] for a in result], ["a2", "b1", "b2"])

    def test_failing_source_does_not_block_others(self):
        def broken():
            raise RuntimeError("boom")

        category = NewsCategory(
            "테스트", "📰",
            (NewsSource(broken, 5), NewsSource(lambda: _articles("b1"), 5)),
            limit=5,
        )

        result = collect_unseen_articles(category, _filter_out())

        self.assertEqual([a["url"] for a in result], ["b1"])

    def test_reports_empty_and_failing_sources(self):
        def get_empty_news():
            return []

        def get_broken_news():
            raise RuntimeError("boom")

        category = NewsCategory(
            "테스트", "📰",
            (NewsSource(get_empty_news, 5), NewsSource(get_broken_news, 5)),
            limit=5,
        )
        report = HealthReport()

        collect_unseen_articles(category, _filter_out(), report)

        self.assertEqual(report.warnings, [
            "테스트/get_empty_news: 기사 0개",
            "테스트/get_broken_news: 오류 - boom",
        ])

    def test_reports_on_fetched_candidates_not_unseen_subset(self):
        source = NewsSource(lambda: [{"title": "a", "url": "a", "content": "본문"}], 5)
        category = NewsCategory("테스트", "📰", (source,), limit=5)
        report = HealthReport()

        collect_unseen_articles(category, _filter_out("a"), report)

        self.assertEqual(report.warnings, [])


if __name__ == "__main__":
    unittest.main()
