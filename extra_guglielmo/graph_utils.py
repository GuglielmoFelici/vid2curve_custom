import networkx as nx


def _all_simple_paths_graph(G: nx.Graph, source, target):
    current_path = [source]
    # visited = dict.fromkeys(G.nodes, False)
    stack = list(G[source])
    while stack:
        node = stack.pop()
        if node == None:
            current_path.pop()
            continue
        elif node == target:
            yield current_path + [node]
            pass
        if node in current_path:
            continue
        current_path += [node]
        # elif node in current_path:
        #     current_path.pop()
        if G[node]:
            stack.append(None)
            stack += list(G[node])
        else:
            current_path.pop()


def BAK_all_simple_paths_graph(G, source, target, cutoff):
    """
    Versione modificata di nx._all_simple_paths_graph per tornare simple paths che possano partire e arrivare allo stesso nodo
    """
    print(source, "\n")
    visited = []  # [source]
    stack = [iter(G[source])]
    while stack:
        children = stack[-1]
        child = next(children, None)
        if child is None:
            stack.pop()
            visited.pop()
        elif len(visited) < cutoff:
            if child == target:
                yield visited + [child]
            elif child in visited:
                continue
            visited += [child]
            if target not in visited:  # expand stack until find all targets
                stack.append(iter(G[child]))
            else:
                visited.pop()  # maybe other ways to child
        else:  # len(visited) == cutoff:
            # for target in (targets & (set(children) | {child})) - set(visited.keys()):
            yield visited + [target]
            stack.pop()
            visited.pop()


def all_simple_edge_paths(G, source, target, cutoff=None):
    """
    Versione modificata di nx.all_simple_edge_paths.

    """
    if source not in G:
        raise nx.NodeNotFound("source node %s not in graph" % source)
    if target not in G:
        raise nx.NodeNotFound("source node %s not in graph" % source)
    # if source in targets:
    #    return []
    if cutoff is None:
        cutoff = len(G) - 1
    if cutoff < 1:
        return []
    return _all_simple_paths_graph(G, source, target)
    # for simp_path in _all_simple_paths_graph(G, source, target):
    #     yield list(zip(simp_path[:-1], simp_path[1:]))
