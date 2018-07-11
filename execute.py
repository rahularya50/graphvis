# coding=utf-8

import compile


class Variable:
    def __init__(self, name, ancestors):
        self.ancestors = ancestors
        self.children = []
        self.values = {}
        self.name = name


class Root:
    def __init__(self):
        self.children = set()
        self.values = dict()


def execute(ast, S):
    root = Root()
    run_commands(ast, S, 0, set(), dict(), root)


def run_commands(commands, S, i, actives, values, root):
    for command in commands:
        if isinstance(command, compile.Token):
            T = ""
            while i != len(S) and not S[i].isspace():
                T += S[i]
                i += 1
            while i != len(S) and S[i].isspace():
                i += 1
            for expression in command.expression_list:
                assign_expression(expression, T, actives, values, root)

        elif type(command) is compile.Hint:
            T = None
            for expression in command.expression_list:
                if get_value(expression, values) is not None:
                    T = get_value(expression, values)
                    break
            if T is None:
                raise Exception("Value hint is indeterminate!")
            for expression in command.expression_list:
                if get_value(expression, values) is None:
                    assign_expression(expression, T, actives, values)

        elif type(command) is compile.Loop:
            cnt = values[command.loopvar]
            if command.loopvar in actives:
                raise Exception("Loop variable already defined!", command.loopvar)
            actives.add(command.loopvar)
            # TODO: Add reaectivated variables to *actives*!
            for i in range(cnt):
                i = run_commands(command.commands, S, i, actives, values, root)
            actives.remove(command.loopvar)
        else:
            raise Exception("Command type unknown!", type(command))

    return i


def get_value(expression, values):
    if isinstance(expression, compile.Constant):
        return expression.value
    elif isinstance(expression, compile.Variable):
        if expression.name in values:
            return values[expression.name]
        else:
            return None
    elif isinstance(expression, compile.MathExpression):
        a = get_value(expression.lhs, values)
        b = get_value(expression.rhs, values)
        if a is None or b is None:
            return None
        return expression.operator.execute(int(a), int(b))
    else:
        raise Exception("Expression type unknown!")


def assign_expression(expression, curr_val, actives, values, root):
    if isinstance(expression, compile.Constant):
        raise Exception("Unable to assign to constant!")
    elif isinstance(expression, compile.Variable):
        name = expression.name
        if name in values:
            raise Exception("Variable name already defined!", name)
        if name not in root.values:
            root.values[name] = Variable(name, sorted(actives))
        prev = root.values
        curr = root.values[name]
        for active in actives:
            if active not in curr:
                prev, curr = curr, curr[values[active]]
            curr = curr[values[active]]
        prev[values[actives[-1]]] = curr_val

    elif isinstance(expression, compile.MathExpression):
        a = get_value(expression.lhs, values)
        b = get_value(expression.rhs, values)
        if a is None and b is None:
            raise Exception("Both sides of an arithmetic expression are indeterminate!", expression)
        elif a is not None and b is not None:
            raise Exception("Expression already fully defined!")
        else:
            if a is None:
                assign_expression(expression.rhs, expression.operator.get_rhs(a, curr_val), actives, values, root)
            else:
                assign_expression(expression.lhs, expression.operator.get_lhs(b, curr_val), actives, values, root)
