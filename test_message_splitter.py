import unittest

from message_splitter import split_message, visible_length


class SplitMessageTest(unittest.TestCase):
    def test_short_message_stays_single_part(self):
        self.assertEqual(split_message("a\nb", 10), ["a\nb\n"])

    def test_groups_lines_without_exceeding_limit(self):
        parts = split_message("aaaa\nbbbb\ncccc", 10)

        self.assertEqual(parts, ["aaaa\nbbbb\n", "cccc\n"])
        self.assertTrue(all(len(p) <= 10 for p in parts))

    def test_long_line_is_hard_split(self):
        parts = split_message("x" * 25, 10)

        self.assertEqual(parts, ["x" * 10, "x" * 10, "x" * 5 + "\n"])

    def test_line_exactly_at_limit_produces_no_empty_part(self):
        parts = split_message("x" * 10 + "\nnext", 10)

        self.assertNotIn("", parts)
        self.assertTrue(all(len(p) <= 10 for p in parts))
        self.assertEqual("".join(parts).replace("\n", ""), "x" * 10 + "next")

    def test_line_one_below_limit_fits_with_newline(self):
        parts = split_message("x" * 9 + "\ny", 10)

        self.assertEqual(parts, ["x" * 9 + "\n", "y\n"])


class VisibleLengthTest(unittest.TestCase):
    def test_excludes_tags_and_link_urls(self):
        html = '<a href="https://news.google.com/very/long/url">제목</a>'

        self.assertEqual(visible_length(html), 2)

    def test_counts_escaped_entities_as_single_characters(self):
        self.assertEqual(visible_length("A &lt; B &amp; C"), 9)


if __name__ == "__main__":
    unittest.main()
