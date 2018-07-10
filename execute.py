# coding=utf-8

import compile


def execute(ast, S):
    variables = {}
    run_commands(ast, S, 0, variables)


def run_commands(commands, S, pos, variables, write_to):
    for command in commands:
        if type(command) is compile.Token:
            ...
        elif type(command) is compile.Hint:
            ...
        elif type(command) is compile.Loop:
            cnt = evaluate_expression(command.loopvar, variables)
            if type(command.loopvar) is compile.Variable:
                name = command.loopvar.name
                if name not in write_to:
                    write_to[name] = (None, [])
                active = write_to[name][1]
            else:
                active = []
            for i in range(cnt):
                pos = run_commands
        else:
            raise Exception("Command type unknown!", type(command))
