import unittest

from message_splitter import split_message


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


if __name__ == "__main__":
    unittest.main()
