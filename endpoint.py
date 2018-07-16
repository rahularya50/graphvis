# coding=utf-8

import compile
import execute
import parse

PROGRAM = '''
T
forall T {
    newgraph
    edges
    VERTICES
}
forall T {
    forall edges {
        <a, ENDPOINT+1> <b, ENDPOINT+1>
    }
}
'''

STRING = '''
2
3
6
4
14

1 2
3 4
5 6

7 8
9 10
11 12
13 14
'''


def get_vertices(graph: execute.Graph) -> dict:
    ...


def get_graph(program: str = PROGRAM, string: str = STRING) -> dict:
    parse_tree = parse.parse(program)
    ast = compile.compile_tree(parse_tree)
    data = execute.Execute(ast, string).get_data()

    vertices = get_vertices(data.values["newgraph"])
