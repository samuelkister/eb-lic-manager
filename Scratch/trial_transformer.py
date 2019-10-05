from lark import Transformer, Lark

import eb_lic_manager.flex_lm.config_file_reader as p


class TreeToJson(Transformer):
    def server(self, child):
        print("SERVER: ")
        print(child)

    def vendor(self, child):
        print("VENDOR: ")
        print(child)

    def feature(self, child):
        print("FEATURE: ")
        print(child)

    def feat_optional(self, child):
        print("FEATURE OPTIONAL: ")
        print(child)
        return "Feature optional"


if __name__ == '__main__':
    config_parser = Lark(p.config_grammar, parser='lalr', start='config', transformer=TreeToJson())
    parse = config_parser.parse

    with open("../Samples/aucotec.lic") as f:
        tree = parse(f.read())
        print()
        print(tree)

