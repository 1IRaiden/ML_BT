import networkx as nx
from matplotlib import pyplot as plt


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


LENGTH = 10
WIDTH = 10
COUNT_POINT = LENGTH*WIDTH


points = []
for x in range(LENGTH):
    for y in range(WIDTH):
        point = Point(y, x)
        points.append(point)

G = nx.Graph()
for i in range(COUNT_POINT):
    G.add_node(i, point=points[i])

for i in range(0, LENGTH, 1):
    for j in range(0, WIDTH, 1):
        count = 10*i+j
        if count%10 != 9:
            G.add_edge(count, count+1, color='blue')
        if count<90:
            G.add_edge(count, count+10, color='blue')

pos = {}
for x in range(LENGTH):
    for y in range(WIDTH):
        count = 10*x+y
        pos[count] = (y, x)
        G.nodes[count]['pos'] = (y, x)

print(list(G.neighbors(4)))
result = nx.astar_path(G, 42, 85)

for i, item in enumerate(result):
    if i < len(result)-1:
        G.remove_edge(result[i], result[i+1])
        G.add_edge(result[i], result[i+1], color='red')

edges = G.edges
colors = [G[u][v]['color'] for u, v in edges]

fig = plt.figure(figsize=(10, 8))
nx.draw(G, pos, with_labels=True, edge_color=colors)
plt.show()

