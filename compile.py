# coding=utf-8
from __future__ import annotations

from typing import Union, NewType, List, Iterable

import parse


class Loop:
    def __init__(self, loopvar: int, statements: List[Statement]) -> None:
        self.loopvar = loopvar
        self.statements = list(statements)

    def __repr__(self) -> str:
        out = "forall (" + str(self.loopvar) + ")" + "{\n"
        for s in self.statements:
            out += str(s) + "\n"
        out += "} "
        return out


class Hint:
    def __init__(self, expression_list: Iterable[Expression]) -> None:
        self.expression_list = list(expression_list)

    def __repr__(self) -> str:
        return "(" + ", ".join(str(x) for x in self.expression_list) + ") "


class Token:
    def __init__(self, expression_list: Iterable[Expression]) -> None:
        self.expression_list = list(expression_list)

    def __repr__(self) -> str:
        return "<" + ", ".join(str(x) for x in self.expression_list) + "> "


class Initializer:
    def __init__(self, type: ObjType, name: VarName = "") -> None:
        self.type = type
        self.name = name

    def __repr__(self) -> str:
        return str(self.type) + "(" + str(self.name) + ")"


class MathExpression:
    def __init__(self, lhs: Expression, op: Operator, rhs: Expression) -> None:
        self.lhs = lhs
        self.operator = op
        self.rhs = rhs

    def __repr__(self) -> str:
        return "(" + str(self.lhs) + " " + str(self.operator) + " " + str(self.rhs) + ")"


class Variable:
    def __init__(self, name: VarName) -> None:
        self.name = name

    def __repr__(self) -> str:
        return self.name


class Keyword:
    def __init__(self, name: str) -> None:
        self.name = name

    def __repr__(self) -> str:
        return self.name


class Constant:
    def __init__(self, value: int) -> None:
        self.value = value

    def __repr__(self) -> str:
        return str(self.value)


class Operator:
    def __init__(self, operator: str) -> None:
        self.operator = operator

    def __repr__(self) -> str:
        return self.operator

    def execute(self, lhs: int, rhs: int) -> int:
        if self.operator == "*":
            return lhs * rhs
        elif self.operator == "/":
            return lhs // rhs
        elif self.operator == "+":
            return lhs + rhs
        elif self.operator == "-":
            return lhs - rhs
        else:
            raise Exception("Unknown operator :(", self.operator)

    def get_rhs(self, lhs: int, result: int) -> int:
        if self.operator == "*":
            return result // lhs
        elif self.operator == "/":
            return lhs // result
        elif self.operator == "+":
            return result - lhs
        elif self.operator == "-":
            return lhs - result
        else:
            raise Exception("Unknown operator :(", self.operator)

    def get_lhs(self, rhs: int, result: int) -> int:
        if self.operator == "*":
            return result // rhs
        elif self.operator == "/":
            return result * rhs
        elif self.operator == "+":
            return result - rhs
        elif self.operator == "-":
            return result + rhs
        else:
            raise Exception("Unknown operator :(", self.operator)


Statement = Union[Initializer, Loop, Hint, Token]
Expression = Union[Keyword, MathExpression, Variable, Constant]
VarName = NewType("VarName", str)
ObjType = NewType("ObjType", str)


def compile_tree(parse_tree: parse.ParseNode) -> List[Statement]:
    statements = parse_tree.children[0]
    return compile_statement_list(statements)


def compile_statement_list(statement_list: parse.ParseNode) -> List[Statement]:
    out = []
    for statement in statement_list.children:
        out.append(compile_statement(statement))
    # print(out)
    return out


def compile_statement(statement: parse.ParseNode) -> Statement:
    obj = statement.children[0]
    if obj.type == "INITIALIZER":
        return Initializer(obj.children[0].value)
    elif obj.type == "HINT":
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


def compile_expression(expression: parse.ParseNode) -> Expression:
    if expression.type == "KEYWORD":
        return Keyword(expression.children[0].value)
    elif expression.type == "<WORD>":
        if expression.value.isnumeric():
            return Constant(int(expression.value))
        else:
            return Variable(expression.value)
    if len(expression.children) == 1:
        return compile_expression(expression.children[0])
    else:
        lhs, op, rhs = expression.children
        return MathExpression(compile_expression(lhs), compile_operator(op), compile_expression(rhs))


def compile_operator(operator: parse.ParseNode) -> Operator:
    return Operator(operator.children[0].value)
