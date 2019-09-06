# -*- coding: utf-8 -*-

from lark import Lark, Transformer, v_args
config_grammar = r"""
    start: config_file

    config_file: (FEATURE | ANYTHING)*

    FEATURE: "FEATURE" /[^\n]*/
    feature: FEATURE
    
    something_else: ANYTHING
    
    ANYTHING: /.[^\n]*/
    
    %ignore WS
    %ignore / \\[\t \f]*\r?\n/   // LINE_CONT
    
    %import common.WS
    %import common.NEWLINE
    %import common.WORD
    %import common.INT
"""


config_parser = Lark(config_grammar)
parse = config_parser.parse


if __name__ == '__main__':
    pass
