# -*- coding: utf-8 -*-

from lark import Lark, Transformer, v_args
config_grammar = r"""
    start: config

    config: _EMPTY_LINE* | comments
    
    _EMPTY_LINE: /^/ WS* NEWLINE
    
    COMMENT: /#.*/ NEWLINE
    comments: COMMENT*
    
    %ignore NEWLINE
    
    %import common.WS
    %import common.NEWLINE
"""



config_parser = Lark(config_grammar)
parse = config_parser.parse


if __name__ == '__main__':
    pass
