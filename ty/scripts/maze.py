import sys
import re

import networkx as nx

known_edges = """
1 2
2 3
3 5
5 8
8 13
"""
edges = """
1 2,7
2 1,3,14
3 5,6
4 6,8
5 3,8,10
6 1,4,10,11
7 1,2,9
8 10,13,15
9 5,7,10
10 7,11,12
11 2,3,6,9
12 4,5,7
13 8,12
14 15
15 11,16
16 13
"""
edge_data = []
for a, bs in re.findall(r'(?m)^(\d+) ([\d,]+)$', known_edges + edges):
    for b in bs.split(","):
        a = int(a)
        b = int(b)
        if a == b:
            continue
        edge_data.append([a, b])

g = nx.DiGraph()
g.add_edges_from(edge_data)

start = 1
end = 13
if len(sys.argv) > 1:
    start = int(sys.argv[1])
if len(sys.argv) > 2:
    end = int(sys.argv[2])
print(nx.shortest_path(g, start, end))
