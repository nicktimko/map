from __future__ import print_function, absolute_import

from collections import defaultdict
import copy

import numpy as np

def nlogn(n):
    return n * np.log2(n)


def total_edge_weight(G):
    return (1 if G.is_directed() else 2) * sum(edge[2].get('weight', 1) for edge in G.edges_iter(data=True))


def node_weight(G, n):
    return sum(edge[2].get('weight', 1) for edge in G.edges_iter(n, data=True))


def relative_weight(G, n):
    if 'rw' not in G.node[n]:
        G.node[n]['rw'] = node_weight(G, n) / total_edge_weight(G)
    return G.node[n]['rw']


class MapEqnManager(object):
    def __init__(self, graph):
        self.G = graph
        if self.G.is_directed():
            raise ValueError('directed graphs not supported yet')

        self._init_weights()
        self._init_modules()

    def _init_weights(self):
        self.Gtw = total_edge_weight(self.G)
        self.nrw = {}
        for n in self.G.nodes_iter():
            self.nrw[n] = node_weight(self.G, n) / self.Gtw
        self.term3 = -sum(nlogn(rw) for rw in self.nrw.values())

    def _init_modules(self):
        self.nm = {}
        self.mn = defaultdict(set)

        # each node is it's own module at the start
        for n in self.G.nodes_iter():
            self.nm[n] = n
            self.mn[n].add(n)

    def module_weight(self, m):
        return sum(self.nrw[n] for n in self.mn[m])

    def module_exit_weight(self, m):
        return sum(self.G.node[n].get('weight', 1) / self.Gtw
                for n, neighbor
                in self.G.edges_iter(self.mn[m])
                if neighbor not in self.mn[m])

    def total_exit_weight(self):
        return sum(self.module_exit_weight(m) for m, nodes in self.mn.items() if nodes)

    def move_node_to_module(self, n, m):
        self.mn[self.nm[n]].remove(n)

        self.nm[n] = m
        self.mn[m].add(n)

    def move_nodes_to_module(self, nodes, m):
        for n in set(nodes):
            self.move_node_to_module(n, m)

    def code_length(self):
        mod_weights = {m: self.module_weight(m) for m, nodes in self.mn.items() if nodes}
        if len(mod_weights) == 1:
            # single module, the other terms are useless/invalid
            return self.term3

        mod_exit_weights = {m: self.module_exit_weight(m) for m in mod_weights}
        total_exit_weight = sum(mod_exit_weights.values())
        return (nlogn(total_exit_weight)
                - 2 * sum(nlogn(ew) for ew in mod_exit_weights.values())
                + self.term3
                + sum(nlogn(mod_weights[m] + mod_exit_weights[m]) for m in mod_weights))

    def module_neighbors(self, m):
        module_neighbors = set()

        for node in self.mn[m]:
            for neighbor in self.G.neighbors(node):
                module_neighbors.add(self.nm[neighbor])
        module_neighbors.discard(m)

        return module_neighbors

    def modules(self):
        return (v for k, v in self.mn.items() if v)

    ######## TESTING / VISUALIZATION #######

    def d3(self, *args, **kwargs):
        import d3shims
        # copy modules to "group" attribute on nodes
        for n, m in self.nm.items():
            self.G.node[n]['group'] = m
        return d3shims.nx_force(self.G, *args, **kwargs)

    def _single_module(self, the_one=1):
        for n in self.nm:
            self.nm[n] = the_one
        self.mn = defaultdict(set, {the_one: set(self.nm)})

    def _verify_module_map_consistency(self):
        """
        Checks synchronization between node->module and module->nodes mappings
        """
        nodes = set(self.nm)
        mn_temp = copy.deepcopy(self.mn)
        while nodes:
            n = nodes.pop()
            m = self.nm[n]
            try:
                mn_temp[m].remove(n)
            except KeyError:
                raise AssertionError('node {} not in expected module {}'.format(n, m))

        for m, m_leftovers in mn_temp.items():
            assert not m_leftovers, 'extra node in module map! (node(s) {} in module {})'.format(m_leftovers, m)


def mapeq(G):
    mG = MapEqnManager(G)
    return mG.code_length()
