# -*- coding: utf-8 -*-
import sys
import unittest
import logging
from unittest.mock import MagicMock

import eb_lic_manager.flex_lm.config_file_reader as p

from lark.tree import Tree
from lark.lexer import Token

# from eb_lic_manager.application.context import Context

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


def generate_expected_tree(construct=None):
    if not construct:
        return generate_tree(['config'])

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

class TestParser(unittest.TestCase):
    def setUp(self) -> None:
        set_logging_level_to(STANDARD_LOGGING_LEVEL)

        self.common_arguments = 'unquoted_value 1 "quoted value" 235 string_quoted="key quoted" digit=6 number=8945135 ' \
                                'key=value_for_key'
        self.common_arguments_tree = [
            ['parameter', ('NON_STRING', 'unquoted_value')],
            ['parameter', ('NON_STRING', '1')],
            ['parameter', ('STRING', '"quoted value"')],
            ['parameter', ('NON_STRING', '235')],
            ['parameter', ('KEY', 'string_quoted='), ('STRING', '"key quoted"')],
            ['parameter', ('KEY', 'digit='), ('NON_STRING', '6')],
            ['parameter', ('KEY', 'number='), ('NON_STRING', '8945135')],
            ['parameter', ('KEY', 'key='), ('NON_STRING', 'value_for_key')],
        ]

    def test_complete_config_file(self):
        # Test just no crash

        set_logging_level_to(logging.DEBUG)
        with open("../Samples/aucotec.lic") as f:
            sample_config_file = f.read()

        j = p.parse(sample_config_file)

        logging.debug(j)
        logging.debug(j.pretty())

    def test_ignored_elements(self):
        """
        Test the elements that should be ignored by the parser
        (i.e. those that don't generate a node in the tree)
        :return: Nothing
        """
        # set_logging_level_to(logging.DEBUG)

        # Defining the list of the ignored token
        ignored_token = [
            # Empty lines
            ("", "nothing"),
            ("\n", "newline"),
            ("   \n", "spaces newline"),
            ("\n\n", "two newlines"),
            ("\n   \n", "newline, spaces newline"),
            ("\t\n   \n", "tab newline, spaces newline"),
            ("  \t  \n   \n", "spaces tab spaces newline, spaces newline"),

            # Comments
            ("# only one comment", "one comment"),
            ("# only one comment\n", "one comment and newline"),
            ("# one comment followed by empty line\n" \
             "\t\n" \
             "# One more comment", "Comment, empty line, comment"),
            ("   \n" \
             "# one comment with empty line before an after\n" \
             "    \n" \
             "# One more comment", "Comments with empty lines before and after"),

            # USE SERVER
            ("USE_SERVER", "without newline"),
            ("USE_SERVER\n", "with newline"),
        ]

        empty_tree = generate_expected_tree()

        for sample, info in ignored_token:
            with self.subTest(sample=info):
                tree = p.parse(sample)
                logging.debug(tree)
                logging.debug(tree.pretty())

                self.assertEqual(empty_tree, tree)

    def test_parsed_elements(self):
        """
        Test the elements that populate the tree with values
        :return: Nothing
        """
        # set_logging_level_to(logging.DEBUG)

        # Defining the list of the parsed token
        parsed_token = [
            ('SERVER', 'server', 'Server'),
            ('VENDOR', 'vendor', 'Vendor'),
            ('FEATURE', 'feature', 'Feature')
        ]

        for sample, node, info in parsed_token:
            with self.subTest(sample=info):
                config = sample + ' ' + self.common_arguments
                expected_tree = generate_expected_tree([node] + self.common_arguments_tree)

                tree = p.parse(config)
                logging.debug(tree)
                logging.debug(tree.pretty())

                self.assertEqual(expected_tree, tree)


