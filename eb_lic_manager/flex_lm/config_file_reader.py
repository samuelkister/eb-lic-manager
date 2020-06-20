# -*- coding: utf-8 -*-
import re
from lark import Lark, Transformer, Tree

"""
All classes needed to read and transform a flex-LM config file
to Python objects.
"""

config_grammar = r"""
    config: (_EOL
        | _COMMENT
        | _USE_SERVER
        | server
        | vendor
        | feature)*
    
    _EOL: /[ \t]*/ NEWLINE
    
    _COMMENT: "#" /[^\n]*/ [_EOL]
    
    _USE_SERVER: "USE_SERVER" [_EOL]
    
    server: "SERVER" parameter*
    vendor: "VENDOR" parameter*
    feature: ("LIC" | "FEATURE") parameter*

    parameter: KEY? _value
    _value: NON_STRING | _string

    NON_STRING: /[^"]\S*/
    _string: STRING
    KEY: CNAME _EQUAL
    _EQUAL: WS* "=" WS*

    %import common.ESCAPED_STRING -> STRING
    %import common.WS
    %import common.NEWLINE
    %import common.CNAME
    
    %ignore WS
"""

# TODO: Write+Test transformer that generate a direct usable "config_file" object
config_parser = Lark(config_grammar, parser='lalr', start='config')

def parse(text: str) -> Tree:
    """
    Parse a config file content
    :param text: the content of the config file as a string
    :return: A lark Tree
    """

    # Remove all line continuation from the original
    text = re.sub(r"\s*\\\s*", " ", text, flags=re.MULTILINE)

    return config_parser.parse(text)


class ConfigTransformer(Transformer):
    """
    Convert the lark tree of a parsed config file to a config object
    """

    def __init__(self, config_factory):
        super().__init__()
        self._config_factory = config_factory

    def get_config(self):
        self._config_factory.get_config()

    def build_param_from_tree(self, children):
        has_not_named_args = False
        args = []
        named_args = []

        # for token in children:
        #     if token.type() == "parameter":
        #
        #     fun = switcher.get(token.type)
        #     if fun:
        #         fun(server, token.value)

    def parameter(self, children):
        key = None
        value = None
        for token in children:
            if token.type == "KEY":
                key = token.value[:-1]
            elif token.type == "STRING":
                value = token.value[1:-1]
            elif token.type == "NON_STRING":
                value = token.value
            else:
                raise Exception("Unknown argument type")

        return (key, value) if key else value

    def server(self, children):
        args, named_args = self.build_args_from_list(children)

        return self._config_factory.add_new_server(*args, **named_args)

    def build_args_from_list(self, arguments):
        args = []
        kwargs = []

        had_kwargs = False

        for arg in arguments:
            if isinstance(arg, tuple):
                had_kwargs = True
                kwargs.append(arg)
            else:
                if had_kwargs:
                    raise SyntaxError("positional argument follows keyword argument")

                args.append(arg)

        return args, dict(kwargs)


if __name__ == '__main__':
    pass
