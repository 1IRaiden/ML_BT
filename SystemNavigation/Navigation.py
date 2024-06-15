import time
import networkx as nx
from matplotlib import pyplot as plt
import random


class BuildNavMap2D:
    position = {}

    def __init__(self, length=10, width=10):
        self.LENGTH = length
        self.WIDTH = width
        self.amount_point = length*width
        self.colors = []    
        self.edges = []
        self.position = {}

    # Get empty graph
    @staticmethod
    def get_graph():
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
    # Possible values of the node
        # friendly
        # unfriendly

    def add_nodes(self, graph_map):
        points = self.__get_position_node()
        for i in range(self.amount_point):
            self.position[points[i]] = i
            BuildNavMap2D.position[points[i]] = i
            graph_map.add_node(i, pos=points[i], type="friendly", weight=1)

    # Add Simple edge between all nodes in from grid
    def add_nav_edge(self, graph_map):
        for i in range(0, self.LENGTH, 1):
            for j in range(0, self.WIDTH, 1):
                count = self.WIDTH * i + j
                if count % self.WIDTH != (self.WIDTH-1):
                    graph_map.add_edge(count, count + 1, color='blue', weight=1)
                if count < (self.LENGTH-1)*self.WIDTH:
                    graph_map.add_edge(count, count + self.WIDTH, color='blue', weight=1)

    def add_nav_diagonal_grid(self, graph_map):
        for i in range(1, self.LENGTH-1, 1):
            for j in range(1, self.WIDTH-2, 1):
                first_node = self.position[(i, j)]
                second_node = self.position[(i+1, j+1)]
                if i >= 2:
                    three_node = self.position[(i-1, j+1)]
                    graph_map.add_edge(first_node, three_node, color='yellow', weight=1)
                if i < self.LENGTH-2:
                    graph_map.add_edge(first_node, second_node, color='yellow', weight=1)

    # This method will be changed
    def __add_nav_addition_edge(self, graph_map: nx.Graph, amount: int):
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

    # This method doing vertices or unavailable or good
    @staticmethod
    def set_status_node(graph_map: nx.Graph, node: int, typ: str):
        weight = 1
        graph_map.nodes[node]['type'] = typ
        neighbours = graph_map.neighbors(node)
        if typ == 'unfriendly':
            weight = 100000
            BuildNavMap2D.__set_weight_edge(graph_map, node, neighbours, weight=weight, color='orange')
        elif typ == 'friendly':
            BuildNavMap2D.__set_weight_edge(graph_map, node, neighbours, weight, 'blue')

    @staticmethod
    def __set_weight_edge(graph, node, others: list[int], weight, color):
        for other in others:
            graph[other][node]['weight'] = weight
            graph[node][other]['color'] = color

    # Get change color for edges
    @staticmethod
    def __visual_path(graph_map: nx.Graph, get_path: list):
        length_path = len(get_path)
        for i in range(0, length_path-1, 1):
            graph_map[get_path[i]][get_path[i + 1]]['color'] = 'red'

    @staticmethod
    def get_coordinate_path(graph_map, way):
        coordinate = []
        for wa in way:
            position = graph_map.nodes[wa]['pos']
            coordinate.append(position)
        return coordinate

    def find_not_comfortable_node(self, position_obstacles):
        nodes = []
        for pos_obstacles in position_obstacles:
            a = round(pos_obstacles[0])
            b = round(pos_obstacles[1])
            node = self.position[(a, b)]
            nodes.append(node)
        return nodes

    @staticmethod
    def get_number_node_from_position(pos: list):
        a = round(pos[0])
        b = round(pos[1])
        node = BuildNavMap2D.position[(a, b)]
        return node


class FindNavPath:
    def __init__(self):
        pass

    @staticmethod
    def __heuristic_func(a, b, G):
        x1, y1 = G.nodes[a]['pos']
        x2, y2 = G.nodes[b]['pos']
        return ((x1-x2)**2+(y1-y2)**2)**0.5

    @staticmethod
    def __heuristic_func_3d(a, b, G):
        x1, y1, z1 = G.nodes[a]['pos']
        x2, y2, z2 = G.nodes[b]['pos']
        return ((x1-x2)**2+(y1-y2)**2 +(z1-z2)**2)**0.5

    @staticmethod
    def find_path_A(g: nx.Graph, node_A, node_B):
        path_a_b = nx.astar_path(g, node_A, node_B, heuristic=lambda a, b: FindNavPath.__heuristic_func(a, b, g), weight='weight')
        return path_a_b

    @staticmethod
    def find_path_A_3D(g: nx.Graph, node_A, node_B):
        path_a_b = nx.astar_path(g, node_A, node_B, heuristic=lambda a, b: FindNavPath.__heuristic_func_3d(a, b, g), weight='weight')
        return path_a_b


