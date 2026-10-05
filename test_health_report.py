import unittest

from health_report import HealthReport


class HealthReportTest(unittest.TestCase):
    def test_no_alert_when_sources_are_healthy(self):
        report = HealthReport()
        report.record_source("한국", "get_naver_news", [{"content": "본문"}, {"content": "본문"}])

        self.assertIsNone(report.format_alert())

    def test_warns_when_source_returns_nothing(self):
        report = HealthReport()
        report.record_source("한국", "get_naver_news", [])

        self.assertIn("한국/get_naver_news: 기사 0개", report.format_alert())

    def test_warns_when_most_bodies_are_missing(self):
        report = HealthReport()
        report.record_source("한국", "get_nate_news", [{"content": None}, {"content": None}, {"content": "본문"}])

        self.assertIn("본문 없는 기사 2/3개", report.format_alert())

    def test_tolerates_occasional_missing_body(self):
        report = HealthReport()
        report.record_source("한국", "get_nate_news", [{"content": None}, {"content": "본문"}, {"content": "본문"}])

        self.assertIsNone(report.format_alert())

    def test_records_errors(self):
        report = HealthReport()
        report.record_error("세계", "get_google_world_news", RuntimeError("boom"))

        self.assertIn("세계/get_google_world_news: 오류 - boom", report.format_alert())


if __name__ == "__main__":
    unittest.main()
