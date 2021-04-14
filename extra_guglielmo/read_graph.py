import networkx as nx

FILE = 'curves.obj'


def build_graph_from_obj(objFileName):
    graph = nx.Graph()
    with open(objFileName, 'r') as objFile:
        for idx, line in enumerate(objFile.readlines()):
            line = line.split()
            if line[0] == 'v':
                graph.add_node(idx+1, vector=line[1:4])
            elif line[0] == 'l':
                graph.add_edge(line[1], line[2])
    return graph
