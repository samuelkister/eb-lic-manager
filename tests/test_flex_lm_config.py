# -*- coding: utf-8 -*-
import unittest
import logging
import eb_lic_manager.flex_lm.config_file as p

logging.basicConfig(level=logging.INFO)

sample_config = \
r"""
# Comment line 1
# Comment line 2

# Comment line 3
"""

"""
SERVER my_server 17007ea8 1700
VENDOR sampled
FEATURE f1 sampled 1.000 01-jan-2005 10 SIGN=9BFAC0316462
FEATURE f2 sampled 1.000 01-jan-2005 10 SIGN=1B9A308CC0F7
"""

class TestParse(unittest.TestCase):
    def test_comment(self):
        "Pass"

        j = p.parse(sample_config)
        print(j)
        print(j.pretty())

        self.assertFalse(False)


if __name__ == '__main__':
    unittest.main()
