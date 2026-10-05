import unittest
from unittest.mock import MagicMock, patch

from news_scraper import fetch_9to5mac_news, fetch_macrumors_news

_9TO5_HOME = """
<article class="article feature feature-large">
  <h2><a href='"https://9to5mac.com/2026/10/01/feature-story/"'>Feature story</a></h2>
</article>
<article class="article feature sidebar">
  <h2><a href="https://9to5mac.com/2026/10/01/feature-story/">Feature story</a></h2>
</article>
<article class="article standard">
  <a href="https://9to5mac.com/guides/opinion/">Opinion</a>
  <h2 class="h1"><a href="/2026/10/04/standard-story/">Standard story</a></h2>
</article>
"""

_9TO5_ARTICLE = """
<article class="article feature"><h2>Unrelated related-story card</h2></article>
<div class="container med post-content">Real body.<div class="related-posts">noise</div></div>
"""

_MR_HOME = """
<article class="js-article"><h2><a href="https://www.macrumors.com/2026/10/04/story/">MR story</a></h2></article>
"""

_MR_ARTICLE = '<article><h1>MR story</h1><div class="js-content">MacRumors body.</div></article>'


def _fake_site(pages: dict[str, str]):
    def fake_request(url, *_args, **_kwargs):
        html = pages.get(url)
        return MagicMock(text=html) if html is not None else None
    return fake_request


class NineToFiveMacTest(unittest.TestCase):
    def setUp(self):
        patcher = patch("news_scraper.safe_request", side_effect=_fake_site({
            "https://9to5mac.com": _9TO5_HOME,
            "https://9to5mac.com/2026/10/01/feature-story/": _9TO5_ARTICLE,
            "https://9to5mac.com/2026/10/04/standard-story/": _9TO5_ARTICLE,
        }))
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_strips_quotes_from_href_and_dedupes_repeated_cards(self):
        urls = [a["url"] for a in fetch_9to5mac_news()]

        self.assertEqual(urls, [
            "https://9to5mac.com/2026/10/01/feature-story/",
            "https://9to5mac.com/2026/10/04/standard-story/",
        ])

    def test_uses_title_link_instead_of_first_tag_link(self):
        titles = [a["title"] for a in fetch_9to5mac_news()]

        self.assertIn("Standard story", titles)
        self.assertNotIn("Opinion", titles)

    def test_reads_post_body_not_first_article_card(self):
        contents = [a["content"] for a in fetch_9to5mac_news()]

        self.assertEqual(contents, ["Real body.", "Real body."])


class MacRumorsTest(unittest.TestCase):
    @patch("news_scraper.safe_request")
    def test_reads_js_content_body(self, mock_request):
        mock_request.side_effect = _fake_site({
            "https://www.macrumors.com": _MR_HOME,
            "https://www.macrumors.com/2026/10/04/story/": _MR_ARTICLE,
        })

        articles = fetch_macrumors_news()

        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0]["content"], "MacRumors body.")


if __name__ == "__main__":
    unittest.main()
