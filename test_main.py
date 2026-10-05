import unittest
from unittest.mock import patch

from health_report import HealthReport
from main import create_news_message
from summarizer import BatchSummary, SummarizationError


def _summaries(*texts: str, duplicate_of: list[int | None] | None = None):
    """summarize_articles 대역: 입력 기사 수와 상관없이 주어진 요약을 반환"""
    return lambda _articles: BatchSummary(list(texts), duplicate_of or [None] * len(texts))


class CreateNewsMessageTest(unittest.TestCase):
    @patch("main.summarize_articles", side_effect=_summaries("요약된 내용입니다."))
    def test_includes_article_url(self, _mock_summarize):
        articles = [{"title": "헤드라인", "content": "본문", "url": "https://example.com/article"}]

        message = create_news_message(articles, "테스트", "📰")

        self.assertIn('<a href="https://example.com/article">헤드라인</a>', message)

    @patch("main.summarize_articles", side_effect=_summaries("요약된 내용입니다."))
    def test_omits_link_line_when_url_missing(self, _mock_summarize):
        articles = [{"title": "헤드라인", "content": "본문"}]

        message = create_news_message(articles, "테스트", "📰")

        self.assertNotIn("<a ", message)
        self.assertIn("헤드라인", message)

    @patch("main.summarize_articles", side_effect=_summaries("A < B & C"))
    def test_escapes_html_in_title_url_and_summary(self, _mock_summarize):
        articles = [{"title": "<script>&", "content": "본문", "url": 'https://e.com/?a=1&b="2"'}]

        message = create_news_message(articles, "테스트", "📰")

        self.assertIn('<a href="https://e.com/?a=1&amp;b=&quot;2&quot;">&lt;script&gt;&amp;</a>', message)
        self.assertIn("→ A &lt; B &amp; C", message)

    @patch("main.summarize_articles", side_effect=_summaries("요약0", "요약1", "요약2", duplicate_of=[None, 0, None]))
    def test_drops_duplicate_story_and_renumbers(self, _mock_summarize):
        articles = [
            {"title": "사건 A", "content": "본문"},
            {"title": "사건 A 다른 언론사", "content": "본문"},
            {"title": "사건 B", "content": "본문"},
        ]

        message = create_news_message(articles, "테스트", "📰")

        self.assertNotIn("사건 A 다른 언론사", message)
        self.assertIn("1️⃣ 사건 A\n→ 요약0", message)
        self.assertIn("2️⃣ 사건 B\n→ 요약2", message)

    @patch("main.summarize_articles", side_effect=_summaries("요약된 내용입니다."))
    def test_summarizes_once_per_category(self, mock_summarize):
        articles = [{"title": "같은 제목", "content": "본문"}, {"title": "같은 제목", "content": "본문"}]

        create_news_message(articles, "테스트", "📰")

        mock_summarize.assert_called_once()
        self.assertEqual(len(mock_summarize.call_args.args[0]), 1)

    @patch("main.summarize_articles", side_effect=SummarizationError("credit_balance_exhausted"))
    def test_falls_back_per_article_and_reports_when_summary_fails(self, _mock_summarize):
        articles = [
            {"title": "헤드라인", "content": "본문   첫 줄", "url": "https://example.com/a"},
            {"title": "본문 없는 기사", "content": None},
        ]
        report = HealthReport()

        message = create_news_message(articles, "테스트", "📰", report)

        self.assertIn("→ 본문 첫 줄", message)
        self.assertIn("→ 본문 없는 기사", message)
        self.assertIn("요약 실패 2/2건 (credit_balance_exhausted)", report.format_alert())

    @patch("main.summarize_articles", side_effect=_summaries("요약0", "요약1"))
    def test_reports_successful_summaries(self, _mock_summarize):
        articles = [{"title": "a", "content": "본문"}, {"title": "b", "content": "본문"}]
        report = HealthReport()

        create_news_message(articles, "테스트", "📰", report)

        self.assertEqual(report.summaries_total, 2)
        self.assertIsNone(report.format_alert())


if __name__ == "__main__":
    unittest.main()
