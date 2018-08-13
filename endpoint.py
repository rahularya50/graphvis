# coding=utf-8

from __future__ import annotations

import json
from typing import Dict, Any, List, Tuple

import compile
import draw_graph
import execute
import parse


def build_vertex(name: str, position: draw_graph.Vertex, single_attrs: Dict[str, str] = {}, mult_attrs={}):
    return {"name": name, "x": position.x, "y": position.y, "single_attrs": single_attrs, "mult_attrs": mult_attrs}


def build_edge(a: int, b: int, directed: bool, single_attrs: Dict[str, str] = {}, mult_attrs={}):
    return {"directed": directed, "head": a, "tail": b, "single_attrs": single_attrs, "mult_attrs": mult_attrs}


def get_graph(graph: execute.Graph) -> Dict[str, Any]:
    out = {"vertices": [], "edges": []}

    vlookup = {}

    for i, vertex in enumerate(graph.vertices):
        vlookup[vertex.id] = i

    positions = draw_graph.position(len(graph.vertices), [(vlookup[edge.a], vlookup[edge.b]) for edge in graph.edges])

    for i, vertex in enumerate(graph.vertices):
        out["vertices"].append(build_vertex(vertex.id, positions[i]))

    for edge in graph.edges:
        out["edges"].append(build_edge(vlookup[edge.a], vlookup[edge.b], False))

    return out


def get_vargraph(root: execute.Root) -> Dict[compile.VarName, List[compile.VarName]]:
    out = {}
    for var in root.values:
        out[var] = root.values[var].ancestors
    return out


def get_varvals(root: execute.Root) -> Dict[compile.VarName, Dict[Tuple[int], int]]:
    out = {}
    for var in root.values:
        out[var] = root.values[var].values
    return out


def get_data(program: str, string: str) -> dict:
    parse_tree = parse.parse(program)
    ast = compile.compile_tree(parse_tree)
    data = execute.Execute(ast, string).get_data()

    out = {}

    vargraph = get_vargraph(data)
    out["vargraph"] = vargraph

    varvals = get_varvals(data)
    out["varvals"] = varvals

    graph = get_graph(data.values[execute.GRAPH_NAME].values[tuple()])
    out["graph"] = graph

    return json.dumps(out)
