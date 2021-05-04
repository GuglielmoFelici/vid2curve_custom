import networkx as nx
import numpy as np
import visualize as plot


def graph_from_obj(objFileName: str) -> nx.Graph:
    graph = nx.Graph()
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


def graph_to_obj(graph: nx.Graph, objFileName: str):
    vertices = []
    lines = []
    graph = relabel_nodes(graph)
    for _, node_vec in graph.nodes(data='vector'):
        vertices.append(f'v {" ".join([str(coord) for coord in node_vec])}\n')
    for edge in graph.edges:
        u, v = list(edge)
        lines.append(f'l {u} {v}\n')
    with open(objFileName, 'w') as destFile:
        destFile.writelines(vertices + lines)


def relabel_nodes(graph: nx.Graph) -> nx.Graph:
    ''' Remaps node tags to numbers in [1, N] to ensure OBJ compatibility. Returns a new graph. '''
    return nx.relabel_nodes(
        graph,
        {node: idx+1 for idx, node in enumerate(graph.nodes)}
    )


def path_to_edges(path: list) -> list:
    ''' [1, 2, 3, 4] -> [(1,2), (2,3), (3,4)] '''
    return list(zip(path[:-1], path[1:]))


def vertex_pos(graph: nx.Graph, v: int):
    return graph.nodes[v]['vector']


def vert_dist(graph: nx.Graph, u: int, v: int):
    sqrd_dist = np.sum((np.array(vertex_pos(graph, u)) -
                        np.array(vertex_pos(graph, v)))**2)
    return np.sqrt(sqrd_dist)


def mean_edge_len(graph: nx.Graph):
    return sum([vert_dist(graph, *edge) for edge in graph.edges]) / graph.number_of_edges()


def get_triangles(graph: nx.Graph, visualize=False):
    def custom_dfs(graph, node, path, cycles):
        path.append(node)
        if visualize:
            plot.plot_graph(graph, colored_vertices=path, frame_duration=1)
        if len(path) == 3:
            if node == path[0]:
                cycles.append(path)
                if visualize:
                    plot.plot_graph(graph, colored_vertices=path, colored_edges=[
                        sorted(edge) for edge in path_to_edges(path)], frame_duration=1)
        else:
            for adj in graph.adj[node]:
                custom_dfs(graph, adj, path, cycles)
        path.pop()
    cycles = []
    for node in graph:
        custom_dfs(graph, node, [], cycles)


def simplify_edges(graph: nx.Graph, visualize=False):
    '''
        Removes every node with 2 adjacents (read "is not a triangle vertex in the mesh").
    '''
    visited = [False for _ in range(graph.size())]
    stack = [next((n for n in graph if graph.degree(n) == 2), None)]
    if not stack[0]:
        return
    while stack:
        node = stack.pop()
        adjacencents = list(graph.adj[node])
        if not visited[node]:
            visited[node] = True
            stack += [n for n in adjacencents
                      if not visited[n] and n not in stack]
            if visualize:
                plot.plot_graph(graph,
                                highlighted_vertex=node,
                                colored_vertices=[
                                    node for node in graph if visited[node]],
                                title='Checking vertex for removal')
            if graph.degree(node) == 2:
                u, v = adjacencents
                graph.remove_node(node)
                graph.add_edge(u, v)


def merge_close_vecs(graph: nx.Graph, visualize=False):
    avg_edge_len = mean_edge_len(graph)

    def next_small_edge(): return next((edge for edge in graph.edges
                                        if vert_dist(graph, *edge) < (avg_edge_len/10)),
                                       None)
    edge = next_small_edge()
    while edge:
        u, v = edge
        if visualize:
            plot.plot_graph(
                graph,
                colored_vertices=[u, v],
                frame_duration=1,
                title='Merging cluster')
        # Centroid
        graph.nodes[u]['vector'] = np.divide(
            np.sum(
                [np.array(vertex_pos(graph, u)),
                 np.array(vertex_pos(graph, v))],
                axis=0),
            2
        )
        # Merge neighbours
        graph.add_edges_from([(u, adj) for adj in graph.adj[v]
                              if adj != u])
        graph.remove_node(v)
        if visualize:
            plot.plot_graph(
                graph,
                highlighted_vertex=u,
                frame_duration=1,
                title='Cluster merging: vectors merged')
        edge = next_small_edge()
