# -*- coding: utf-8 -*-
import sys
import unittest
import logging

import eb_lic_manager.flex_lm.config_file as p

from lark.tree import Tree
from lark.lexer import Token

STANDARD_LOGGING_LEVEL = logging.INFO
logging.basicConfig(level=STANDARD_LOGGING_LEVEL, stream=sys.stderr)


def set_logging_level_to(level):
    logger = logging.getLogger()
    logger.setLevel(level)

#TODO: replace tests of values with Lark.Tree comparison where it simplifies tests
# (see test_server)

class TestParse(unittest.TestCase):
    def setUp(self) -> None:
        set_logging_level_to(STANDARD_LOGGING_LEVEL)

    def test_complete_config_file(self):
#        set_logging_level_to(logging.DEBUG)
        with open("../Samples/aucotec.lic") as f:
            sample_config_file = f.read()

        j = p.parse(sample_config_file)

        logging.debug(j)
        logging.debug(j.pretty())

    def test_empty_lines(self):
        """
        Empty lines should be implicitely ignored.
        Parsing return an empty list
        :return: Nothing
        """
        samples = [("", "nothing"),
                   ("\n", "newline"),
                   ("   \n", "spaces newline"),
                   ("\n\n", "two newlines"),
                   ("\n   \n", "newline, spaces newline"),
                   ("\t\n   \n", "tab newline, spaces newline"),
                   ("  \t  \n   \n", "spaces tab spaces newline, spaces newline")
                   ]

        for s in samples:
            with self.subTest(s=s[1]):
                j = p.parse(s[0])
                logging.debug(j)
                logging.debug(j.pretty())

                self.assertFalse(j.children)

    def test_comments(self):
        """
        Comments should be ignored.
        Parsing return an empty list
        :return: Nothing
        """
        samples = [
            ("# only one comment", "one comment"),
            ("# only one comment\n", "one comment and newline"),
            ("# one comment followed by empty line\n"\
             "\t\n"\
             "# One more comment", "Comment, empty line, comment"),
            ("   \n"\
             "# one comment with empty line before an after\n" \
             "    \n"\
             "# One more comment", "Comments with empty lines before and after"),
        ]

        for s in samples:
            with self.subTest(s=s[1]):
                j = p.parse(s[0])
                logging.debug(j)
                logging.debug(j.pretty())

                self.assertFalse(j.children)

    def test_server(self):
        """
        Server lines are decoded
        :return: Nothing
        """
        # set_logging_level_to(logging.DEBUG)

        samples = [
            ("SERVER my_server1 17007ea8 11987", "Single server"),
            ("SERVER my_server1 17007ea8 11987 PRIMARY_IS_MASTER HEARTBEAT_INTERVAL=1", "Single server with options"),
            ("SERVER my_server1 17007ea8 11987\n"\
             "SERVER my_server2 27007ea8 21987\n"\
             "SERVER my_server3 37007ea8 31987", "Three server")
        ]

        trees = [Tree('config', [
                    Tree('server',
                       [Token('SERVER_NAME', 'my_server1'),
                        Token('SERVER_ID', '17007ea8'),
                        Token('SERVER_PORT', '11987'),
                        ])
                ]),
                Tree('config', [
                    Tree('server',
                       [Token('SERVER_NAME', 'my_server1'),
                        Token('SERVER_ID', '17007ea8'),
                        Token('SERVER_PORT', '11987'),
                        Token('SERVER_REST', 'PRIMARY_IS_MASTER HEARTBEAT_INTERVAL=1')]),
                ]),
                Tree('config', [
                    Tree('server',
                        [Token('SERVER_NAME', 'my_server1'),
                         Token('SERVER_ID', '17007ea8'),
                         Token('SERVER_PORT', '11987'),
                        ]
                    ),
                    Tree('server',
                        [Token('SERVER_NAME', 'my_server2'),
                         Token('SERVER_ID', '27007ea8'),
                         Token('SERVER_PORT', '21987'),
                        ]
                    ),
                    Tree('server',
                        [Token('SERVER_NAME', 'my_server3'),
                         Token('SERVER_ID', '37007ea8'),
                         Token('SERVER_PORT', '31987'),
                        ]
                    ),
                 ])
               ]

        for sample, expected in zip(samples, trees):
            with self.subTest(s=sample[1]):
                tree = p.parse(sample[0])
                logging.debug(tree)
                logging.debug(tree.pretty())

                self.assertEqual(expected, tree)

    def test_vendor(self):
        """
        Vendor lines are decoded
        :return: Nothing
        """

        # VENDOR vendor[vendor_daemon_path] \
        #     [[OPTIONS =]options_file_path] [[PORT =]port]

        samples = [
            ('VENDOR vendor_name', "Only vendor name"),
            ('VENDOR vendor_name deamon_path', "Vendor name, deamon path"),
            ('VENDOR vendor_name deamon_path OPTIONS="/path/to/file.opt"', "Vendor name, 'OPTIONS='+path"),
            ('VENDOR vendor_name deamon_path OPTIONS="/path/to/file.opt" PORT=1234',
                "Vendor name, 'OPTIONS='+path, 'PORT='+port")
        ]

        values = [
            {'VENDOR_NAME': 'vendor_name',
             'VENDOR_OPTION': ['deamon_path', 'OPTIONS="/path/to/file.opt"', 'PORT=1234']},
        ]

        for s in samples:
            count = {'VENDOR_OPTION': -1}

            with self.subTest(s=s[1]):
                j = p.parse(s[0])

                logging.debug(j)
                logging.debug(j.pretty())

                children = j.children

                for i in range(len(children)):
                    child = children[i]
                    d = values[i]

                    logging.debug(d)

                    for token in children[i].children:
                        expected = d[token.type]
                        if isinstance(expected, list):
                            count[token.type] += 1
                            expected = expected[count[token.type]]

                        self.assertEqual(token.value, expected)

    def test_use_server(self):
        """
        USE_SERVER should be ignored.
        Parsing return an empty list
        :return: Nothing
        """
        samples = [
            ("USE_SERVER", "without newline"),
            ("USE_SERVER\n", "with newline"),
        ]

        for s in samples:
            with self.subTest(s=s[1]):
                j = p.parse(s[0])
                logging.debug(j)
                logging.debug(j.pretty())

                self.assertFalse(j.children)

    def test_feature(self):
        """
        Server lines are decoded
        :return: Nothing

        {FEATURE|INCREMENT} feature vendor feat_version exp_date \
            num_lic SIGN=sign [optional_attributes]

        optional_attribute can be KEY, KEY=VALUE, KEY="VALUE STRING"
        """
        #TODO: extend tests (add optional features)

        # set_logging_level_to(logging.DEBUG)

        samples = [
            ('FEATURE feature vendor version exp_date num_lic SIGN=sign', "Minimal feature"),
            ('FEATURE feature vendor version exp_date num_lic SIGN="sign"', "Minimal feature, SIGN quoted"),
        ]

        values = [
            {'FEAT_NAME': 'feature',
             'FEAT_VENDOR': 'vendor',
             'FEAT_VERSION': 'version',
             'EXP_DATE': 'exp_date',
             'NUM_LIC': 'num_lic',
             'FEAT_OPTIONAL': ['SIGN=sign'],
             },
            {'FEAT_NAME': 'feature',
             'FEAT_VENDOR': 'vendor',
             'FEAT_VERSION': 'version',
             'EXP_DATE': 'exp_date',
             'NUM_LIC': 'num_lic',
             'FEAT_OPTIONAL': ['SIGN="sign"'],
             },
        ]

        for sample, expected in zip(samples, values):
            with self.subTest(s=sample[1]):
                tree = p.parse(sample[0])
                logging.debug(tree)
                logging.debug(tree.pretty())

                for token in tree.children[0].children:
                    expected_val = expected[token.type]

                    if isinstance(expected_val, list):
                        self.assertIn(token.value, expected_val)
                    else:
                        self.assertEqual(token.value, expected_val)


if __name__ == '__main__':
    unittest.main()
