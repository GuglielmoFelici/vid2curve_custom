import networkx as nx
import numpy as np
import visualize as plot
# from visualize import plot_graph


def graph_from_obj(objFileName: str) -> nx.Graph:
    graph = nx.Graph()
    with open(objFileName, 'r') as objFile:
        for idx, line in enumerate(objFile.readlines()):
            line = line.split()
            if line[0] == 'v':
                graph.add_node(idx+1, vector=[float(coord)
                                              for coord in line[1:4]])
            elif line[0] == 'l':
                graph.add_edge(int(line[1]), int(line[2]))
    return graph


def graph_to_obj(graph: nx.Graph, objFileName: str):
    vertices = []
    lines = []
    graph = relabel_nodes(graph)
    for node, node_vec in graph.nodes(data='vector'):
        # TODO add color?
        vertices.append(f'v {" ".join([str(coord) for coord in node_vec])}\n')
    for edge in graph.edges:
        u, v = list(edge)
        lines.append(f'l {u} {v}\n')
    with open(objFileName, 'w') as destFile:
        destFile.writelines(vertices)
        destFile.writelines(lines)


def relabel_nodes(graph: nx.Graph) -> nx.Graph:
    ''' Remaps node tags to numbers in [1, N] to ensure OBJ compatibility. Returns a new graph. '''
    newGraph = nx.relabel_nodes(
        graph,
        {node: idx+1 for idx, node in enumerate(graph.nodes)}
    )
    return newGraph


def path_to_edges(path: list) -> list:
    ''' [1,2,3, 4] -> [(1,2), (2,3), (3,4)] '''
    return list(zip(path[:-1], path[1:]))


def vert_dist(u: list, v: list):
    sqrd_dist = np.sum((np.array(u) - np.array(v))**2)
    return np.sqrt(sqrd_dist)


def get_vertex_pos(graph: nx.Graph, v: int):
    return graph.nodes(data=True)[v]['vector']


def simplify_edges(graph: nx.Graph, visualize=False):
    '''
        Removes every node with 2 adjacents (read "is not a triangle vertex in the mesh").
    '''
    visited = [False for i in range(graph.size())]
    stack = [next((n for n in graph.nodes if graph.degree(n) == 2), None)]
    if stack[0] == None:
        return
    while len(stack):  # TODO while stack
        node = stack.pop()
        adjacencents = list(graph.adj[node].keys())
        if not visited[node]:
            visited[node] = True
            stack += [n for n in adjacencents
                      if not visited[n] and n not in stack]
            if visualize:
                plot.plot_graph(graph,
                                highlighted_vertex=node,
                                colored_vertices=[
                                    vis for vis in graph.nodes if visited[vis]],
                                title='Checking vertices for removal')
            if graph.degree(node) == 2:
                u, v = adjacencents
                graph.remove_node(node)
                graph.add_edge(u, v)


def merge_close_vecs(graph: nx.Graph, visualize=False):
    clusters = []
    for u, u_vec in graph.nodes(data='vector'):
        cluster = [u]
        for v, v_vec in graph.nodes(data='vector'):
            if u == v:
                continue
            sqrd_dist = np.sum((np.array(u_vec) - np.array(v_vec))**2)
            dist = np.sqrt(sqrd_dist)
            if (dist < 0.01):
                cluster.append(v)
                # to_merge.append((u, v))
        if len(cluster) > 1:
            clusters.append(cluster)
    for cluster in clusters:
        if set(cluster) - set(graph.nodes):
            continue
        if visualize:
            plot.plot_graph(
                graph,
                colored_vertices=cluster,
                frame_duration=1,
                title='Cluster merging: vector cluster found')
        centroid = np.divide(
            np.sum(
                [np.array(get_vertex_pos(graph, v)) for v in cluster],
                axis=0),
            len(cluster)
        )
        new_node = cluster[0]
        new_adjacents = []
        for node in cluster:
            new_adjacents += list(graph.adj[node])
        graph.remove_nodes_from(cluster)
        graph.add_node(new_node, vector=centroid)
        for adj in new_adjacents:
            if graph.has_node(adj) and adj != new_node:
                graph.add_edge(new_node, adj)
        if visualize:
            plot.plot_graph(
                graph,
                highlighted_vertex=new_node,
                frame_duration=1,
                title='Cluster merging: cluster merged in new vector')

# def reduce_to_triangles(graph: nx.Graph):
#     all_loops = {}
#     for node in graph.nodes:
#         all_loops[node] = list(
#             graph_utils.all_simple_edge_paths(graph, node, node))
#     return all_loops


# def path_is_face(graph: nx.Graph, path: list):
#     edges = [sorted(edge) for edge in path_to_edges(path)]
#     for node in path:
#         for adj in list(graph[node]):
#             if adj in path and sorted((node, adj)) not in edges:
#                 return False
#     return True