class Visual:
    def __init__(self):
        self.fig, self.ax = plt.subplots()
        self.ax.grid()

    def update(self, data_x, data_y):
        self.ax.scatter(data_x, data_y, color = 'r')
        self.ax.set_xlim(-1, 12)
        self.ax.set_ylim(-1, 12)
        plt.draw()
        plt.pause(0.05)
        plt.cla()


class BuildNavMap3D:
    position = {}
    def __init__(self, length=10, width=10, height=4):
        self.LENGTH = length
        self.WIDTH = width
        self.HEIGHT = height
        self.amount_point = length*width*height
        self.colors = []
        self.edges = []
        self.position = {}

        # Get empty graph

    @staticmethod
    def get_graph():
        graph = nx.Graph()
        return graph

        # Get position node for graph

    def __get_position_node(self):
        points = []
        for y in range(0, self.HEIGHT, 1):
            for x in range(0, self.LENGTH, 1):
                for z in range(0, self.WIDTH, 1):
                    points.append((x, y, z))
        return points

    def add_nodes(self, graph_map):
        points = self.__get_position_node()
        for i in range(self.amount_point):
            self.position[points[i]] = i
            BuildNavMap3D.position[points[i]] = i
            graph_map.add_node(i, pos=points[i], type="friendly", weight=1)

    def add_nav_edge(self, graph_map):
        for y in range(0, self.HEIGHT, 1):
            for x in range(self.LENGTH):
                for h in range(self.WIDTH):
                    if x < self.LENGTH-1:
                        vertical_a = self.position[(x, y, h)]
                        vertical_b = self.position[(x + 1, y, h)]
                        graph_map.add_edge(vertical_a, vertical_b)
                    if h < self.WIDTH-1:
                        vertical_ay = self.position[(x, y, h)]
                        vertical_by = self.position[(x, y, h+1)]
                        graph_map.add_edge(vertical_ay, vertical_by)
                    if y < self.HEIGHT-1:
                        vertical_az = self.position[(x, y, h)]
                        vertical_bz= self.position[(x, y + 1 , h)]
                        graph_map.add_edge(vertical_az, vertical_bz)

    def add_nav_diagonal_grid(self, graph_map):
        for y in range(0, self.HEIGHT, 1):
            for x in range(self.LENGTH):
                for h in range(self.WIDTH):
                    if x < self.WIDTH-1 and y < self.HEIGHT-1:
                        vertical_a = self.position[(x, y, h)]
                        vertical_b = self.position[(x + 1, y + 1, h)]
                        graph_map.add_edge(vertical_a, vertical_b)

                    if h > 0 and x < self.LENGTH-1 and y < self.HEIGHT-1:
                        vertical_ay = self.position[(x, y, h)]
                        vertical_by = self.position[(x + 1, y + 1, h-1)]
                        graph_map.add_edge(vertical_ay, vertical_by)

                    if x > 0 and h < self.WIDTH-1 and y < self.HEIGHT-1:
                        vertical_az = self.position[(x, y, h)]
                        vertical_bz = self.position[(x - 1, y + 1, h + 1)]
                        graph_map.add_edge(vertical_az, vertical_bz)

                    if x > 0 and y > 0 and h > 0:
                        if x > self.LENGTH-1 and h < self.WIDTH-1 and y < self.HEIGHT-1:
                            vertical_az = self.position[(x, y, h)]
                            vertical_bz = self.position[(x - 1, y - 1, h + 1)]
                            graph_map.add_edge(vertical_az, vertical_bz)


    @staticmethod
    def get_number_node_from_position(pos: list):
        a = round(pos[0])
        b = round(pos[1])
        c = round(pos[2])
        node = BuildNavMap3D.position[(a, b, c)]
        return node

    # At this moment this function has not realisation, perhaps it be create new node for station or cargo
    def add_additional_vert(self, graph_map):
        pass

    @staticmethod
    def get_coordinate_path(graph_map, way):
        coordinate = []
        for wa in way:
            position = graph_map.nodes[wa]['pos']
            coordinate.append(position)
        return coordinate


if __name__ == '__main__':
    nav_map = BuildNavMap3D(10, 10, 4)
    graph_map = BuildNavMap3D.get_graph()
    nav_map.add_nodes(graph_map)
    nav_map.add_nav_edge(graph_map)
    nav_map.add_nav_diagonal_grid(graph_map)

    way = FindNavPath.find_path_A_3D(graph_map, 1, 233)
    position = BuildNavMap3D.get_coordinate_path(graph_map, way)

    fir = plt.figure(figsize=(10, 10))
    ax = fir.add_subplot(projection='3d')

    for i in range(len(position)-1):
        x =[position[i][0], position[i + 1][0]]
        y =[position[i][1], position[i + 1][1]]
        z =[position[i][2], position[i + 1][2]]
        ax.plot(x, y, z)

    print(position)
    plt.xlim(0, 10)
    plt.ylim(0, 4)
    t2 = time.time()

    plt.show()

















