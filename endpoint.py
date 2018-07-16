# coding=utf-8

from __future__ import annotations

import json
from typing import Dict, Any

import compile
import execute
import parse


def build_vertex(name: str, single_attrs: Dict[str, str] = {}, mult_attrs={}):
    return {"name": name, "single_attrs": single_attrs, "mult_attrs": mult_attrs}


def build_edge(a: int, b: int, directed: bool, single_attrs: Dict[str, str] = {}, mult_attrs={}):
    return {"directed": directed, "head": a, "tail": b, "single_attrs": single_attrs, "mult_attrs": mult_attrs}


def get_graph(graph: execute.Graph) -> Dict[str, Any]:
    out = {"vertices": [], "edges": []}

    vlookup = {}

    for vertex in graph.vertices:
        vlookup[vertex.id] = len(vlookup)
        out["vertices"].append(build_vertex(vertex.id))

    for edge in graph.edges:
        out["edges"].append(build_edge(vlookup[edge.a], vlookup[edge.b], False))

    return out


def get_data(program: str, string: str) -> dict:
    parse_tree = parse.parse(program)
    ast = compile.compile_tree(parse_tree)
    data = execute.Execute(ast, string).get_data()

    out = {}
    graph = get_graph(data.values[execute.GRAPH_NAME].values[tuple()])

    out["graph"] = graph

    return json.dumps(out)
