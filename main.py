import time
from SystemNavigation.Navigation import BuildNavMap2D, FindNavPath
from SystemNavigation.ManagerMovement import AIManager
import numpy as np
from ML_BT.Vehicle.Vehicle import Car
import concurrent.futures


def expand_list(position: list):
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


def main(game_car):
    game_car.set_connection('localhost', f'{8000 + game_car.id}')
    time.sleep(1)

    # game_car.include_arm()
    src = np.random.randint(0, 99)

    while True:
        # Метод-заглушка для тестировая
        # if src % 1 == 0:
        #   node, typ = manager.set_unable_node()
        #   nav_map.set_status_node(graph_map, node, typ)

        # Пункт назначения определяет автоматически на рандом в данный момент
        dst = np.random.randint(0, 99)
        way = FindNavPath.find_path_A(graph_map, src, dst)
        position = BuildNavMap2D.get_coordinate_path(graph_map, way)

        for pos in position:
            game_car.move_for_target(game_car.id, pos[0], pos[1], 0)

        src = dst


if __name__ == "__main__":
    nav_map = BuildNavMap2D(10, 12)
    graph_map = BuildNavMap2D.get_graph()
    nav_map.add_nodes(graph_map)
    nav_map.add_nav_edge(graph_map)
    nav_map.add_nav_diagonal_grid(graph_map)

    amount_vehicle = 2
    manager = AIManager()

    # Obstacle position -- this info will be taken from data
    position_obstacle = AIManager.get_position_obstacle()
    nodes = nav_map.find_not_comfortable_node(position_obstacle)

    for node in nodes:
        BuildNavMap2D.set_status_node(graph_map, node, "unfriendly")

    cars = []
    for i in range(amount_vehicle):
        car = Car(i)
        car.YOUR_POSITION = manager.get_start_position_from_config()
        AIManager.car_positions[car.id] = (car.x, car.y)
        cars.append(car)

    # fig = plt.figure(figsize=(15, 15))
    # nav_map.draw_map_2d(graph_map, fog)

    with concurrent.futures.ThreadPoolExecutor(max_workers=amount_vehicle + 1 ) as executor:
        futures_cars = [executor.submit(main, cars[i]) for i in range(amount_vehicle)]
        ai_sub = [executor.submit(AIManager.is_safe)]

        futures = ai_sub+futures_cars
        for future_car in concurrent.futures.as_completed(futures):
            print(future_car.result())











# movement_x, movement_y = expand_list(position)
# for x, y in zip(movement_x, movement_y):
#   vis.update(x, y)






