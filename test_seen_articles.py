import json
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import seen_articles


class SeenArticlesTest(unittest.TestCase):
    def setUp(self):
        self._tmp_dir = TemporaryDirectory()
        self.addCleanup(self._tmp_dir.cleanup)
        store_path = Path(self._tmp_dir.name) / "sent_history.json"
        patcher = patch.object(seen_articles, "_STORE_PATH", store_path)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.store_path = store_path

    def test_filter_unseen_returns_all_when_history_empty(self):
        articles = [{"url": "https://a.com/1"}, {"url": "https://a.com/2"}]
        self.assertEqual(seen_articles.filter_unseen(articles), articles)

    def test_filter_unseen_excludes_previously_sent_urls(self):
        seen_articles.mark_as_sent([{"url": "https://a.com/1"}])

        articles = [{"url": "https://a.com/1"}, {"url": "https://a.com/2"}]
        result = seen_articles.filter_unseen(articles)

        self.assertEqual(result, [{"url": "https://a.com/2"}])

    def test_filter_unseen_keeps_articles_without_url(self):
        articles = [{"title": "no url here"}]
        self.assertEqual(seen_articles.filter_unseen(articles), articles)

    def test_mark_as_sent_prunes_entries_older_than_retention(self):
        stale_time = datetime.now(timezone.utc) - timedelta(days=seen_articles._RETENTION_DAYS + 1)
        self.store_path.write_text(
            json.dumps({"https://old.com/article": stale_time.isoformat()}),
            encoding="utf-8",
        )

        seen_articles.mark_as_sent([{"url": "https://new.com/article"}])

        history = json.loads(self.store_path.read_text(encoding="utf-8"))
        self.assertNotIn("https://old.com/article", history)
        self.assertIn("https://new.com/article", history)

    def test_mark_as_sent_keeps_recent_entries(self):
        recent_time = datetime.now(timezone.utc) - timedelta(days=1)
        self.store_path.write_text(
            json.dumps({"https://recent.com/article": recent_time.isoformat()}),
            encoding="utf-8",
        )

        seen_articles.mark_as_sent([{"url": "https://new.com/article"}])

        history = json.loads(self.store_path.read_text(encoding="utf-8"))
        self.assertIn("https://recent.com/article", history)
        self.assertIn("https://new.com/article", history)


if __name__ == "__main__":
    unittest.main()
