# -*- coding: utf-8 -*-

from lark import Lark

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
#TODO: in string /.+/ is also catching the "\" of a line continuation. Find right regex

#TODO: Write+Test transformer that generate a direct usable "config_file" object
config_parser = Lark(config_grammar, parser='lalr', start='config')
#TODO: rename "parse" in something more unique
parse = config_parser.parse


if __name__ == '__main__':
    pass
