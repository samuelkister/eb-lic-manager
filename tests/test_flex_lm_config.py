# -*- coding: utf-8 -*-
import unittest
import logging
import eb_lic_manager.flex_lm.config_file as p

logging.basicConfig(level=logging.INFO)

class TestParse(unittest.TestCase):
    def test_empty_lines(self):
        samples = [("", "nothing"),
                   ("\n", "one empty"),
                   ("   ", "only spaces"),
                   ("   \n", "spaces an newline"),
                   ("\n\n", "two newlines"),
                   ("\n   \n", "newline, spaces an newline")]

        for s in samples:
            with self.subTest(s=s[1]):
                j = p.parse(s[0])
                logging.debug(j)
                logging.debug(j.pretty())

                self.assertFalse(j.children)

    def test_comments(self):
        samples = [
            ("# only one comment", "one comment"),
            ("# only one comment\n", "one comment and newline"),
            ("""# one comment with empty line
            
# One more comment""", "Comment, empty line, comment"),
            ("""
# one comment with empty line before an after

# One more comment""", "Comments with empty lines before and after"),
        ]

        for s in samples:
            with self.subTest(s=s[1]):
                j = p.parse(s[0])
                logging.debug(j)
                logging.debug(j.pretty())

                self.assertFalse(j.children)


if __name__ == '__main__':
    unittest.main()
