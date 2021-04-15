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
    visited = [False for i in range(graph.size())]
    stack = [next((n for n in graph.nodes if graph.degree(n) == 2), None)]
    if stack[0] == None:
        return
    while len(stack):
        node = stack.pop()
        adjacencents = list(graph.adj[node].keys())
        if not visited[node]:
            visited[node] = True
            stack += [n for n in adjacencents
                      if not visited[n] and n not in stack]
            # plot_graph(graph, currentVertex=node, explored=visited)
            if graph.degree(node) == 2:
                u, v = adjacencents
                graph.remove_node(node)
                graph.add_edge(u, v)
    if relabel_nodes:
        nx.relabel_nodes(
            graph,
            {node: idx+1 for idx, node in enumerate(graph.nodes)},
            copy=False
        )


def graph_to_obj(graph: nx.Graph, objFileName: str):
    vertices = []
    lines = []
    for nodeView in graph.nodes(data='vector'):
        vertices.append(f'v {" ".join(nodeView[1])}\n')  # TODO add color?
    print(len(graph.edges)
    for edge in graph.edges:
        u, v=list(edge)
        lines.append(f'l {u} {v}\n')
    with open(objFileName, 'w') as destFile:
        destFile.writelines(vertices)
        destFile.writelines(lines)


def plot_graph(graph: nx.Graph, currentVertex=None, explored=[], stack=[]):
    vertices, vColors, vSizes, lines=[], [], [], []
    for node in graph.nodes:
        vertices.append(np.array(
            graph.nodes(data=True)[node]['vector']
        ))
        if node == currentVertex:
            vColors.append(np.array([0, 255, 0, 1]))
            vSizes.append(10)
        elif explored[node]:
            vColors.append(np.array([0, 0, 255, 1]))
            vSizes.append(15)
        elif node in stack:
            vColors.append(np.array([255, 255, 0, 1]))
            vSizes.append(10)
        else:
            vColors.append(np.array([255, 0, 0, 1]))
            vSizes.append(4)
    lines=[]
    for edge in graph.edges:
        u, v=list(edge)
        lines.append(
            np.array(graph.nodes(data=True)[u]['vector']))
        lines.append(
            np.array(graph.nodes(data=True)[v]['vector']))
    lineWidget.setData(pos=np.array(lines), mode='lines')
    vertexWidget.setData(pos=np.array(vertices),
                         color=np.array(vColors), size=np.array(vSizes))
    input("")


graph=graph_from_obj('curves.obj')
cleanup_graph(graph, relabel_nodes=True)
graph_to_obj(graph, 'out.obj')


# create three grids, add each to the view
# xgrid = gl.GLGridItem()
# ygrid = gl.GLGridItem()
# zgrid = gl.GLGridItem()
# view.addItem(xgrid)
# view.addItem(ygrid)
# view.addItem(zgrid)