class TestTransformer(unittest.TestCase):
    def setUp(self) -> None:
        set_logging_level_to(STANDARD_LOGGING_LEVEL)
        self.factory_mock = MagicMock()
        self.transformer = p.ConfigTransformer(self.factory_mock)

    def test_argument_transformer(self):
        # set_logging_level_to(logging.DEBUG)

        # Empty return nothing
        self.assertEqual(None, self.transformer.parameter([]))

        # Only one non string return this non string
        non_string = "non_string"

        token_non_string = Token('NON_STRING', non_string)
        self.assertEqual(non_string, self.transformer.parameter([token_non_string]))

        # Only one string return this string, stripped
        a_string = "a_string"
        token_string = Token('STRING', '"{}"'.format(a_string))
        self.assertEqual(a_string, self.transformer.parameter([token_string]))

        # Key and non string
        a_key = "a_key"
        token_key = Token("KEY", a_key + "=")

        self.assertEqual((a_key, non_string), self.transformer.parameter([token_key, token_non_string]))

        # Key and string
        self.assertEqual((a_key, a_string), self.transformer.parameter([token_key, token_string]))

    def test_build_args_from_list(self):
        # set_logging_level_to(logging.DEBUG)

        # Return one empty list an one empty dict if receiving nothing
        args, kwargs = self.transformer.build_args_from_list([])
        self.assertListEqual([], args, "ARGS not empty")
        self.assertDictEqual(dict(), kwargs, "KWARGS not empty")

        # Return list of values if no tuples
        list_values = ["a", 1]
        args, kwargs = self.transformer.build_args_from_list(list_values)
        self.assertListEqual(list_values, args, "ARGS not corresponding")
        self.assertDictEqual(dict(), kwargs, "KWARGS not empty")

        # Return dictionary if no values
        list_dict = [("a", 1), ("b", 2)]
        args, kwargs = self.transformer.build_args_from_list(list_dict)
        self.assertListEqual([], args, "ARGS not corresponding")
        self.assertDictEqual(dict(list_dict), kwargs, "KWARGS not corresponding")

        # Return liste of value and dictionary
        mixed_list = list_values[:]
        mixed_list.extend(list_dict)
        args, kwargs = self.transformer.build_args_from_list(mixed_list)
        self.assertListEqual(list_values, args, "ARGS not corresponding")
        self.assertDictEqual(dict(list_dict), kwargs, "KWARGS not corresponding")


        # Raise error if value follow tuple (value before is allowed)
        with self.assertRaises(Exception):
            self.transformer.build_args_from_list(["a", 1, ("k", "val"), 42])

    def test_server(self):
        self.transformer.build_args_from_list = lambda x: (["a", 1], {"p1": "b", "p2": 2})
        self.transformer.server(None)
        self.factory_mock.add_new_server.assert_called_with("a", 1, p1="b", p2=2)


    @unittest.skip("asserts TBD")
    def test_complete_config_file(self):
        # set_logging_level_to(logging.DEBUG)
        with open("../Samples/aucotec.lic") as f:
            sample_config_file = f.read()

        j = p.parse(sample_config_file)

        logging.debug(j)
        logging.debug(j.pretty())

    @unittest.skip("asserts TBD")
    def test_empty_tree(self):
        self.assertTrue(True)

    @unittest.skip("asserts TBD")
    def test_single_server(self):
        """
        One single server
        """
        # set_logging_level_to(logging.DEBUG)

        server_name = 'my_server1'
        server_id = '17007ea8'
        server_port = '11987'
        server_rest = 'PRIMARY_IS_MASTER HEARTBEAT_INTERVAL=1'

        tree = generate_expected_tree(
            ['server',
                ('SERVER_NAME', server_name),
                ('SERVER_ID', server_id),
                ('SERVER_PORT', server_port),
                ('SERVER_REST', server_rest)
             ])

        logging.debug(tree)
        logging.debug(tree.pretty())

        self.transformer.transform(tree)

        servers = self.context.get_servers()

        self.assertEqual(1, len(servers), "No single server created")

        server = servers[0]

        self.assertEqual(server_name, server.name)
        self.assertEqual(server_id, server.id)
        self.assertEqual(server_port, server.port)

    @unittest.skip("asserts TBD")
    def test_multiple_server(self):
        """
        Three server
        """
        # set_logging_level_to(logging.DEBUG)

        server_name = ['my_server1', 'my_server2', 'my_server3']
        server_id = ['17007ea8', '27007ea8', '37007ea8']
        server_port = ['11987', '22987', '33987']

        servers_tree = ['config']
        for x in range(3):
            servers_tree.append(
                ['server',
                    ('SERVER_NAME', server_name[x]),
                    ('SERVER_ID', server_id[x]),
                    ('SERVER_PORT', server_port[x])
                ])

        tree = generate_tree(servers_tree)

        logging.debug(tree)
        logging.debug(tree.pretty())

        self.transformer.transform(tree)

        servers = self.context.get_servers()

        self.assertEqual(3, len(servers), "Wrong amount of servers created")

        for x in range(3):
            server = servers[x]

            self.assertEqual(server_name[x], server.name)
            self.assertEqual(server_id[x], server.id)
            self.assertEqual(server_port[x], server.port)

    @unittest.skip("asserts TBD")
    def test_vendor(self):
        """
        Vendor lines are decoded

        # VENDOR vendor [vendor_daemon_path] \
        #     [[OPTIONS=]options_file_path] [[PORT=]port]
        """

        # set_logging_level_to(logging.DEBUG)

        vendor_name = 'my_vendor'
        daemon_path = 'my_daemon_path'
        option_file_path = '/option/file/path'
        daemon_port = '123654'

        tree = generate_expected_tree(
            ['vendor',
                ('VENDOR_NAME', vendor_name)
             ])
        self.transformer.transform(tree)

        vendor = self.context.get_vendor()
        self.assertEqual(vendor_name, vendor.name)

        tree = generate_expected_tree(
            ['vendor',
                ('VENDOR_NAME', vendor_name),
                ('VENDOR_OPTION', vendor_name)
             ])
        self.transformer.transform(tree)

        vendor = self.context.get_vendor()
        self.assertEqual(vendor_name, vendor.name)

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
