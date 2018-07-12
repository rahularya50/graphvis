# coding=utf-8

import compile
import parse


class Variable:
    def __init__(self, name, ancestors):
        self.ancestors = ancestors
        self.children = set()
        self.values = {}
        self.name = name

    def __repr__(self):
        return self.name + ": " + str(self.values)


class Root:
    def __init__(self):
        self.children = set()
        self.values = dict()

    def __repr__(self):
        return str(self.values)


def execute(ast, S):
    root = Root()
    run_commands(ast, S.strip(), 0, dict(), {}, root)
    print(root)


def run_commands(commands, S, i, values, loopcnts, root):
    for command in commands:
        if isinstance(command, compile.Initializer):
            if command.name == "newgraph":
                ...
            else:
                raise Exception("Unknown initializer!", command.name)

        if isinstance(command, compile.Token):
            T = ""
            while i != len(S) and not S[i].isspace():
                T += S[i]
                i += 1
            while i != len(S) and S[i].isspace():
                i += 1
            for expression in command.expression_list:
                assign_expression(expression, T, values, loopcnts, root)

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
                    assign_expression(expression, T, loopcnts, values, root)

        elif type(command) is compile.Loop:
            loopvar = command.loopvar.name
            cnt = values[loopvar]
            if loopvar in loopcnts:
                raise Exception("Loop variable already defined!", command.loopvar)
            loopcnts[loopvar] = 0
            for _ in range(int(cnt)):
                for child_name in root.values[loopvar].children:
                    ok = True
                    child = root.values[child_name]
                    for ancestor in child.ancestors:
                        if ancestor not in loopcnts:
                            ok = False
                            break
                    if ok:
                        key = tuple()
                        for ancestor in child.ancestors:
                            key = key + (loopcnts[ancestor],)
                        if key in child.values:
                            values[child_name] = child.values[key]
                i = run_commands(command.statements, S, i, values, loopcnts, root)
                loopcnts[loopvar] += 1
                to_remove = []
                for value in values:
                    if loopvar in root.values[value].ancestors:
                        to_remove.append(value)
                for value in to_remove:
                    del values[value]
            del loopcnts[loopvar]
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


def assign_expression(expression, curr_val, values, loopcnts, root):
    if isinstance(expression, compile.Constant):
        raise Exception("Unable to assign to constant!")
    elif isinstance(expression, compile.Variable):
        name = expression.name
        if name in values:
            raise Exception("Variable name already defined!", name)
        if name not in root.values:
            root.values[name] = Variable(name, sorted(loopcnts))
        key = tuple()
        for loopvar in sorted(loopcnts):
            root.values[loopvar].children.add(name)
            key = key + (loopcnts[loopvar],)
        root.values[name].values[key] = curr_val
        values[name] = curr_val

    elif isinstance(expression, compile.MathExpression):
        a = get_value(expression.lhs, values)
        b = get_value(expression.rhs, values)
        if a is None and b is None:
            raise Exception("Both sides of an arithmetic expression are indeterminate!", expression)
        elif a is not None and b is not None:
            raise Exception("Expression already fully defined!")
        else:
            if b is None:
                assign_expression(expression.rhs, expression.operator.get_rhs(int(a), int(curr_val)), values, loopcnts,
                                  root)
            else:
                assign_expression(expression.lhs, expression.operator.get_lhs(int(b), int(curr_val)), values, loopcnts,
                                  root)


execute(compile.compile_tree(parse.parse('''
A
newgraph
forall A {
    N
}
forall A {
    forall N {
        M
    }
}
''')), '''
3
2 3 4
1 2
3 4 5
6 7 8 9
''')
