import networkx as nx

class GraphPathFinder:
    def heuristic_func(self, a, b):
        x1, y1 = a
        x2, y2 = b
        return ((x1 - x2)*2 + (y1 - y2)*2)*0.5

    def find_path_A(self, g: nx.Graph, node_A, node_B):
        path_a_b = nx.astar_path(g, node_A, node_B, heuristic=self.heuristic_func)
        return path_a_b

# Создание графа и добавление узлов в виде координатных точек
g = nx.Graph()
g.add_edge((0, 0), (1, 1))
g.add_edge((1, 1), (2, 2))
g.add_edge((2, 2), (3, 3))

finder = GraphPathFinder()
try:
    path = finder.find_path_A(g, (0, 0), (3, 3))
    print("Путь между узлами:", path)
except nx.NodeNotFound:
    print("Один из узлов не найден в графе.")
except nx.NetworkXNoPath:
    print("Между узлами нет пути.")