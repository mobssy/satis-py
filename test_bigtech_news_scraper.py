import unittest

from bigtech_news_scraper import _format_bigtech_title


class FormatBigtechTitleTest(unittest.TestCase):
    def test_tags_company_mentions(self):
        self.assertEqual(_format_bigtech_title("Nvidia beats estimates"), "[NVIDIA] Nvidia beats estimates")
        self.assertEqual(_format_bigtech_title("Alphabet shares rise"), "[Google] Alphabet shares rise")

    def test_does_not_match_inside_other_words(self):
        self.assertEqual(_format_bigtech_title("Metal prices surge"), "[BigTech] Metal prices surge")
        self.assertEqual(_format_bigtech_title("A metaverse winter"), "[BigTech] A metaverse winter")

    def test_ignores_amazon_rainforest(self):
        title = "The Amazon's future is on the ballot in Brazil"

        self.assertEqual(_format_bigtech_title(title), f"[BigTech] {title}")

    def test_still_tags_amazon_the_company(self):
        self.assertEqual(_format_bigtech_title("Amazon cuts AWS prices"), "[Amazon] Amazon cuts AWS prices")

    def test_falls_through_to_later_company_when_amazon_is_rainforest(self):
        title = "Apple pledges funds for the Amazon rainforest"

        self.assertEqual(_format_bigtech_title(title), f"[Apple] {title}")


if __name__ == "__main__":
    unittest.main()
