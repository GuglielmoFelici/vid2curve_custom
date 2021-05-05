import pyqtgraph.opengl as gl
import pyqtgraph as pg
import numpy as np
import v2c_graph as graph
import time


view = lineWidget = vertexWidget = None


def init_window():
    global view, lineWidget, vertexWidget
    pg.mkQApp()
    # make a widget to display 3D objects
    view = gl.GLViewWidget()
    lineWidget = gl.GLLinePlotItem()
    vertexWidget = gl.GLScatterPlotItem()
    view.addItem(lineWidget)
    view.addItem(vertexWidget)
    view.show()


def responsive_sleep(secs: int):
    i = 0
    while i < secs:
        time.sleep(0.01)
        i += 0.01
        pg.mkQApp().processEvents()


def plot_graph(g: graph.V2CGraph,
               highlighted_vertex=None,
               colored_vertices=[],
               colored_edges=[],
               edges_color=[255, 0, 0, 1],
               title='',
               is_frame=True,
               frame_duration=0.01):
    ''' Plots the graph. If is_frame is True, pauses the program for frame_duration (to be used in loops).'''
    if not view or not lineWidget or not vertexWidget:
        print("Error: window not initialized properly")
        return False
    if title:
        view.setWindowTitle(title)
    vertices, vColors, vSizes, lines, lColors = [], [], [], [], []
    for node, node_vec in g.nodes(data='vector'):
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
    for edge in g.edges:
        u, v = edge
        lines.append(
            np.array(g.vertex_pos(u)))
        lines.append(
            np.array(g.vertex_pos(v)))
        if tuple(sorted(edge)) in graph.sort_edges(colored_edges):
            lColors.append(np.array(edges_color))
            lColors.append(np.array(edges_color))
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


def plot_cycles(graph: graph.V2CGraph, paths: dict):
    for node in paths:
        for path in paths[node]:
            plot_graph(graph, colored_vertices=path, highlighted_vertex=node,
                       colored_edges=graph.path_to_edges(path))
