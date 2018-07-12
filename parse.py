# coding=utf-8

GRAMMAR = '''
GOAL = STATEMENTS
STATEMENTS = [STATEMENT]
STATEMENT = INITIALIZER | HINT | LOOP | TOKEN
TOKEN = VALUE | "<" EXPRESSION_LIST ">"
EXPRESSION_LIST = [EXPRESSION, ","]
HINT = "(" EXPRESSION "=" EXPRESSION ")" | "(" EXPRESSION_LIST ")"
LOOP = "forall" VALUE "{" STATEMENTS "}"
EXPRESSION = SECOND_EXPRESSION FIRST_OPERATOR EXPRESSION | SECOND_EXPRESSION
SECOND_EXPRESSION = SINGLETON SECOND_OPERATOR SECOND_EXPRESSION | SINGLETON
SINGLETON = "(" EXPRESSION ")" | VALUE
@FIRST_OPERATOR = "+"|"-"
@SECOND_OPERATOR = "*"|"/"
@INITIALIZER = "newgraph"
VALUE = <WORD>
'''


class WhiteSpace:
    def __init__(self):
        pass

    def __repr__(self):
        return "whitespace"


class OneOf:
    def __init__(self, *possibilities, hold_literals):
        self.possibilities = possibilities
        self.hold_literals = hold_literals

    def __repr__(self):
        return "OneOf(" + ", ".join(str(x) for x in self.possibilities) + ")"


class AllOf:
    def __init__(self, *elements):
        self.elements = elements

    def __repr__(self):
        return "AllOf(" + ", ".join(str(x) for x in self.elements) + ")"


class Value:
    def __init__(self):
        pass

    def __repr__(self):
        return "value"


class Array:
    def __init__(self, element, delim=None, hold_literals=False):
        self.element = element
        self.delim = delim
        self.hold_literals = hold_literals

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

    def __repr__(self, indent=0):
        if self.value:
            return " " * indent + self.type + ": " + self.value
        out = " " * indent + self.type + ": [\n"
        next_indent = indent + 1
        if len(self.children) > 1:
            next_indent += 2
        for x in self.children:
            if type(x) is ParseNode:
                out += x.__repr__(next_indent)
            else:
                out += str(x)
            out += ", \n"
        out += " " * indent + "]"
        return out


def build_proc_grammar(raw_grammar):
    proc_grammar = {}
    lines = raw_grammar.split("\n")

    for line in lines:
        if not line:
            continue
        exp = line.split(" = ")[0]
        seq = line.split(" = ")[1]
        hold_literals = False
        if exp[0] == "@":
            hold_literals = True
            exp = exp[1:]
        if seq[0] == '[':
            if len(seq[1:-1].split(",")) == 1:
                proc_grammar[exp] = Array(seq[1:-1], hold_literals=hold_literals)
            else:
                seq, delim = seq[1:-1].split(",", 1)
                delim = delim.strip()
                delim = delim[1:-1]
                proc_grammar[exp] = Array(seq, delim)
        else:
            possibilities = []
            curr_possibility = []
            curr_elem = ""
            in_literal = False
            in_special = False
            for x in seq:
                if in_special:
                    if x == ">":
                        curr_possibility.append(Value())
                        curr_elem = ""
                        in_special = False
                    else:
                        curr_elem += x
                elif x == "\"":
                    if in_literal:
                        if curr_elem:
                            curr_possibility.append(Literal(curr_elem))
                        in_literal = False
                        curr_elem = ""
                    else:
                        if curr_elem:
                            curr_possibility.append(curr_elem)
                        in_literal = True
                        curr_elem = ""
                elif in_literal:
                    curr_elem += x
                elif x == "<":
                    if curr_elem:
                        curr_possibility.append(curr_elem)
                    curr_elem = ""
                    in_special = True
                elif x == " ":
                    if curr_elem:
                        curr_possibility.append(curr_elem)
                    curr_possibility.append(WhiteSpace())
                    curr_elem = ""
                elif x == "|":
                    if curr_elem:
                        curr_possibility.append(curr_elem)
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
            proc_grammar[exp] = OneOf(*possibilities, hold_literals=hold_literals)
    return proc_grammar


def build_parse_tree(S, proc_grammar):
    return match("GOAL", S, proc_grammar)


def match_array(goal, S, grammar, i):
    element = grammar[goal].element
    delim = grammar[goal].delim
    if not match(element, S, grammar, i):
        return None
    out = ParseNode(goal)
    while True:
        x = match(element, S, grammar, i)
        if not x:
            return out, i
        out.addChild(x[0])
        i = x[1]
        if delim:
            if S[i:i+len(delim)] != delim:
                return out, i
            i += len(delim)
        while i != len(S) and S[i].isspace():
            i += 1


def match(goal, S, grammar, i=0):
    if type(grammar[goal]) is Array:
        return match_array(goal, S, grammar, i)
    for possibility in grammar[goal].possibilities:
        pos = i
        out = ParseNode(goal)
        fail = False
        for element in possibility.elements:
            if isinstance(element, Literal):
                if S[pos:pos+len(element.value)] != element.value:
                    fail = True
                    break
                pos += len(element.value)
                if grammar[goal].hold_literals:
                    out.addChild(ParseNode("LITERAL", element.value))
            elif isinstance(element, WhiteSpace):
                while pos != len(S) and S[pos].isspace():
                    pos += 1
            elif isinstance(element, Value):
                curr = ""
                while pos != len(S) and S[pos].isalnum():
                    curr += S[pos]
                    pos += 1
                if not curr:
                    fail = True
                    break
                out.addChild(ParseNode("<WORD>", curr))
            else:
                x = match(element, S, grammar, pos)
                if not x:
                    fail = True
                    break
                out.addChild(x[0])
                pos = x[1]
        if not fail:
            return out, pos
    return None


def parse(S, proc_grammar=None):
    if proc_grammar is None:
        proc_grammar = build_proc_grammar(GRAMMAR)
    return match("GOAL", S, proc_grammar)[0]
