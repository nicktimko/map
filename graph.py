import networkx as nx

# the unweighted, undirected sample graph from
# http://mapequation.org/apps/MapDemo.html

# unpartitioned: 4.53 bits
# optimized: 3.25 bits
# snowflakes: 6.53 bits
G = nx.Graph()
G.add_path([1, 2, 3, 4, 2, 5, 6, 2])
G.add_path([6, 4, 7, 8, 10, 7, 9, 10, 11, 9])
G.add_path([10, 12, 11, 13, 12])
G.add_path([8, 13, 25, 23, 24, 22, 23])
G.add_path([25, 22, 21, 20, 19, 21, 18, 16, 21])
G.add_path([8, 14, 15, 16, 14, 18])
G.add_path([17, 16, 19])
G.add_path([20, 16])
