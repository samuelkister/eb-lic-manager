# -*- coding: utf-8 -*-
import sys
import unittest
import logging

import eb_lic_manager.flex_lm.config_file_reader as p

from lark.tree import Tree
from lark.lexer import Token

STANDARD_LOGGING_LEVEL = logging.INFO
logging.basicConfig(level=STANDARD_LOGGING_LEVEL, stream=sys.stderr)


def set_logging_level_to(level):
    logger = logging.getLogger()
    logger.setLevel(level)


def generate_tree(construct):
    # logging.debug("generate_tree({})".format(construct))

    if not isinstance(construct, list) and not isinstance(construct, tuple):
        raise AttributeError("construct not list nor tuple {}".format(construct))

    if isinstance(construct, tuple):
        return Token(construct[0], construct[1])

    if isinstance(construct, list):
        if len(construct) == 1:
            return Tree(construct[0], [])
        else:
            return Tree(construct[0], [generate_tree(el) for el in construct[1:]])


def generate_expected_tree(construct=[]):
    return generate_tree(['config', construct])


class TestTreeGenerator(unittest.TestCase):
    """testing of the tree generator"""

    def setUp(self) -> None:
        set_logging_level_to(STANDARD_LOGGING_LEVEL)

    def testWrongParmeters(self):
        with self.assertRaises(Exception):
            generate_tree([])

        with self.assertRaises(Exception):
            generate_tree(('NoName',))

    def testEmptyTree(self):
        # set_logging_level_to(logging.DEBUG)

        expect = Tree('config', [])

        value = generate_tree(['config'])
        self.assertEqual(expect, value)

    def testTreeWithOneToken(self):
        expect = Tree('config', [Token('TOKEN1', 'Value1')])
        value = generate_tree(['config', ('TOKEN1', 'Value1')])

        self.assertEqual(expect, value)

    def testTreeWithMultipleToken(self):
        expect = Tree('config', [Token('TOKEN1', 'Value1'), Token('TOKEN2', 'Value2')])
        value = generate_tree(['config', ('TOKEN1', 'Value1'), ('TOKEN2', 'Value2')])

        self.assertEqual(expect, value)

    def testTreeWithSubTree(self):
        expect = Tree('config', [
            Tree('subtree', [Token('TOKEN1', 'Value1'), Token('TOKEN2', 'Value2')])
        ])

        value = generate_tree(['config', ['subtree', ('TOKEN1', 'Value1'), ('TOKEN2', 'Value2')]])

        self.assertEqual(expect, value)

    def testComplexTree(self):
        expect = Tree('config', [
            Token('TOKEN1', 'Value1'),
            Tree('subtree1', [Token('TOKEN1.1', 'Value1.1'), Token('TOKEN1.2', 'Value1.2')]),
            Token('TOKEN2', 'Value2'),
            Tree('subtree2', [Token('TOKEN2.1', 2.1), Token('TOKEN2.2', 'Value2.2')]),
        ])

        value = generate_tree(['config',
                               ('TOKEN1', 'Value1'),
                               ['subtree1', ('TOKEN1.1', 'Value1.1'), ('TOKEN1.2', 'Value1.2')],
                               ('TOKEN2', 'Value2'),
                               ['subtree2', ('TOKEN2.1', 2.1), ('TOKEN2.2', 'Value2.2')]
                               ])

        self.assertEqual(expect, value)


# TODO: replace tests of values with Lark.Tree comparison where it simplifies tests
#  (see test_server)

