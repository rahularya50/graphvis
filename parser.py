# coding=utf-8

grammar = '''
GOAL = STATEMENTS
STATEMENTS = [STATEMENT]
STATEMENT = TOKEN|HINT|LOOP|CONDITIONAL
TOKEN = EXPRESSION|"<"EXPRESSION_LIST">"
EXPRESSION_LIST = [EXPRESSION, ","]
HINT = "(" EXPRESSION "=" EXPRESSION ")"|"(" EXPRESSION_LIST ")"
LOOP = "forall" EXPRESSION "{" STATEMENTS "}"
EXPRESSION = RAW_TOKEN|EXPRESSION OPERATOR EXPRESSION|"(" EXPRESSION ")"
OPERATOR = "+"|"-"|"*"|"/"
RAW_TOKEN = "VERTICES"|"EDGES"|LITERAL
'''


class WhiteSpace:
    def __init__(self):
        pass

    def __repr__(self):
        return "whitespace"


class OneOf:
    def __init__(self, *possibilities):
        self.possibilities = possibilities

    def __repr__(self):
        return "OneOf(" + ", ".join(str(x) for x in self.possibilities) + ")"


class AllOf:
    def __init__(self, *elements):
        self.elements = elements

    def __repr__(self):
        return "AllOf(" + ", ".join(str(x) for x in self.elements) + ")"


class Array:
    def __init__(self, *element, delim=WhiteSpace()):
        self.element = element
        self.delim = delim

    def __repr__(self):
        return "Array(" + str(self.element) + ", " + str(self.delim) + ")"


class Literal:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "Literal(" + str(self.value) + ")"


class ParseNode:
    def __init__(self, type, value=None):
        self.type = type
        self.value = value
        self.children = []

    def addChild(self, node):
        self.children.append(node)


def build_proc_grammar(raw_grammar):
    proc_grammar = {}
    lines = raw_grammar.split("\n")

    for line in lines:
        if not line:
            continue
        exp = line.split(" = ")[0]
        seq = line.split(" = ")[1]
        if seq[0] == '[':
            if len(seq[1:-1].split(",")) == 1:
                proc_grammar[exp] = Array(seq[1:-1])
            else:
                seq, delim = seq[1:-1].split(",", 1)
                delim.strip()
                if delim[0] == "\"":
                    delim = Literal(delim[1:-1])
                proc_grammar[exp] = Array(seq, delim)
        else:
            possibilities = []
            curr_possibility = []
            curr_elem = ""
            inLiteral = False
            for x in seq:
                if x == "\"":
                    if inLiteral:
                        if curr_elem:
                            curr_possibility.append(Literal(curr_elem))
                        inLiteral = False
                        curr_elem = ""
                    else:
                        if curr_elem:
                            curr_possibility.append(curr_elem)
                        inLiteral = True
                        curr_elem = ""
                elif inLiteral:
                    curr_elem += x
                elif x == " ":
                    if curr_elem:
                        curr_possibility.append(curr_elem)
                    curr_possibility.append(WhiteSpace())
                    curr_elem = ""
                elif x == "|":
                    if curr_possibility:
                        possibilities.append(AllOf(*curr_possibility))
                    curr_possibility = []
                    curr_elem = ""
                else:
                    curr_elem += x
            if curr_elem:
                curr_possibility.append(curr_elem)
            if curr_possibility:
                possibilities.append(AllOf(*curr_possibility))
            proc_grammar[exp] = OneOf(*possibilities)
    return proc_grammar


def build_parse_tree(S, proc_grammar):
    return match("GOAL", S, proc_grammar, 0)


def match(goal, S, grammar, i):
    if grammar[goal] is Array:
        return match_array(goal, S, grammar, i)
    for possibility in grammar[goal].possibilities:
        pos = i
        for element in possibility.elements:
            if element is Literal:
                pass
            elif element is WhiteSpace:
                pass
            else:


proc_grammar = build_proc_grammar(grammar)
print("\n".join(str(x) for x in proc_grammar.items()))
