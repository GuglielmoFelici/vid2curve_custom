from networkx.algorithms.bipartite.basic import color
import pyqtgraph.opengl as gl
import networkx as nx
import pyqtgraph as pg
import numpy as np
import argparse
import graph_utils

parser = argparse.ArgumentParser(
    description='Reduces vertices in OBJ-represented graph')

parser.add_argument('-p', '--plot', dest='plot',
                    action='store_true', help='Visualize the algorithm')
global_options = parser.parse_args()

if global_options.plot:
    pg.mkQApp()
    # make a widget for displaying 3D objects
    view = gl.GLViewWidget()
    lineWidget = gl.GLLinePlotItem()
    vertexWidget = gl.GLScatterPlotItem()
    view.addItem(lineWidget)
    view.addItem(vertexWidget)
    view.show()

FILE = 'curves.obj'


def graph_from_obj(objFileName: str):
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


def relabel_nodes(graph: nx.Graph):
    ''' Rimappa NON IN PLACE le etichette dei nodi con numeri crescenti da 1 a N. Ritorna un nuovo grafo '''
    newGraph = nx.relabel_nodes(
        graph,
        {node: idx+1 for idx, node in enumerate(graph.nodes)}
    )
    return newGraph


def cleanup_graph(graph: nx.Graph, visualize=global_options.plot):
    '''
        Removes every node with 2 adjacents (read "is not a triangle vertex in the mesh").
        If relabel_nodes is True, relabels the nodes with numbers from 1 to n
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
                plot_graph(graph, current_vertex=node,
                           colored_vertices=[vis for vis in visited if visited[vis]])
            if graph.degree(node) == 2:
                u, v = adjacencents
                graph.remove_node(node)
                graph.add_edge(u, v)


def graph_to_obj(graph: nx.Graph, objFileName: str):
    vertices = []
    lines = []
    for node, node_vec in graph.nodes(data='vector'):
        # TODO add color?
        vertices.append(f'v {" ".join([str(x) for x in node_vec])}\n')
    for edge in graph.edges:
        u, v = list(edge)
        lines.append(f'l {u} {v}\n')
    with open(objFileName, 'w') as destFile:
        destFile.writelines(vertices)
        destFile.writelines(lines)


def plot_graph(graph: nx.Graph, current_vertex=None, colored_vertices=[], colored_edges=[]):
    vertices, vColors, vSizes, lines, lColors = [], [], [], [], []
    for node, node_vec in graph.nodes(data='vector'):
        vertices.append(np.array(
            node_vec
        ))
        if node == current_vertex:
            vColors.append(np.array([0, 255, 0, 1]))
            vSizes.append(10)
        elif node in colored_vertices:
            vColors.append(np.array([0, 0, 255, 1]))
            vSizes.append(15)
        else:
            vColors.append(np.array([255, 0, 0, 1]))
            vSizes.append(4)
    lines = []
    for edge in graph.edges:
        u, v = list(edge)
        lines.append(
            np.array(graph.nodes(data=True)[u]['vector']))
        lines.append(
            np.array(graph.nodes(data=True)[v]['vector']))
        if sorted(edge) in [sorted(col_edge) for col_edge in colored_edges]:
            # , np.array([0, 255, 0, 1]))
            lColors.append(np.array([255, 0, 0, 1]))
            lColors.append(np.array([255, 0, 0, 1]))
        else:
            # ,np.array([255, 255, 255, 1]))
            lColors.append(np.array([255, 255, 255, 1]))
            lColors.append(np.array([255, 255, 255, 1]))
    lineWidget.setData(pos=np.array(lines), mode='lines',
                       color=np.array(lColors))
    vertexWidget.setData(pos=np.array(vertices),
                         color=np.array(vColors), size=np.array(vSizes))
    input("")


def reduce_to_triangles(graph: nx.Graph):
    all_loops = {}
    for node in graph.nodes:
        all_loops[node] = list(
            graph_utils.all_simple_edge_paths(graph, node, node))
    return all_loops


def path_to_edges(path: list):
    return list(zip(path[:-1], path[1:]))


def plot_paths(graph: nx.Graph, paths: dict):
    for node in paths:
        for path in paths[node]:
            plot_graph(graph, colored_vertices=path, current_vertex=node,
                       colored_edges=path_to_edges(path))


# def path_is_face(graph: nx.Graph, path: list):
#     edges = [sorted(edge) for edge in path_to_edges(path)]
#     for node in path:
#         for adj in list(graph[node]):
#             if adj in path and sorted((node, adj)) not in edges:
#                 return False
#     return True


def merge_close_vecs(graph: nx.Graph, visualize=False):
    visualize = visualize and global_options.plot
    to_merge = []
    for u, u_vec in graph.nodes(data='vector'):
        for v, v_vec in graph.nodes(data='vector'):
            if u == v:
                continue
            sqrd_dist = np.sum((np.array(u_vec) - np.array(v_vec))**2)
            dist = np.sqrt(sqrd_dist)
            if (dist < 0.01):
                to_merge.append((u, v))
    for u, v in to_merge:
        if not u in graph.nodes or not v in graph.nodes:
            continue
        if visualize:
            plot_graph(graph, current_vertex=u, colored_vertices=[v])
        new_adjacents = list(graph.adj[v])
        graph.remove_node(v)
        for new_adj in new_adjacents:
            if graph.has_node(new_adj) and new_adj != u:
                graph.add_edge(u, new_adj)
        if visualize:
            plot_graph(graph, current_vertex=u, colored_vertices=[v])


graph: nx.Graph = graph_from_obj('curves.obj')
cleanup_graph(graph, visualize=global_options.plot)
# graph = relabel_nodes(graph)
merge_close_vecs(graph)
graph = relabel_nodes(graph)
# paths = reduce_to_triangles(graph)
# plot_paths(graph, paths)
graph_to_obj(graph, 'out.obj')
