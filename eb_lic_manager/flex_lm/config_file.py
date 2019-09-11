# -*- coding: utf-8 -*-

from lark import Lark, Transformer, v_args
#TODO: Change start rule (in config_file for example)
#TODO: Replace all '/\S+/' with 'NON_WHITESPACE+'
#TODO: Check if 'NON_WHITESPACE**+**' is necessary (='/\S+/', already has +)

config_grammar = r"""
    start: (_EOL
        | _COMMENT
        | server
        | vendor
        | _USE_SERVER
        | feature)*
    
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
    
    feature: "FEATURE "i _feature_param [_EOL]
    _feature_param: FEAT_NAME FEAT_VENDOR FEAT_VERSION EXP_DATE NUM_LIC [FEAT_OPTIONAL*]
    
    FEAT_NAME: NON_WHITESPACE+
    FEAT_VENDOR: NON_WHITESPACE+
    FEAT_VERSION: NON_WHITESPACE+
    EXP_DATE: NON_WHITESPACE+
    NUM_LIC: NON_WHITESPACE+
    FEAT_OPTIONAL: NON_WHITESPACE+
    
    WS: /[ \t\f\r]+/
    NON_WHITESPACE: /\S+/
    
    LINE_CONTINUATION: /\\[ \t\f\r]*\n/ [WS]
    
    %ignore WS
    %ignore LINE_CONTINUATION
    
    %import common.NEWLINE
    %import common.WORD
    %import common.INT
"""

#TODO: Write+Test lexer that generate a direct usable "config_file" object
config_parser = Lark(config_grammar, parser="lalr")
#TODO: rename "parse" in something more unique
parse = config_parser.parse


if __name__ == '__main__':
    pass
