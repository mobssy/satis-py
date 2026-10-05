import unittest
from unittest.mock import MagicMock, patch

from korean_news_scraper import get_google_korea_news, get_nate_news, get_naver_news
from news_categories import CATEGORIES

_NATE_HOME = """
<div class="mlt01">
  <a class="lt1" href="//news.nate.com/view/20261005n07088">
    <span class="tb">
      <h2 class="tit">농지 전수조사 관련 발언</h2>
      <span class="medium">한국경제<em>2026-10-05</em></span>
    </span>
  </a>
</div>
"""

_NATE_ARTICLE = '<div id="realArtcContents">네이트 기사 본문입니다.</div>'

_NAVER_HOME = """
<div class="cjs_nf_list _item_list">
  <a class="cjs_nf_a _item" href="https://n.news.naver.com/article/666/0000126086">
    <div class="cn_title_area">
      <h4 class="cn_title">네이버 속보 제목</h4>
      <div class="cn_snippet"><div class="cn_name">경기일보</div></div>
    </div>
  </a>
</div>
"""

_NAVER_ARTICLE = '<article id="dic_area">네이버 기사 본문입니다.<span class="end_photo_org">사진</span></article>'


def _fake_site(pages: dict[str, str]):
    def fake_request(url, *args, **kwargs):
        html = pages.get(url)
        return MagicMock(text=html) if html is not None else None
    return fake_request


class NateNewsTest(unittest.TestCase):
    @patch("korean_news_scraper.safe_request")
    def test_resolves_protocol_relative_links_and_reads_body(self, mock_request):
        mock_request.side_effect = _fake_site({
            "https://news.nate.com/": _NATE_HOME,
            "https://news.nate.com/view/20261005n07088": _NATE_ARTICLE,
        })

        articles = get_nate_news()

        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0]["url"], "https://news.nate.com/view/20261005n07088")
        self.assertEqual(articles[0]["content"], "네이트 기사 본문입니다.")

    @patch("korean_news_scraper.safe_request")
    def test_title_excludes_outlet_and_date(self, mock_request):
        mock_request.side_effect = _fake_site({
            "https://news.nate.com/": _NATE_HOME,
            "https://news.nate.com/view/20261005n07088": _NATE_ARTICLE,
        })

        articles = get_nate_news()

        self.assertEqual(articles[0]["title"], "농지 전수조사 관련 발언")


class NaverNewsTest(unittest.TestCase):
    @patch("korean_news_scraper.safe_request")
    def test_parses_newsflash_items_where_item_is_the_link(self, mock_request):
        mock_request.side_effect = _fake_site({
            "https://news.naver.com/": _NAVER_HOME,
            "https://n.news.naver.com/article/666/0000126086": _NAVER_ARTICLE,
        })

        articles = get_naver_news()

        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0]["title"], "네이버 속보 제목")
        self.assertEqual(articles[0]["url"], "https://n.news.naver.com/article/666/0000126086")
        self.assertEqual(articles[0]["content"], "네이버 기사 본문입니다.")

    @patch("korean_news_scraper.safe_request", return_value=None)
    def test_returns_empty_list_when_homepage_fails(self, _mock_request):
        self.assertEqual(get_naver_news(), [])


class GoogleKoreaNewsTest(unittest.TestCase):
    @patch("korean_news_scraper.fetch_google_rss_news", return_value=[])
    def test_requests_korean_top_stories_without_label_prefix(self, mock_fetch):
        get_google_korea_news()

        args, kwargs = mock_fetch.call_args
        self.assertIsNone(args[0])
        self.assertEqual(kwargs["locale"].ceid, "KR:ko")
        self.assertEqual(kwargs["title_formatter"]("제목 - 한겨레"), "제목 - 한겨레")


class KoreanCategoryTest(unittest.TestCase):
    def test_google_korea_is_the_last_fallback_source(self):
        korean = next(c for c in CATEGORIES if c.name == "한국")

        self.assertEqual(
            [s.fetch.__name__ for s in korean.sources],
            ["get_naver_news", "get_nate_news", "get_google_korea_news"],
        )


if __name__ == "__main__":
    unittest.main()
