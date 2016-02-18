from __future__ import absolute_import, print_function

import pathlib

import networkx as nx

nets = list(pathlib.Path(__file__).parent.glob('*.net'))
for net in nets:
    G = nx.read_pajek(str(net))

    if isinstance(G, nx.MultiDiGraph):
        G = nx.DiGraph(G)
    else:
        G = nx.Graph(G)

    globals()[net.stem] = G


del net
del nets
del nx
del pathlib
del G
