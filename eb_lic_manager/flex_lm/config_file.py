# -*- coding: utf-8 -*-

from lark import Lark, Transformer, v_args
config_grammar = r"""
    start: (_EOL
        | _COMMENT
        | server
        | vendor
        | _USE_SERVER)*
    
    _EOL: /[ \t]*/ NEWLINE
    
    _COMMENT: "#" /[^\n]*/ [_EOL]
    
    server: "SERVER "i SERVER_NAME SERVER_ID SERVER_PORT [SERVER_REST] [_EOL]
    SERVER_NAME: /\S+/
    SERVER_ID: /\S+/
    SERVER_PORT: INT
    SERVER_REST: /[^\n]+/
    
    vendor: "VENDOR "i VENDOR_NAME [VENDOR_OPTION*] [_EOL]
    VENDOR_NAME: NON_WHITESPACE
    VENDOR_OPTION: NON_WHITESPACE+
    
    _USE_SERVER: "USE_SERVER" [_EOL]
    
    WS: /[ \t\f\r]+/
    NON_WHITESPACE: /\S+/
    
    %ignore WS
    
    %import common.NEWLINE
    %import common.WORD
    %import common.INT
"""

config_parser = Lark(config_grammar, parser="lalr")
parse = config_parser.parse


if __name__ == '__main__':
    pass
