import threading
import time
from ML_Behaviour.creatingBT import Agent
from ML_BT.ML_Behaviour.BTAgents import AIManagerBlackboard
from ML_BT.SystemNavigation.ManagerMovement import AIManager
from ML_BT.SystemNavigation.Navigation import BuildNavMap2D, FindNavPath, BuildNavMap3D
from ML_BT.Vehicle.Vehicle import Car, Drone
from Config import HAS_DRONE_IN_GAME, HAS_CARS_IN_GAMES


path = 'Example BT/config.json'
path_box = r'C:\Users\user\Desktop\Проекты\MachineLeaning\MachineLearning\ML_BT\Example BT\config_box.json'


graph_map = None
graph_map_2d = None

if __name__ == "__main__":
    # Initialization 2D map
    if HAS_CARS_IN_GAMES:
        nav_map = BuildNavMap2D(10, 12)
        graph_map = BuildNavMap2D.get_graph()
        nav_map.add_nodes(graph_map)
        nav_map.add_nav_edge(graph_map)
        nav_map.add_nav_diagonal_grid(graph_map)
        position_obstacle = AIManager.get_position_obstacle()
        nodes = nav_map.find_not_comfortable_node(position_obstacle)

        for node in nodes:
            BuildNavMap2D.set_status_node(graph_map, node, "unfriendly")

    # Initiation 3D map
    if HAS_DRONE_IN_GAME:
        nav_map_2d = BuildNavMap3D(10, 10, 4)
        graph_map_2d = BuildNavMap3D.get_graph()
        nav_map_2d.add_nodes(graph_map_2d)
        nav_map_2d.add_nav_edge(graph_map_2d)
        nav_map_2d.add_nav_diagonal_grid(graph_map_2d)

    # Initialization cars and blackboard for save data
    all_game_obj = 6
    amount_agents_car = 3
    ai = AIManagerBlackboard()
    ai.add_all_status_cars(amount_agents_car)

    agents = []
    threads = []

    manager = AIManager()

    # This thread will be follow game and do request on server
    ai_thread = threading.Thread(target=manager.start_manager, args=(path_box, ai))
    ai_thread.start()

    start_positions = manager.get_start_position_from_config(path)

    for i in range(amount_agents_car):
        car = Car(i)
        # car = Drone(i)
        car.YOUR_POSITION = start_positions[i]

        agent = Agent(i, graph_map, car)
        # agent.create_behaviour_tree()
        agents.append(agent)
        thread = threading.Thread(target=agent.start_tick)
        threads.append(thread)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()