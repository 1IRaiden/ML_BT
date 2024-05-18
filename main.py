import time
import matplotlib.pyplot as plt
import networkx as nx
from SystemNavigation.Navigation import BuildNavMap2D, FindNavPath, Visual
from SystemNavigation.ManagerMovement import AIManager
import numpy as np
from threading import Thread
from Vehicle.Vehicle import Car
import concurrent.futures


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


def main(car):
    car.set_connection('localhost', f'{8000 + car.id}')
    time.sleep(5)
    # car.include_arm()

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
        # print(f"Я машина {car.id} and my path: {way}")
        # Для более детальной визуализации траектории

        for pos in position:
            car.get_coordinate_position()
            car.movement(pos[0], pos[1], 0)

        src = dst


if __name__ == "__main__":
    nav_map = BuildNavMap2D(10, 12)
    graph_map = nav_map.get_graph()
    nav_map.add_nodes(graph_map)
    nav_map.add_nav_edge(graph_map)
    nav_map.add_nav_diagonal_grid(graph_map)

    amount_vehicle = 3

    manager = AIManager()
    path = FindNavPath()
    # vis = Visual()

    # Obstacle position -- this info will be taken from data
    pt = ((2.4, 2.6), (1.1, 1.6), (2.3, 1.4), (6.5, 7.8))
    nodes = nav_map.find_not_comfortable_node(pt)

    cars = []
    for i in range(amount_vehicle):
        car = Car(i)
        cars.append(car)
    fog = plt.figure(figsize=(15, 15))
    nav_map.draw_map_2d(graph_map, fog)
    with concurrent.futures.ThreadPoolExecutor(max_workers=amount_vehicle) as executor:
        futures = [executor.submit(main, cars[i]) for i in range(amount_vehicle)]
        for future in concurrent.futures.as_completed(futures):
            print(future.result())










# movement_x, movement_y = expand_list(position)
# for x, y in zip(movement_x, movement_y):
#   vis.update(x, y)






