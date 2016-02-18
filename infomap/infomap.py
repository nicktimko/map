from __future__ import print_function, absolute_import

import random
import time

from .mapeq import MapEqnManager


def get_nodes_and_shuffle(G):
    nodes = list(G.nodes_iter())
    random.shuffle(nodes)
    return nodes


def find_greatest_neighbor_decrease(mG, n):
    node_module = mG.nm[n] # module of focal node
    neighbors = mG.G.neighbors(n)
    scores = {None: mG.code_length()}

    for neighbor in neighbors:
        original_module = mG.nm[neighbor]
        mG.move_node_to_module(neighbor, node_module)
        scores[neighbor] = mG.code_length()
        mG.move_node_to_module(neighbor, original_module)

    return min(scores.keys(), key=lambda k: scores[k])


def node_collapse_iteration(mG):
    nodes = get_nodes_and_shuffle(mG.G)

    start = set(mG.nm.items())
    #changed = False
    for n in nodes:
        best = find_greatest_neighbor_decrease(mG, n)
        if best is None:
            continue
        mG.move_node_to_module(best, mG.nm[n])
        # oscillations might be thwarting "any change" meaning "a net change"
        # need to check, for now just check en-masse at start/end
        #changed = True

    return start != set(mG.nm.items())


def get_modules_and_shuffle(mG):
    modules = [module for module, nodes in mG.mn.items() if nodes]
    random.shuffle(modules)
    return modules


def find_greatest_module_neighbor_decrease(mG, module):
    module_neighbors = mG.module_neighbors(module)

    scores = {None: mG.code_length()}

    for mneighbor in module_neighbors:
        nodes = set(mG.mn[mneighbor]) # copy
        mG.move_nodes_to_module(nodes, module)
        scores[mneighbor] = mG.code_length()
        mG.move_nodes_to_module(nodes, mneighbor)

    return min(scores.keys(), key=lambda k: scores[k])


def module_collapse_iteration(mG):
    modules = get_modules_and_shuffle(mG)

    start = set(mG.nm.items())
    for m in modules:
        mbest = find_greatest_module_neighbor_decrease(mG, m)
        if mbest is None:
            continue
        mG.move_nodes_to_module(mG.mn[mbest], m)

    return start != set(mG.nm.items())


def infomap(G, timeout=20):
    mG = MapEqnManager(G)

    start = time.time()
    e = Exception('timeout')

    while time.time() - start < timeout:
        changes = node_collapse_iteration(mG)
        if not changes:
            break
    else:
        raise e

    while time.time() - start < timeout:
        changes = module_collapse_iteration(mG)
        if not changes:
            break
    else:
        raise e

    return mG
