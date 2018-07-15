# coding=utf-8

import compile
import parse

GRAPH_NAME = "newgraph"
VERTEX_COUNT = "VERTICES"
EDGE_COUNT = "EDGES"


class Variable:
    def __init__(self, name, ancestors):
        self.ancestors = ancestors
        self.children = set()
        self.values = {}
        self.name = name

    def __repr__(self):
        return self.name + ": " + str(self.values)


class Graph:
    def __init__(self):
        self.directed = False
        self.vertices = []
        self.edges = []
        self.nextEdge = None

    def add_endpoint(self, endpoint, loopcnts):
        if self.nextEdge is None:
            self.nextEdge = Edge(endpoint, None, loopcnts)
        else:
            self.nextEdge.b = endpoint
            self.edges.append(self.nextEdge)
            self.nextEdge = None

    def add_vertex(self, vertex, loopcnts):
        self.vertices.append(Vertex(vertex, loopcnts))

    def set_vertices(self, vertices, loopcnts):
        if self.vertices:
            raise Exception("Vertices have already been added")
        for i in range(vertices):
            self.vertices.append(Vertex(i, loopcnts))
            self.vertices[-1].dependencies[VERTEX_COUNT] = i

    def __repr__(self):
        return "Vertices = " + str(self.vertices) + ", Edges = " + str(self.edges)


class Vertex:
    def __init__(self, index, loopcnts):
        self.id = index
        self.dependencies = loopcnts.copy()

    def __repr__(self):
        return str(self.id)


class Edge:
    def __init__(self, a, b, loopcnts):
        self.a = a
        self.b = b
        self.dependencies = loopcnts.copy()

    def __repr__(self):
        return "(" + str(self.a) + ", " + str(self.b) + ")"


class Root:
    def __init__(self):
        self.children = set()
        self.values = dict()

    def __repr__(self):
        return "\n".join(str(self.values[x]) for x in self.values)


class Main:
    def __init__(self, ast, S):
        self.values = {}
        self.loopcnts = {}
        self.root = Root()
        self.S = S.strip()
        self.i = 0
        print(ast)
        self.run_commands(ast)
        print(self.root)

    def get_data(self):
        return self.root

    def run_commands(self, commands):
        for command in commands:
            if isinstance(command, compile.Initializer):
                if command.type == "newgraph":
                    if GRAPH_NAME in self.values:
                        raise Exception("Attempting to initialize graph when one already exists!")
                    self.store(GRAPH_NAME, Graph())
                else:
                    raise Exception("Unknown initializer!", command.type)

            elif isinstance(command, compile.Token):
                T = ""
                while self.i != len(self.S) and not self.S[self.i].isspace():
                    T += self.S[self.i]
                    self.i += 1
                while self.i != len(self.S) and self.S[self.i].isspace():
                    self.i += 1
                for expression in command.expression_list:
                    self.assign_expression(expression, T)

            elif isinstance(command, compile.Hint):
                T = None
                for expression in command.expression_list:
                    if self.get_value(expression) is not None:
                        T = self.get_value(expression)
                        break
                if T is None:
                    raise Exception("Value hint is indeterminate!")
                for expression in command.expression_list:
                    if self.get_value(expression) is None:
                        self.assign_expression(expression, T)

            elif isinstance(command, compile.Loop):
                loopvar = command.loopvar.name
                cnt = self.values[loopvar]
                if loopvar in self.loopcnts:
                    raise Exception("Loop variable already defined!", command.loopvar)
                self.loopcnts[loopvar] = 0
                for _ in range(int(cnt)):
                    for child_name in self.root.values[loopvar].children:
                        ok = True
                        child = self.root.values[child_name]
                        for ancestor in child.ancestors:
                            if ancestor not in self.loopcnts:
                                ok = False
                                break
                        if ok:
                            key = tuple()
                            for ancestor in child.ancestors:
                                key = key + (self.loopcnts[ancestor],)
                            if key in child.values:
                                self.values[child_name] = child.values[key]
                    self.run_commands(command.statements)
                    self.loopcnts[loopvar] += 1
                    to_remove = []
                    for value in self.values:
                        if loopvar in self.root.values[value].ancestors:
                            to_remove.append(value)
                    for value in to_remove:
                        del self.values[value]
                del self.loopcnts[loopvar]
            else:
                raise Exception("Command type unknown!", type(command))

    def get_value(self, expression):
        if isinstance(expression, compile.Constant):
            return expression.value
        elif isinstance(expression, compile.Variable):
            if expression.name in self.values:
                return self.values[expression.name]
            else:
                return None
        elif isinstance(expression, compile.MathExpression):
            a = self.get_value(expression.lhs)
            b = self.get_value(expression.rhs)
            if a is None or b is None:
                return None
            return expression.operator.execute(int(a), int(b))
        elif isinstance(expression, compile.Keyword):
            return None
        #            raise Exception("Unable to access value of keyword, please provide quantity with a unique identifier.")
        else:
            raise Exception("Expression type unknown!", type(expression), expression)

    def assign_expression(self, expression, curr_val):
        print("Assigning", curr_val, "to", expression, "under loops", self.loopcnts)
        if isinstance(expression, compile.Constant):
            raise Exception("Unable to assign to constant!")

        elif isinstance(expression, compile.Variable):
            self.store(expression.name, curr_val)

        elif isinstance(expression, compile.MathExpression):
            a = self.get_value(expression.lhs)
            b = self.get_value(expression.rhs)
            if a is None and b is None:
                raise Exception("Both sides of an arithmetic expression are indeterminate!", expression)
            elif a is not None and b is not None:
                raise Exception("Expression already fully defined!")
            else:
                if b is None:
                    self.assign_expression(expression.rhs, expression.operator.get_rhs(int(a), int(curr_val)))
                else:
                    self.assign_expression(expression.lhs, expression.operator.get_lhs(int(b), int(curr_val)))

        elif isinstance(expression, compile.Keyword):
            # decode keyword, access + store in graph!
            if expression.name == "ENDPOINT":
                if GRAPH_NAME not in self.values:
                    raise Exception("Graph not yet initialized!")
                self.values[GRAPH_NAME].add_endpoint(curr_val, self.loopcnts)
            elif expression.name == "VERTEX":
                if GRAPH_NAME not in self.values:
                    raise Exception("Graph not yet initialized!")
                self.values[GRAPH_NAME].add_vertex(curr_val, self.loopcnts)
            elif expression.name == "VERTICES":
                if GRAPH_NAME not in self.values:
                    raise Exception("Graph not yet initialized!")
                self.values[GRAPH_NAME].set_vertices(int(curr_val), self.loopcnts)
            elif expression.name == "HEAD":
                raise Exception("Directed graphs not yet supported!")
            elif expression.name == "TAIL":
                raise Exception("Directed graphs not yet supported!")
            else:
                raise Exception("Keyword type unknown!")
        else:
            raise Exception("Expression type unknown!", expression, type(expression))

    def store(self, name, value):
        if name in self.values:
            raise Exception("Variable name already defined!", name)
        if name not in self.root.values:
            self.root.values[name] = Variable(name, sorted(self.loopcnts))
        key = tuple()
        for loopvar in sorted(self.loopcnts):
            self.root.values[loopvar].children.add(name)
            key = key + (self.loopcnts[loopvar],)
        self.root.values[name].values[key] = value
        self.values[name] = value


print(Main(compile.compile_tree(parse.parse('''
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
''')), '''
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
''').get_data().values["newgraph"])
