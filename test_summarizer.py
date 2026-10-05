import json
import unittest
from unittest.mock import MagicMock, patch

import summarizer
from summarizer import (
    BatchSummary,
    SummarizationError,
    fallback_summary,
    parse_batch_response,
    summarize_articles,
)


class _QuotaError(Exception):
    code = "credit_balance_exhausted"


def _response(items: list[dict]) -> str:
    return json.dumps({"items": items}, ensure_ascii=False)


class ParseBatchResponseTest(unittest.TestCase):
    def test_orders_items_by_index(self):
        raw = _response([
            {"index": 1, "summary": "둘째", "duplicate_of": None},
            {"index": 0, "summary": " 첫째 ", "duplicate_of": None},
        ])

        result = parse_batch_response(raw, 2)

        self.assertEqual(result, BatchSummary(["첫째", "둘째"], [None, None]))

    def test_keeps_valid_duplicate_reference(self):
        raw = _response([
            {"index": 0, "summary": "a", "duplicate_of": None},
            {"index": 1, "summary": "b", "duplicate_of": 0},
        ])

        self.assertEqual(parse_batch_response(raw, 2).duplicate_of, [None, 0])

    def test_ignores_self_forward_and_chained_duplicate_references(self):
        raw = _response([
            {"index": 0, "summary": "a", "duplicate_of": None},
            {"index": 1, "summary": "b", "duplicate_of": 0},
            {"index": 2, "summary": "c", "duplicate_of": 1},
            {"index": 3, "summary": "d", "duplicate_of": 3},
            {"index": 4, "summary": "e", "duplicate_of": 9},
            {"index": 5, "summary": "f", "duplicate_of": True},
        ])

        self.assertEqual(parse_batch_response(raw, 6).duplicate_of, [None, 0, None, None, None, None])

    def test_rejects_invalid_json(self):
        with self.assertRaises(SummarizationError) as ctx:
            parse_batch_response("not json", 1)
        self.assertEqual(ctx.exception.reason, "invalid_response")

    def test_rejects_empty_response(self):
        with self.assertRaises(SummarizationError) as ctx:
            parse_batch_response(None, 1)
        self.assertEqual(ctx.exception.reason, "empty_response")

    def test_rejects_missing_item(self):
        raw = _response([{"index": 0, "summary": "a", "duplicate_of": None}])

        with self.assertRaises(SummarizationError):
            parse_batch_response(raw, 2)

    def test_rejects_empty_summary(self):
        raw = _response([{"index": 0, "summary": "  ", "duplicate_of": None}])

        with self.assertRaises(SummarizationError):
            parse_batch_response(raw, 1)


class SummarizeArticlesTest(unittest.TestCase):
    @patch.object(summarizer, "_client")
    def test_summarizes_all_articles_in_one_request(self, mock_client):
        choice = MagicMock()
        choice.message.content = _response([
            {"index": 0, "summary": "요약0", "duplicate_of": None},
            {"index": 1, "summary": "요약1", "duplicate_of": None},
        ])
        mock_client.chat.completions.create.return_value = MagicMock(choices=[choice])
        articles = [
            {"title": "제목0", "content": "본" * 5000},
            {"title": "제목1", "content": None},
        ]

        result = summarize_articles(articles)

        self.assertEqual(result.summaries, ["요약0", "요약1"])
        mock_client.chat.completions.create.assert_called_once()
        prompt = mock_client.chat.completions.create.call_args.kwargs["messages"][1]["content"]
        self.assertIn("[0] 제목: 제목0", prompt)
        self.assertIn("[1] 제목: 제목1\n내용: (없음)", prompt)
        self.assertNotIn("본" * (summarizer._MAX_BODY_CHARS + 1), prompt)

    @patch.object(summarizer, "_client")
    def test_skips_api_call_for_empty_input(self, mock_client):
        self.assertEqual(summarize_articles([]), BatchSummary([], []))
        mock_client.chat.completions.create.assert_not_called()

    @patch.object(summarizer, "_client")
    def test_raises_with_api_error_code_as_reason(self, mock_client):
        mock_client.chat.completions.create.side_effect = _QuotaError("429")

        with self.assertRaises(SummarizationError) as ctx:
            summarize_articles([{"title": "t", "content": "c"}])

        self.assertEqual(ctx.exception.reason, "credit_balance_exhausted")

    @patch.object(summarizer, "_client")
    def test_falls_back_to_exception_name_without_code(self, mock_client):
        mock_client.chat.completions.create.side_effect = TimeoutError()

        with self.assertRaises(SummarizationError) as ctx:
            summarize_articles([{"title": "t", "content": "c"}])

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
