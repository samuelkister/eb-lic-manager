# -*- coding: utf-8 -*-
import re

from lark import Lark, Transformer, Tree

from eb_lic_manager.gui.context import Context

config_grammar = r"""
    config: (_EOL
        | _COMMENT
        | server
        | vendor
        | _USE_SERVER
        | feature)*
    
    _EOL: /[ \t]*/ NEWLINE
    
    _COMMENT: "#" /[^\n]*/ [_EOL]
    
    server: "SERVER "i SERVER_NAME SERVER_ID SERVER_PORT [SERVER_REST] [_EOL]
    SERVER_NAME: NON_WHITESPACE
    SERVER_ID: NON_WHITESPACE
    SERVER_PORT: INT
    SERVER_REST: /[^\n]+/
    
    vendor: "VENDOR "i VENDOR_NAME [VENDOR_OPTION*] [_EOL]
    VENDOR_NAME: NON_WHITESPACE
    VENDOR_OPTION: NON_WHITESPACE
    
    _USE_SERVER: "USE_SERVER" [_EOL]
    
    feature: "FEATURE "i _feature_param [_EOL]
    _feature_param: FEAT_NAME FEAT_VENDOR FEAT_VERSION EXP_DATE NUM_LIC [feat_optional*]
    
    FEAT_NAME: NON_WHITESPACE
    FEAT_VENDOR: NON_WHITESPACE
    FEAT_VERSION: NON_WHITESPACE
    EXP_DATE: NON_WHITESPACE
    NUM_LIC: NON_WHITESPACE
    feat_optional: KEY ["=" _value]
    _value: STRING | NON_STRING
    KEY: CNAME
    
    WS: /[ \t\f\r]+/
    NON_WHITESPACE: /\S+/
    
    NON_STRING: /[^"]\S+/
    STRING: "\"" /.*?[^"]/* "\""

    _LINE_CONTINUATION: /\\[ \t\f\r]*\n/ [WS]
    
    %ignore WS
    %ignore _LINE_CONTINUATION
    
    %import common.NEWLINE
    // %import common.ESCAPED_STRING
    %import common.INT
    %import common.CNAME
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
    def __init__(self, context: Context):
        super().__init__()
        self._context = context

    def server(self, children):
        server = self._context.create_new_server()

        switcher = {
            'SERVER_NAME': lambda server, name: server.set_name(name),
            'SERVER_ID': lambda server, id: server.set_id(id),
            'SERVER_PORT': lambda server, port: server.set_port(port)
        }

        for token in children:
            fun = switcher.get(token.type)
            if fun:
                fun(server, token.value)


    # def vendor(self, child):
    #     print("VENDOR: ")
    #     print(child)
    #
    # def feature(self, child):
    #     print("FEATURE: ")
    #     print(child)
    #
    # def feat_optional(self, child):
    #     print("FEATURE OPTIONAL: ")
    #     print(child)
    #     return "Feature optional"



if __name__ == '__main__':
    pass
