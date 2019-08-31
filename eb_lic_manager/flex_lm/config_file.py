# -*- coding: utf-8 -*-

from lark import Lark, Transformer, v_args
config_grammar = r"""
    start: _EMPTY_LINE* | _COMMENT*
    
    _EMPTY_LINE: /^[\t ]*\n/
    
    _COMMENT: "#" /[^\n]*/
    
    %ignore _EMPTY_LINE
    %ignore _COMMENT
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
