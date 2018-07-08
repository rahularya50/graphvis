# coding=utf-8


class Parser:
    def __init__(self, S):
        self.S = S

    def get_goal(self, i):
        x = self.is_statements(i)
        if x:
            return x
        return None

    def get_statements(self, i):
        x = self.get_statement(i)
        if not x:
            return None
        statements = ParseNode("statements")
        statements.addChild(x[0])
        i = x[1]
        while True:
            x = self.get_statement(i)
            if not x:
                return statements, i
            statements.addChild(x[0])
            i = x[1]

    def get_statement(self, i):
        x = self.get_loop(i)
        if x:
            return x
        x = self.get_hint(i)
        if x:
            return x
        x = self.get_token(i)
        if x:
            return x
        return None

    def get_token(self, i):
        x = self.get_expression_list(i)



class ParseNode:
    def __init__(self, type, value=None):
        self.type = type
        self.value = value
        self.children = []

    def addChild(self, node):
        self.children.append(node)
