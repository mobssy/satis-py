import unittest
from unittest.mock import patch

from health_report import HealthReport
from main import create_news_message
from summarizer import SummarizationError


class CreateNewsMessageTest(unittest.TestCase):
    @patch("main.summarize_article", return_value="요약된 내용입니다.")
    def test_includes_article_url(self, _mock_summarize):
        articles = [{"title": "헤드라인", "content": "본문", "url": "https://example.com/article"}]

        message = create_news_message(articles, "테스트", "📰")

        self.assertIn('<a href="https://example.com/article">헤드라인</a>', message)

    @patch("main.summarize_article", return_value="요약된 내용입니다.")
    def test_omits_link_line_when_url_missing(self, _mock_summarize):
        articles = [{"title": "헤드라인", "content": "본문"}]

        message = create_news_message(articles, "테스트", "📰")

        self.assertNotIn("<a ", message)
        self.assertIn("헤드라인", message)

    @patch("main.summarize_article", return_value="요약된 내용입니다.")
    def test_summarizes_title_when_body_missing(self, mock_summarize):
        articles = [{"title": "헤드라인", "content": None, "url": "https://example.com/a"}]

        create_news_message(articles, "테스트", "📰")

        mock_summarize.assert_called_once_with("헤드라인")

    @patch("main.summarize_article", return_value="A < B & C")
    def test_escapes_html_in_title_url_and_summary(self, _mock_summarize):
        articles = [{"title": "<script>&", "content": "본문", "url": 'https://e.com/?a=1&b="2"'}]

        message = create_news_message(articles, "테스트", "📰")

        self.assertIn('<a href="https://e.com/?a=1&amp;b=&quot;2&quot;">&lt;script&gt;&amp;</a>', message)
        self.assertIn("→ A &lt; B &amp; C", message)

    @patch("main.summarize_article", side_effect=SummarizationError("credit_balance_exhausted"))
    def test_uses_fallback_and_reports_when_summary_fails(self, _mock_summarize):
        articles = [{"title": "헤드라인", "content": "본문   첫 줄", "url": "https://example.com/a"}]
        report = HealthReport()

        message = create_news_message(articles, "테스트", "📰", report)

        self.assertIn("→ 본문 첫 줄", message)
        self.assertIn("요약 실패 1/1건 (credit_balance_exhausted)", report.format_alert())

    @patch("main.summarize_article", return_value="요약된 내용입니다.")
    def test_reports_successful_summaries(self, _mock_summarize):
        articles = [{"title": "헤드라인", "content": "본문"}]
        report = HealthReport()

        create_news_message(articles, "테스트", "📰", report)

        self.assertEqual(report.summaries_total, 1)
        self.assertIsNone(report.format_alert())


if __name__ == "__main__":
    unittest.main()
