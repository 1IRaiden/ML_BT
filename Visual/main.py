import networkx as nx
from Navigation import BuildNavMap2D, FindNavPath, Visual, AIManager
import numpy as np
from threading import Thread
from openpyxl import Workbook


def expand_list(position : list):
    length = len(position)
    _x = []
    _y = []
    for i, (x, y) in enumerate(position, start=1):
        if i < length:
            end_projection = position[i]
            data_X = np.linspace(x, end_projection[0], 6).tolist()
            data_Y = np.linspace(y, end_projection[1], 6).tolist()

            _x = _x + data_X
            _y = _y + data_Y

    return _x, _y


def main():
    src = np.random.randint(0, 99)
    while True:
        # Метод-заглушка для тестировая
        # if src % 1 == 0:
        #   node, typ = manager.set_unable_node()
        #   nav_map.set_status_node(graph_map, node, typ)

        # Пункт назначения определяет автоматически на рандом в данный момент
        dst = np.random.randint(0, 99)
        way = path.find_path_A(graph_map, src, dst)
        position = nav_map.get_coordinate_path(graph_map, way)

        #
        movement_x, movement_y = expand_list(position)

        # for x, y in zip(movement_x, movement_y):
        #    vis.update(x, y)

        src = dst



if __name__ == "__main__":
    nav_map = BuildNavMap2D(10, 12)
    graph_map = nav_map.get_graph()
    nav_map.add_nodes(graph_map)
    nav_map.add_nav_edge(graph_map)
    nav_map.add_nav_diagonal_grid(graph_map)

    # vis = Visual()

    manager = AIManager()



    path = FindNavPath()
    main()



'''
src = np.random.randint(0, 99)
    while True:
        dst = np.random.randint(0, 99)
        way = path.find_path_A(graph_map, src, dst)
        position = nav_map.get_coordinate_path(graph_map, way)
        movement_x, movement_y = expand_list(position)

        # nav_map.visual_path(graph_map, way)
        for x, y in zip(movement_x, movement_y):
            vis.update(x, y)

        src = dst
        '''
