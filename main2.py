import threading
from ML_Behaviour import CarAction, BTAgents
from ML_BT.ML_Behaviour.BTAgents import AIManagerBlackboard
from ML_BT.SystemNavigation.ManagerMovement import AIManager
from ML_BT.SystemNavigation.Navigation import BuildNavMap2D, FindNavPath
from ML_BT.Vehicle.Vehicle import Car
from ML_BT.ML_Behaviour.CarAction import Nav


path = 'Example BT/config.json'

if __name__ == "__main__":
    # Initialization map
    nav_map = BuildNavMap2D(10, 12)
    graph_map = BuildNavMap2D.get_graph()
    nav_map.add_nodes(graph_map)
    nav_map.add_nav_edge(graph_map)
    nav_map.add_nav_diagonal_grid(graph_map)

    position_obstacle = AIManager.get_position_obstacle()
    nodes = nav_map.find_not_comfortable_node(position_obstacle)

    for node in nodes:
        BuildNavMap2D.set_status_node(graph_map, node, "unfriendly")

    # Initialization cars and blackboard for save data
    amount_agents_car = 3
    ai = AIManagerBlackboard()
    ai.add_all_status_cars(amount_agents_car)

    agents = []
    threads = []

    manager = AIManager()
    start_positions = manager.get_start_position_from_config(path)

    for i in range(amount_agents_car):
        car = Car(i)
        car.YOUR_POSITION = start_positions[i]

        agent = CarAction.Agent(i, graph_map, car)
        agent.create_behaviour_tree()
        agents.append(agent)
        thread = threading.Thread(target=agent.start_tick)
        threads.append(thread)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()