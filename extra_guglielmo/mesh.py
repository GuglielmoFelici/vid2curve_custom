from __future__ import annotations
from v2c_graph import V2CGraph
import numpy as np
from functools import reduce


class Mesh:

    def __init__(self, vertices: np.array, triangles: np.array):
        self.vertices = vertices
        self.triangles = triangles

    @classmethod
    def from_graph(cls, graph: V2CGraph, visualize=False) -> Mesh:
        triangles, degrees = graph.find_cycles(4, visualize=visualize)
        vertices = np.array(
            [vec for _, vec in graph.nodes(data='vector')])
        faces = np.empty((0, 3), dtype=np.int32)
        for tr in triangles:
            if any(degrees[edge] == 2 for edge in tr):  # is not an inner face
                faces = np.append(faces,
                                  [list(reduce(lambda edge1, edge2:
                                               set(edge1) | set(edge2), tr))],  # {(1,2), (2,3), (3,1)} -> [[1,2,3]]
                                  axis=0)
        return Mesh(vertices, faces)

    def to_obj(self, objFileName: str):
        out_vertices = []
        out_triangles = []
        for vertex in self.vertices:
            out_vertices.append(
                f'v {" ".join([str(coord) for coord in vertex])}\n')
        for triangle in self.triangles:
            out_triangles.append(
                f'f {" ".join([str(vert) for vert in triangle])}\n')
        with open(objFileName, 'w') as destFile:
            destFile.writelines(out_vertices + out_triangles)
