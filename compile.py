# coding=utf-8


class Loop:
    def __init__(self, loopvar, statements):
        self.loopvar = loopvar
        self.statements = list(statements)

    def __repr__(self):
        out = "forall (" + str(self.loopvar) + ")" + "{\n"
        for s in self.statements:
            out += str(s) + "\n"
        out += "} "
        return out


class Hint:
    def __init__(self, expression_list):
        self.expression_list = list(expression_list)

    def __repr__(self):
        return "(" + ", ".join(str(x) for x in self.expression_list) + ") "


class Token:
    def __init__(self, expression_list):
        self.expression_list = list(expression_list)

    def __repr__(self):
        return "<" + ", ".join(str(x) for x in self.expression_list) + "> "


class MathExpression:
    def __init__(self, lhs, op, rhs):
        self.lhs = lhs
        self.op = op
        self.rhs = rhs

    def __repr__(self):
        return "(" + str(self.lhs) + " " + str(self.op) + " " + str(self.rhs) + ")"


class Variable:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name


class Constant:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return str(self.value)


class Operator:
    def __init__(self, operator):
        self.operator = operator

    def __repr__(self):
        return self.operator


def compile_ast(ast):
    statements = ast.children[0]
    return compile_statement_list(statements)


def compile_statement_list(statement_list):
    out = []
    for statement in statement_list.children:
        out.append(compile_statement(statement))
    return out


def compile_statement(statement):
    obj = statement.children[0]
    if obj.type == "HINT":
        if obj.children[0].type == "EXPRESSION_LIST":
            return Hint(compile_expression(exp) for exp in obj.children[0].children)
        else:
            return Hint(compile_expression(x) for x in obj.children)
    elif obj.type == "LOOP":
        return Loop(compile_expression(obj.children[0]), compile_statement_list(obj.children[1]))
    elif obj.type == "TOKEN":
        if obj.children[0].type == "EXPRESSION_LIST":
            return Token(compile_expression(exp) for exp in obj.children[0].children)
        else:
            return Token((compile_expression(obj.children[0]),))
    else:
        raise Exception("Statement type unknown!", obj.type)


def compile_expression(expression):
    if expression.type == "<WORD>":
        if expression.value.isnumeric():
            return Constant(int(expression.value))
        else:
            return Variable(expression.value)
    if len(expression.children) == 1:
        return compile_expression(expression.children[0])
    else:
        lhs, op, rhs = expression.children
        return MathExpression(compile_expression(lhs), compile_operator(op), compile_expression(rhs))


def compile_operator(operator):
    return Operator(operator.children[0].value)