class TestParse(unittest.TestCase):
    def setUp(self) -> None:
        set_logging_level_to(STANDARD_LOGGING_LEVEL)

    def test_complete_config_file(self):
        # set_logging_level_to(logging.DEBUG)
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
            ("# one comment followed by empty line\n" \
             "\t\n" \
             "# One more comment", "Comment, empty line, comment"),
            ("   \n" \
             "# one comment with empty line before an after\n" \
             "    \n" \
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
            ("SERVER my_server1 17007ea8 11987\n" \
             "SERVER my_server2 27007ea8 21987\n" \
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
            count = {'VENDOR_OPTION': -1}

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
        # TODO: extend tests (add optional features)

        # set_logging_level_to(logging.DEBUG)

        base_feature = 'FEATURE feature vendor version exp_date num_lic '
        base_expected_tree = \
            ['feature',
             ('FEAT_NAME', 'feature'),
             ('FEAT_VENDOR', 'vendor'),
             ('FEAT_VERSION', 'version'),
             ('EXP_DATE', 'exp_date'),
             ('NUM_LIC', 'num_lic'),
             ]

        tests_inputs = [
            ("Minimal feature, SIGN unquoted",
             'SIGN=sign',
             ['feat_optional',
              ('KEY', 'SIGN'),
              ('NON_STRING', 'sign')
              ]
             ),

            ("Minimal feature, SIGN quoted",
             'SIGN="sign"',
             ['feat_optional',
              ('KEY', 'SIGN'),
              ('STRING', '"sign"')
              ]
             ),

            ("Minimal feature, SIGN multilines",
             'SIGN="first \\\n   second"',
             ['feat_optional',
              ('KEY', 'SIGN'),
          ('STRING', '"first \\\n   second"')
              ]
             ),
        ]

        data = [(base_feature + feat_comp, desc, generate_expected_tree(base_expected_tree+[tree_comp]))
                for desc, feat_comp, tree_comp in tests_inputs]

        logging.debug(data)

        for sample, info, expected in data:
            with self.subTest(s=info):
                tree = p.parse(sample)
                logging.debug(sample)
                logging.debug(tree)
                logging.debug(tree.pretty())

                self.assertEqual(expected, tree)


class TestTransformer(unittest.TestCase):
    def setUp(self) -> None:
        set_logging_level_to(STANDARD_LOGGING_LEVEL)

    @unittest.skip("asserts TBD")
    def test_complete_config_file(self):
        # set_logging_level_to(logging.DEBUG)
        with open("../Samples/aucotec.lic") as f:
            sample_config_file = f.read()

        j = p.parse(sample_config_file)

        logging.debug(j)
        logging.debug(j.pretty())

    def test_empty_tree(self):

        self.assertTrue(True)

    @unittest.skip("TBD")
    def test_single_server(self):
        """
        Server lines are decoded
        :return: Nothing
        """
        # set_logging_level_to(logging.DEBUG)

        tree = generate_expected_tree([Tree('config', [
            Tree('server',
                 [Token('SERVER_NAME', 'my_server1'),
                  Token('SERVER_ID', '17007ea8'),
                  Token('SERVER_PORT', '11987'),
                  Token('SERVER_REST', 'PRIMARY_IS_MASTER HEARTBEAT_INTERVAL=1')]),
        ])])


    @unittest.skip("TBD")
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
            count = {'VENDOR_OPTION': -1}

    @unittest.skip("TBD")
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

    @unittest.skip("TBD")
    def test_feature(self):
        """
        Server lines are decoded
        :return: Nothing

        {FEATURE|INCREMENT} feature vendor feat_version exp_date \
            num_lic SIGN=sign [optional_attributes]

        optional_attribute can be KEY, KEY=VALUE, KEY="VALUE STRING"
        """
        # TODO: extend tests (add optional features)

        # set_logging_level_to(logging.DEBUG)

        base_feature = 'FEATURE feature vendor version exp_date num_lic '
        base_expected_tree = \
            ['feature',
             ('FEAT_NAME', 'feature'),
             ('FEAT_VENDOR', 'vendor'),
             ('FEAT_VERSION', 'version'),
             ('EXP_DATE', 'exp_date'),
             ('NUM_LIC', 'num_lic'),
             ]

        tests_inputs = [
            ("Minimal feature, SIGN unquoted",
             'SIGN=sign',
             ['feat_optional',
              ('KEY', 'SIGN'),
              ('NON_STRING', 'sign')
              ]
             ),

            ("Minimal feature, SIGN quoted",
             'SIGN="sign"',
             ['feat_optional',
              ('KEY', 'SIGN'),
              ('STRING', '"sign"')
              ]
             ),

            ("Minimal feature, SIGN multilines",
             'SIGN="first \\\n   second"',
             ['feat_optional',
              ('KEY', 'SIGN'),
          ('STRING', '"first \\\n   second"')
              ]
             ),
        ]

        data = [(base_feature + feat_comp, desc, generate_expected_tree(base_expected_tree+[tree_comp]))
                for desc, feat_comp, tree_comp in tests_inputs]

        logging.debug(data)

        for sample, info, expected in data:
            with self.subTest(s=info):
                tree = p.parse(sample)
                logging.debug(sample)
                logging.debug(tree)
                logging.debug(tree.pretty())

                self.assertEqual(expected, tree)


if __name__ == '__main__':
    unittest.main()
