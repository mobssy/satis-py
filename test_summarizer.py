import unittest
from unittest.mock import MagicMock, patch

import summarizer
from summarizer import SummarizationError, fallback_summary, summarize_article


class _QuotaError(Exception):
    code = "credit_balance_exhausted"


class SummarizeArticleTest(unittest.TestCase):
    @patch.object(summarizer, "_client")
    def test_returns_stripped_summary(self, mock_client):
        choice = MagicMock()
        choice.message.content = "  한 줄 요약입니다.  "
        mock_client.chat.completions.create.return_value = MagicMock(choices=[choice])

        self.assertEqual(summarize_article("본문"), "한 줄 요약입니다.")

    @patch.object(summarizer, "_client")
    def test_raises_with_api_error_code_as_reason(self, mock_client):
        mock_client.chat.completions.create.side_effect = _QuotaError("429")

        with self.assertRaises(SummarizationError) as ctx:
            summarize_article("본문")

        self.assertEqual(ctx.exception.reason, "credit_balance_exhausted")

    @patch.object(summarizer, "_client")
    def test_falls_back_to_exception_name_without_code(self, mock_client):
        mock_client.chat.completions.create.side_effect = TimeoutError()

        with self.assertRaises(SummarizationError) as ctx:
            summarize_article("본문")

        self.assertEqual(ctx.exception.reason, "TimeoutError")


class FallbackSummaryTest(unittest.TestCase):
    def test_collapses_whitespace(self):
        self.assertEqual(fallback_summary("a\n\n  b\tc"), "a b c")

    def test_truncates_long_text_with_ellipsis(self):
        self.assertEqual(fallback_summary("x" * 200, max_length=10), "x" * 10 + "...")

    def test_keeps_text_at_exact_limit_without_ellipsis(self):
        self.assertEqual(fallback_summary("x" * 10, max_length=10), "x" * 10)


if __name__ == "__main__":
    unittest.main()
