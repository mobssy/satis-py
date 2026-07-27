import unittest
from unittest.mock import patch

from main import create_news_message


class CreateNewsMessageTest(unittest.TestCase):
    @patch("main.summarize_article", return_value="요약된 내용입니다.")
    def test_includes_article_url(self, _mock_summarize):
        articles = [{"title": "헤드라인", "content": "본문", "url": "https://example.com/article"}]

        message = create_news_message(articles, "테스트", "📰")

        self.assertIn("🔗 https://example.com/article", message)

    @patch("main.summarize_article", return_value="요약된 내용입니다.")
    def test_omits_link_line_when_url_missing(self, _mock_summarize):
        articles = [{"title": "헤드라인", "content": "본문"}]

        message = create_news_message(articles, "테스트", "📰")

        self.assertNotIn("🔗", message)


if __name__ == "__main__":
    unittest.main()
