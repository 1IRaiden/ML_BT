import threading
from ML_Behaviour import CarAction, BTAgents
from ML_BT.ML_Behaviour.BTAgents import AIManagerBlackboard


if __name__ == "__main__":
    amount_agents_car = 3
    ai = AIManagerBlackboard()
    ai.add_all_status_cars(amount_agents_car)
    agents = []
    threads = []

    for i in range(amount_agents_car):
        agent = CarAction.Agent(i)
        agent.create_behaviour_tree()
        agents.append(agent)
        thread = threading.Thread(target=agent.start_tick)
        threads.append(thread)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()