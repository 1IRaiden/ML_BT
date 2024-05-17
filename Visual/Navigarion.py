import networkx as nx
from matplotlib import pyplot as plt
import random


class BuildNavMap2D:
    def __init__(self, length=10, width=10):
        self.LENGTH = length
        self.WIDTH = width
        self.amount_point = length*width
        self.colors = []
        self.edges = []
        self.position = {}

    # Get empty graph
    def get_graph(self):
        graph = nx.Graph()
        return graph

    # Get position node for graph
    def __get_position_node(self):
        points = []
        for x in range(0, self.LENGTH, 1):
            for z in range(0, self.WIDTH, 1):
                points.append((x, z))
        return points

    # Add nodes in graph
    # Возможные значения типа узла:
        # friendly
        # unfriendly
    def add_nodes(self, graph_map):
        points = self.__get_position_node()
        for i in range(self.amount_point):
            self.position[points[i]] = i
            graph_map.add_node(i, pos=points[i], type="friendly", weight=1)
        print(self.position)

    # Add Simple edge between all nodes in from grid
    def add_nav_edge(self, graph_map):
        for i in range(0, self.LENGTH, 1):
            for j in range(0, self.WIDTH, 1):
                count = self.WIDTH * i + j
                if count % self.WIDTH != (self.WIDTH-1):
                    graph_map.add_edge(count, count + 1, color='blue', weight= 1)
                if count < (self.LENGTH-1)*self.WIDTH:
                    graph_map.add_edge(count, count + self.WIDTH, color='blue', weight=1)

    def add_nav_diagonal_grid(self, graph_map):
        for i in range(1, self.LENGTH-1, 1):
            for j in range(1, self.WIDTH-2, 1):
                first_node = self.position[(i, j)]
                second_node = self.position[(i+1, j+1)]
                if i>=2:
                    three_node = self.position[(i-1, j+1)]
                    graph_map.add_edge(first_node, three_node, color='yellow', weight=1)
                if i< self.LENGTH-2:
                    graph_map.add_edge(first_node, second_node, color='yellow', weight=1)

    def add_nav_additionation_edge(self, graph_map: nx.Graph, amount: int):
        i = 1
        while i <= amount:
            first = random.randint(0, self.amount_point-1)
            second = random.randint(0, self.amount_point-1)
            neighbours = list(graph_map.neighbors(first))
            for neighbour in neighbours:
                if second == neighbour or second == first:
                    break
            node_a = graph_map.nodes[first]
            node_b = graph_map.nodes[second]
            pos_xa = node_a['pos'][0]
            pos_ya = node_a['pos'][1]
            pos_xb = node_b['pos'][0]
            pos_yb = node_b['pos'][1]
            if (pos_xa != pos_xb) and (pos_ya != pos_yb):
                graph_map.add_edge(first, second, color='blue', weight=1)
                i += 1

    # Draw 2d map is Graph
    def draw_map_2d(self, graph_map, fig):
        for u, v, data in graph_map.edges(data=True):
            self.colors.append(data.get('color'))
        pos = nx.get_node_attributes(graph_map, 'pos')
        nx.draw(graph_map, pos, with_labels=True, edge_color=self.colors)
        plt.show()

    # Этот метод негативные вершины делает либо доступными, либо не доступными
    def set_status_node(self, graph_map: nx.Graph, node: int, typ: str):
        weight = 1
        graph_map.nodes[node]['type'] = typ
        neighbours = graph_map.neighbors(node)
        if typ == 'unfriendly':
            weight = 100000
            self.__set_weight_edge(graph_map, node, neighbours, weight, 'orange')
        elif typ == 'friendly':
            self.__set_weight_edge(graph_map, node, neighbours, weight, 'blue')

    def __set_weight_edge(self, G, node, others: list[int], weight, color):
        for other in others:
            G[other][node]['weight'] = weight
            graph_map[node][other]['color'] = color

    # Get change color for edges
    def visual_path(self, graph_map: nx.Graph, get_path: list):
        length_path = len(get_path)
        for i in range(0, length_path-1, 1):
            graph_map[get_path[i]][get_path[i + 1]]['color'] = 'red'


class FindNavPath:
    def __init__(self):
        pass
    def heuristic_func(self, a, b, G):
        x1, y1 = G.nodes[a]['pos']
        x2, y2 = G.nodes[b]['pos']
        return ((x1-x2)**2+(y1-y2)**2)**0.5

    def find_path_A(self, g: nx.Graph, node_A, node_B):
        path_a_b = nx.astar_path(g, node_A, node_B, heuristic=lambda a, b: self.heuristic_func(a, b, g), weight='weight')
        return path_a_b



if __name__ == "__main__":
    nav_map = BuildNavMap2D(10, 12)
    graph_map = nav_map.get_graph()
    nav_map.add_nodes(graph_map)
    nav_map.add_nav_edge(graph_map)
    nav_map.add_nav_diagonal_grid(graph_map)
    # nav_map.add_nav_additionation_edge(graph_map, 25)

    nav_map.set_status_node(graph_map, 55, 'unfriendly')
    nav_map.set_status_node(graph_map, 53, 'unfriendly')
    nav_map.set_status_node(graph_map, 53, 'unfriendly')

    path = FindNavPath()
    way = path.find_path_A(graph_map, 11, 74)

    nav_map.visual_path(graph_map, way)

    fig = plt.figure(figsize= (20, 20))
    nav_map.draw_map_2d(graph_map, fig)