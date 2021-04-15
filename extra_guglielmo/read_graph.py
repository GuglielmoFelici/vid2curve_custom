import pyqtgraph.opengl as gl
import networkx as nx
import pyqtgraph as pg
import numpy as np
import time
from threading import Thread
import datetime

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


def cleanup_graph(graph: nx.Graph, relabel_nodes=False):
    '''
        Removes every node with 2 adjacents (read "is not a triangle vertex in the mesh").
        If relabel_nodes is True, relabels the nodes with numbers from 1 to n
    '''
    node = next((n for n in graph.adj if graph.degree(n) == 2), None)
    __cleanup_graph__(graph, node)
    if relabel_nodes:
        nx.relabel_nodes(
            graph,
            {node: idx+1 for idx, node in enumerate(graph.nodes)},
            copy=False
        )


def __cleanup_graph__(graph: nx.Graph, root, visited=[]):
    visited.append(root)
    adjacencents = list(graph.adj[root].keys())
    plot_graph(graph, currentVertex=root, explored=visited)
    if graph.degree(root) == 2:
        u, v = adjacencents
        graph.remove_node(root)
        graph.add_edge(u, v)
    input(".")
    __cleanup_graph__(graph, next(
        n for n in adjacencents if n not in visited), visited)

    # while node:
    #     u, v = graph.adj[node].keys()
    #     plot_graph(graph, currentVertex=node)
    #     graph.remove_node(node)
    #     graph.add_edge(u, v)
    #     input(".")
    #     node = u
    # node = next((n for n in graph.adj if graph.degree(n) == 2), None)
    # plot_graph(graph)
    # t = Thread(target=plot_graph, args=[graph])
    # t.start()
    # plot_graph(graph)
    # t.join()


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


def plot_graph(graph: nx.Graph, currentVertex=None, explored=[]):
    vertices = vColors = vSizes = []
    for node in graph.nodes:
        vertices.append(np.array([
            graph.nodes(data=True)[node]['vector']
        ]))
        vColors.append(
            np.array([255, 0, 0, 1]) if node != currentVertex
            else np.array([0, 255, 0, 1])
        )
        if node == currentVertex:
            vColors.append(np.array([255, 0, 0, 1]))
            vSizes.append(4)
        else:
            vColors.append(np.array([0, 255, 0, 1]))
            vSizes.append(10)
    vertices = np.array([node[1] for node in graph.nodes(data='vector')])
    # print([
    #     np.array([255, 0, 0, 1]) if node != currentVertex
    #     else np.array([0, 255, 0, 1])
    #     for node in graph.nodes
    # ])
    vColors = np.array(
        [
            np.array([255, 0, 0, 1]) if node != currentVertex
            else np.array([0, 255, 0, 1])
            for node in graph.nodes
        ]
    )
    vSizes = np.array(
        [
            4 if node != currentVertex
            else 10
            for node in graph.nodes
        ]
    )
    lines = []
    for edge in graph.edges:
        lines.append(
            np.array(graph.nodes(data=True)[list(edge)[0]]['vector']))
        lines.append(
            np.array(graph.nodes(data=True)[list(edge)[1]]['vector']))
    lineWidget.setData(pos=np.array(lines), mode='lines')
    vertexWidget.setData(pos=vertices, color=vColors, size=vSizes)


graph = graph_from_obj('curves.obj')
cleanup_graph(graph, relabel_nodes=True)
# graph_to_obj(graph, 'out.obj')


# create three grids, add each to the view
# xgrid = gl.GLGridItem()
# ygrid = gl.GLGridItem()
# zgrid = gl.GLGridItem()
# view.addItem(xgrid)
# view.addItem(ygrid)
# view.addItem(zgrid)


input()
