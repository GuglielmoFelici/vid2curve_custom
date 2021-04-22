import networkx as nx
import pyqtgraph.opengl as gl
import pyqtgraph as pg
import numpy as np
from graph_utils import vertex_pos, path_to_edges
from PyQt5 import QtCore
import os
import time


view = lineWidget = vertexWidget = None


def init_window():
    global view, lineWidget, vertexWidget
    pg.mkQApp()
    # make a widget for displaying 3D objects
    view = gl.GLViewWidget()
    lineWidget = gl.GLLinePlotItem()
    vertexWidget = gl.GLScatterPlotItem()
    view.addItem(lineWidget)
    view.addItem(vertexWidget)
    view.show()


def _plot_graph(graph: nx.Graph, highlighted_vertex=None, colored_vertices=[], colored_edges=[], title='', wait_for_input=True, skip_key='q', clear_console=True) -> bool:
    QtCore.QTimer.singleShot(20000, lambda: print("heyo"))
    print("heyo")
    return True


def responsive_sleep(secs: int):
    i = 0
    while i < secs:
        time.sleep(0.01)
        i += 0.01
        pg.mkQApp().processEvents()


def plot_graph(graph: nx.Graph, highlighted_vertex=None, colored_vertices=[], colored_edges=[], title='', is_frame=True, frame_duration=0.01):
    ''' Plots the graph. If is_frame is True, pauses the program for frame_duration (to be used in loops).'''

    if not view or not lineWidget or not vertexWidget:
        return False
    view.setWindowTitle(title)
    vertices, vColors, vSizes, lines, lColors = [], [], [], [], []
    for node, node_vec in graph.nodes(data='vector'):
        vertices.append(np.array(
            node_vec
        ))
        if node == highlighted_vertex:
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
            np.array(vertex_pos(graph, u)))
        lines.append(
            np.array(vertex_pos(graph, v)))
        if sorted(edge) in [sorted(col_edge) for col_edge in colored_edges]:
            lColors.append(np.array([255, 0, 0, 1]))
            lColors.append(np.array([255, 0, 0, 1]))
        else:
            lColors.append(np.array([255, 255, 255, 1]))
            lColors.append(np.array([255, 255, 255, 1]))
    lineWidget.setData(pos=np.array(lines), mode='lines',
                       color=np.array(lColors))
    vertexWidget.setData(pos=np.array(vertices),
                         color=np.array(vColors), size=np.array(vSizes))
    if is_frame:
        frame_duration = max(frame_duration, min(frame_duration, 0.01))
        responsive_sleep(frame_duration)


def plot_cycles(graph: nx.Graph, paths: dict):
    for node in paths:
        for path in paths[node]:
            plot_graph(graph, colored_vertices=path, highlighted_vertex=node,
                       colored_edges=path_to_edges(path))
