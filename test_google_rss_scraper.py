import unittest
from unittest.mock import MagicMock, patch

from google_rss_scraper import KOREA_KOREAN, US_ENGLISH, _build_url, fetch_google_rss_news

_RSS = b"""<?xml version="1.0" encoding="UTF-8"?>
<rss><channel>
  <item>
    <title>Headline One</title>
    <link>https://news.google.com/articles/1</link>
    <description>&lt;a href="https://example.com/1"&gt;Headline One&lt;/a&gt;&amp;nbsp;&amp;nbsp;&lt;font color="#6f6f6f"&gt;Example Times&lt;/font&gt;</description>
  </item>
  <item>
    <title>Missing description</title>
    <link>https://news.google.com/articles/2</link>
  </item>
</channel></rss>"""


class FetchGoogleRssNewsTest(unittest.TestCase):
    @patch("google_rss_scraper.fetch_with_retry")
    def test_parses_items_and_strips_html_from_description(self, mock_fetch):
        mock_fetch.return_value = MagicMock(content=_RSS)

        result = fetch_google_rss_news("query", "테스트")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["title"], "[테스트] Headline One")
        self.assertEqual(result[0]["url"], "https://news.google.com/articles/1")
        self.assertNotIn("<", result[0]["content"])
        self.assertIn("Example Times", result[0]["content"])

    @patch("google_rss_scraper.fetch_with_retry", return_value=None)
    def test_returns_empty_list_when_request_fails(self, _mock_fetch):
        self.assertEqual(fetch_google_rss_news("query", "테스트"), [])


class BuildUrlTest(unittest.TestCase):
    def test_search_url_for_query(self):
        self.assertEqual(
            _build_url("new+york", US_ENGLISH),
            "https://news.google.com/rss/search?q=new+york&hl=en-US&gl=US&ceid=US:en",
        )

    def test_top_stories_url_without_query(self):
        self.assertEqual(
            _build_url(None, KOREA_KOREAN),
            "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko",
        )


if __name__ == "__main__":
    unittest.main()
