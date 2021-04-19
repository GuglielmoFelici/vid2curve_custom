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
                graph.add_node(idx+1, vector=line[1:4])
            elif line[0] == 'l':
                graph.add_edge(int(line[1]), int(line[2]))
    return graph


def cleanup_graph(graph: nx.Graph, relabel_nodes=False, visualize=global_options.plot):
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
    if relabel_nodes:
        newGraph = nx.relabel_nodes(
            graph,
            {node: idx+1 for idx, node in enumerate(graph.nodes)}
        )
    return newGraph


def graph_to_obj(graph: nx.Graph, objFileName: str):
    vertices = []
    lines = []
    for nodeView in graph.nodes(data='vector'):
        vertices.append(f'v {" ".join(nodeView[1])}\n')  # TODO add color?
    for edge in graph.edges:
        u, v = list(edge)
        lines.append(f'l {u} {v}\n')
    with open(objFileName, 'w') as destFile:
        destFile.writelines(vertices)
        destFile.writelines(lines)


def plot_graph(graph: nx.Graph, current_vertex=None, colored_vertices=[], colored_edges=[]):
    vertices, vColors, vSizes, lines, lColors = [], [], [], [], []
    for node in graph.nodes:
        vertices.append(np.array(
            graph.nodes(data=True)[node]['vector']
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


def plot_paths(graph: nx.Graph, paths: dict):
    for node in paths:
        print("\nNODE", node)
        for path in paths[node]:
            print(path)
            print(list(zip(path[:-1], path[1:])))
            print("\n")
            plot_graph(graph, colored_vertices=path, current_vertex=node,
                       colored_edges=list(zip(path[:-1], path[1:])))


graph = graph_from_obj('curves.obj')
graph = cleanup_graph(graph, relabel_nodes=True, visualize=False)
paths = reduce_to_triangles(graph)
plot_paths(graph, paths)
# print(list(zip(paths[:-1], paths[1:])))
# graph_to_obj(graph, 'out.obj')
