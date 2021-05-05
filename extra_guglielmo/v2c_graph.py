
from __future__ import annotations
import networkx as nx
import numpy as np
import visualize as plot
from typing import List, Tuple, Set, FrozenSet, Dict


class V2CGraph(nx.Graph):

    def __init__(self, graph: nx.Graph = None):
        super().__init__(incoming_graph_data=graph)

    @classmethod
    def from_obj(cls, objFileName: str) -> V2CGraph:
        graph = V2CGraph()
        with open(objFileName, 'r') as objFile:
            vert_n = 0
            for line in objFile.readlines():
                line = line.split()
                if line and line[0] == 'v':
                    vert_n += 1
                    graph.add_node(vert_n, vector=[float(coord)
                                                   for coord in line[1:4]])
                elif line and line[0] == 'l':
                    graph.add_edge(int(line[1]), int(line[2]))
        return graph

    def to_obj(self, objFileName: str):
        vertices = []
        lines = []
        for _, node_vec in self.nodes(data='vector'):
            vertices.append(
                f'v {" ".join([str(coord) for coord in node_vec])}\n')
        for edge in self.edges:
            u, v = list(edge)
            lines.append(f'l {u} {v}\n')
        with open(objFileName, 'w') as destFile:
            destFile.writelines(vertices + lines)

    def relabel_nodes(self) -> V2CGraph:
        ''' Remaps node tags to numbers in [1, N] to ensure OBJ compatibility. Returns a new graph.  '''
        return V2CGraph(
            graph=nx.relabel_nodes(
                self,
                {node: idx+1 for idx, node in enumerate(self.nodes)}
            ))

    def vertex_pos(self, v: int) -> List[float]:
        return self.nodes[v]['vector']

    def sorted_edges(self) -> List[Tuple]:
        return sort_edges(self.edges)

    def has_edge(self, edge) -> bool:
        return tuple(sorted(edge)) in self.sorted_edges()

    def vert_dist(self, u: int, v: int) -> float:
        sqrd_dist = np.sum((np.array(self.vertex_pos(u)) -
                            np.array(self.vertex_pos(v)))**2)
        return np.sqrt(sqrd_dist)

    def mean_edge_len(self) -> float:
        return sum([self.vert_dist(*edge) for edge in self.edges]) / self.number_of_edges()

    def find_cycles(self, length, visualize=False) -> (List[List[Tuple]], Dict[Tuple, int]):
        ''' Returns a list of cycles (where each cycle is a list of sorted edges) and a dictionary with sorted edges as keys and edges' degrees as values.
            An edge's degree is the amount of cycles it belongs too.  '''
        cycles = set()  # performance
        curr_path = []
        degrees = {edge: 0 for edge in self.sorted_edges()}

        def find_cycles(start):
            curr_path.append(start)
            # order of edges in cycle doesn't count
            cycle = frozenset(sort_edges(path_to_edges(curr_path)))
            visualize and plot.plot_graph(self,
                                          highlighted_vertex=curr_path[0],
                                          colored_vertices=curr_path,
                                          frame_duration=0.2,
                                          colored_edges=cycle)
            if len(curr_path) == length:
                if start == curr_path[0] and cycle not in cycles:
                    cycles.add(cycle)
                    for edge in cycle:
                        degrees[edge] += 1
                    visualize and plot.plot_graph(self,
                                                  highlighted_vertex=curr_path[0],
                                                  colored_vertices=curr_path,
                                                  colored_edges=cycle,
                                                  edges_color=[0, 255, 0, 1],
                                                  frame_duration=1)
            else:
                for adj in [n for n in self.adj[start] if len(curr_path) < 2 or n != curr_path[-2]]:
                    find_cycles(adj)
            curr_path.pop()
        for node in self.nodes:
            find_cycles(node)
        return list(map(list, cycles)), degrees

    def simplify_edges(self, visualize=False):
        '''
            Removes every node with 2 adjacents (read "is not a triangle vertex in the mesh").
        '''
        visited = [False for _ in range(self.size())]
        stack = [next((n for n in self.nodes if self.degree(n) == 2), None)]
        if not stack[0]:
            return
        while stack:
            node = stack.pop()
            adjacencents = list(self.adj[node])
            if not visited[node]:
                visited[node] = True
                stack += [n for n in adjacencents
                          if not visited[n] and n not in stack]
                if visualize:
                    plot.plot_graph(self,
                                    highlighted_vertex=node,
                                    colored_vertices=[
                                        node for node in self.nodes if visited[node]],
                                    title='Checking vertex for removal')
                if self.degree(node) == 2:
                    u, v = adjacencents
                    self.remove_node(node)
                    self.add_edge(u, v)

    def merge_close_vecs(self, visualize=False):
        avg_edge_len = self.mean_edge_len()

        def next_small_edge(): return next((edge for edge in self.edges
                                            if self.vert_dist(*edge) < (avg_edge_len/10)),
                                           None)
        edge = next_small_edge()
        while edge:
            u, v = edge
            if visualize:
                plot.plot_graph(
                    self,
                    colored_vertices=[u, v],
                    frame_duration=1,
                    title='Merging cluster')
            # Centroid
            self.nodes[u]['vector'] = np.divide(
                np.sum(
                    [np.array(self.vertex_pos(u)),
                     np.array(self.vertex_pos(v))],
                    axis=0),
                2
            )
            # Merge neighbours
            self.add_edges_from([(u, adj) for adj in self.adj[v]
                                 if adj != u])
            self.remove_node(v)
            if visualize:
                plot.plot_graph(
                    self,
                    highlighted_vertex=u,
                    frame_duration=1,
                    title='Cluster merging: vectors merged')
            edge = next_small_edge()


def path_to_edges(path: list) -> List[Tuple]:
    ''' [1, 2, 3, 4] -> [(1,2), (2,3), (3,4)] '''
    return list(zip(path[:-1], path[1:]))


def sort_edges(edges: list) -> List[Tuple]:
    return list(map(lambda edge: tuple(sorted(edge)), edges))


def from_obj(objFileName: str) -> V2CGraph:
    return V2CGraph.from_obj(objFileName)
