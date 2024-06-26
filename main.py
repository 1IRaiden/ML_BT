import threading
import json
from ML_Behaviour.creatingBT import Agent
from ML_BT.SystemNavigation.ManagerMovement import AIBehaviour
from ML_BT.ML_Behaviour.BTAgents import AIManagerBlackboard
from ML_BT.SystemNavigation.Navigation import BuildNavMap2D, BuildNavMap3D
from ML_BT.Vehicle.Vehicle import Car, Drone
from Config import AMOUNT_CAR, ALL_AI_OBJECT, TypeObject
from ML_BT.Web_Core.Requester import Core, Researcher


# Ссылки на навигационную карту 2D и 3D
graph_map = None
graph_map_3d = None


if __name__ == "__main__":
    # Класс Core позволяет взаимодейсвовать с сервером и отпрпавлять ему команды - в результате мы будет получать json данные
    core = Core()

    # Простейшая черная доска для записи и синхронизации переменных состояниях
    ai = AIManagerBlackboard()

    # Мои данные для теста и отслеживания состояниях при различных значениях переменных
    path = 'game_core.json'
    my_commands = 'Red'

    with open(path, 'r') as file:
        data = json.load(file)

    # В данный момент мы получаем все данные
    home_positions, my_positions_ids, recharge_position, types_object = Researcher.get_config_information(data,
                                                                                                          my_commands)
    round_home_position = []
    for home_position in home_positions:
        x, y, z = home_position
        round_home_position.append([round(x), round(y), round(z)])

    # Получаем данные о кол-ве дронов и машинок
    cars_index = []
    pioneer_index = []
    for i, typ in enumerate(types_object):
        if typ == TypeObject.geo_car.value[0]:
            AMOUNT_CAR += 1
            cars_index.append(my_positions_ids[i])
        else:
            pioneer_index.append(my_positions_ids[i])
        ALL_AI_OBJECT += 1

    if AMOUNT_CAR > 0:
        Agent.HAS_CARS_IN_GAMES = True

    amount_drone = ALL_AI_OBJECT - AMOUNT_CAR
    if amount_drone > 0:
        Agent.HAS_DRONE_IN_GAME = True

    # Adding information about future agents on blackboard
    ai.add_recharge_information(recharge_position[0], recharge_position[1])
    ai.add_home_position(my_positions_ids, home_positions)
    ai.set_status_all_drone_landing(pioneer_index)
    ai.set_main_status_for_game_object(my_positions_ids)

    # В данный момент главный класс, который будет описывать логику игры исходях полученныз данных в json
    behaviour = AIBehaviour(core, my_positions_ids)
    behaviour.set_amounts_parameters(pioneer_index, cars_index)

    # Initialization 2D map
    if Agent.HAS_CARS_IN_GAMES:
        nav_map = BuildNavMap2D(10, 12)
        graph_map = BuildNavMap2D.get_graph()
        nav_map.add_nodes(graph_map)
        nav_map.add_nav_edge(graph_map)
        nav_map.add_nav_diagonal_grid(graph_map)
        position_obstacle = Researcher.get_obstacle_position()
        nodes = nav_map.find_not_comfortable_node(position_obstacle)

        for node in nodes:
            BuildNavMap2D.set_status_node(graph_map, node, "unfriendly")

    # Initiation 3D map
    if Agent.HAS_DRONE_IN_GAME:
        nav_map_3d = BuildNavMap3D(6, 6, 6)
        graph_map_3d = BuildNavMap3D.get_graph()
        nav_map_3d.add_nodes(graph_map_3d)
        nav_map_3d.add_nav_edge(graph_map_3d)
        nav_map_3d.add_nav_diagonal_grid(graph_map_3d)

    # Set navigation map as main from movement
    Agent.set_nav_map_for_game(nav_map_2d=graph_map, nav_map_3d=graph_map_3d)

    agents = []
    threads = []

    # Creation game_object : drones and cars
    # Так же здесь создаются агенты - именно они создают деревья поведения и воспроизводят тики для перехода из одного состояния в другое
    # 2d agent
    if Agent.HAS_CARS_IN_GAMES:
        for number_car in range(AMOUNT_CAR):
            car = Car(cars_index[number_car])
            agent = Agent(car)
            agents.append(agent)
            thread = threading.Thread(target=agent.start_tick)
            threads.append(thread)

    # 3d agent
    if Agent.HAS_DRONE_IN_GAME:
        for number_drone in range(amount_drone):
            drone = Drone(pioneer_index[number_drone])
            agent = Agent(drone)
            agents.append(agent)
            thread = threading.Thread(target=agent.start_tick)
            threads.append(thread)

    # Создаем поток для упралвения игровой логикой
    beh = threading.Thread(target=behaviour.start_behaviour, args = (data,))
    beh.start()

    # Запускаем всех агентов
    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()
