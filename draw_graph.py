# coding=utf-8
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class Vertex:
    x: int
    y: int


@dataclass
class Force:
    fx: int
    fy: int


D = 200
K1 = 0.3
K2 = 10000

THRESHOLD = 0.05

XHEIGHT = 400
YHEIGHT = 400


def dist(v1: Vertex, v2: Vertex) -> float:
    return ((v2.x - v1.x) ** 2 + (v2.y - v1.y) ** 2) ** (1 / 2)


def position(num_vertices: int, edges: List[Tuple[int, int]]) -> List[Vertex]:
    vertices = [Vertex(100 + i ** 2, 100 * i) for i in range(num_vertices)]

    bigMove = True
    while bigMove:
        bigMove = False
        forces = [Force(0, 0) for _ in range(num_vertices)]
        for edge in edges:
            for (a, b) in [(edge[0], edge[1]), (edge[1], edge[0])]:
                d = dist(vertices[a], vertices[b])
                F = K1 * (d - D)
                forces[a].fx += F * (vertices[b].x - vertices[a].x) / d
                forces[a].fy += F * (vertices[b].y - vertices[a].y) / d
        for i, v1 in enumerate(vertices):
            for j, v2 in enumerate(vertices):
                if v1 == v2:
                    continue
                forces[i].fx += K2 / (dist(v1, v2) ** 3) * (v1.x - v2.x)
                forces[i].fy += K2 / (dist(v1, v2) ** 3) * (v1.y - v2.y)
                forces[j].fx += K2 / (dist(v1, v2) ** 3) * (v2.x - v1.x)
                forces[j].fy += K2 / (dist(v1, v2) ** 3) * (v2.y - v1.y)
        for i, force in enumerate(forces):
            if force.fx ** 2 + force.fy ** 2 > THRESHOLD:
                bigMove = True
            vertices[i].x += force.fx
            vertices[i].y += force.fy

    minX = min(v.x for v in vertices)
    maxX = max(v.x for v in vertices)
    minY = min(v.y for v in vertices)
    maxY = max(v.y for v in vertices)

    print(minX, minY, maxX, maxY)

    for i, vertex in enumerate(vertices):
        vertices[i] = Vertex(int((vertex.x - minX) / (maxX - minX) * XHEIGHT),
                             int((vertex.y - minY) / (maxY - minY) * YHEIGHT))

    return vertices
