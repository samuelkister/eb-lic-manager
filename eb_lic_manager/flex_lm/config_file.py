# -*- coding: utf-8 -*-

from lark import Lark, Transformer, v_args
config_grammar = r"""
    start: config

    config: _EMPTY_LINE* | comments server
    
    _EMPTY_LINE: /^/ WS* NEWLINE
    
    COMMENT: /#.*/ NEWLINE
    comments: COMMENT*
    
    server: "SERVER "i server_name server_id server_port NEWLINE
    server_name: /(\w)+/
    server_id: /(\w)+/
    server_port: INT
    
    %ignore NEWLINE
    %ignore WS
    
    %import common.WS
    %import common.NEWLINE
    %import common.WORD
    %import common.INT
"""



config_parser = Lark(config_grammar)
parse = config_parser.parse


if __name__ == '__main__':
    pass
