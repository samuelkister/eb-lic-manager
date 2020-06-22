# -*- coding: utf-8 -*-
import abc
import re
from typing import Any

from lark import Lark, Transformer, Tree

"""
All classes and functions needed to read and transform a flex-LM config file
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


def parse(text: str) -> Tree:
    """
    Parse the content of a config file

    :param text: the content of the config file as a string
    :return: A lark Tree
    """

    # Remove all line continuation from the original
    text = re.sub(r"\s*\\\s*", " ", text, flags=re.MULTILINE)

    config_parser = Lark(config_grammar, parser='lalr', start='config')

    return config_parser.parse(text)


class AbstractConfigFactory(abc.ABC):
    """
    Class to construct a FlexLM configuration object.
    """

    @abc.abstractmethod
    def get_config(self):
        """
        Return the constructed configuration object.

        :return: the constructed configuration object
        :rtype: FlexLm Configuration Object
        """

        return "Not implemented"

    @abc.abstractmethod
    def add_new_server(self, *args, **kwargs) -> None:
        """
        Add a new server to the configuration, created with the given parameters.

        :param args: The server values
        :type args: Any
        :param kwargs: The server named values
        :type kwargs: Any
        :return: None
        :rtype: None
        """

        return "Not implemented"


class ConfigTransformer(Transformer):
    """
    Convert the lark tree of a parsed config file to a config object
    """

    def __init__(self, config_factory: AbstractConfigFactory):

        super().__init__()
        self._config_factory = config_factory

    def get_config(self):
        """
        Get the constructed configuration object

        :returns the constructed configuration object
        """
        self._config_factory.get_config()

    def parameter(self, children) -> Any:
        """
        Transform a tree children into one value (if no "KEY" is present) or tuple of (key, value).
        "STRING": quotation marks are removed -> string
        "NON_STRING": stay string
        "KEY": key part of the tuple (key, value) -> string

        :param children: Lark Node defining a parameter in the config file
        :type children: Node
        :return: (key, value) if "KEY" is present else value
        :rtype: string or tuple
        """

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

    def server(self, children) -> Any:
        """
        Transmit the decoded parameters of a SERVER line to the factory in order to have a
        Server object generated in the FlexLmConfig object.

        :param children: list of parameters
        :type children: list of values and/or tuples (key, value)
        :return: The value returned by the config factory
        :rtype: Any
        """

        args, named_args = self.build_args_from_list(children)

        return self._config_factory.add_new_server(*args, **named_args)

    def build_args_from_list(self, arguments) -> tuple:
        """
        Check the passed list of arguments to avoid single values after named values
        and return a tuple of (list of single values, dictionary of named values)

        :param arguments: list of values and tuple (key, value)
        :type arguments: list
        :return: (list of single values, dictionary of named values)
        :rtype: tuple(list, dict)
        """

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
