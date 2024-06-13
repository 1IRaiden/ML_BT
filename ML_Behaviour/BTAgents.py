from py_trees import blackboard
from py_trees import common
import typing

''' This class is needed to synchronize data on the blackboard, 
since during the game we need to know about all the states of game objects

main parameters: 
1. is_keeper{amount_agents_car}_box
2. attack{amount_agents_car}
3. has_cargo{amount_agents_car}
4. need_recharge{amount_agents_car}
5. free_recharge{1}
6. amount_patrons{amount_agents_car}
7. dst{amount_agents_car}
8. route{amount_agents_car}
9. pos_box{number}
10. car_start_position{number}
11. reward_box{i}
12. car_current_position{i}

'''


class AIManagerBlackboard:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(AIManagerBlackboard, cls).__new__(cls, *args, *kwargs)
            cls._instance.writer = AIManagerBlackboard.__create_blackboard_client()
        return cls._instance

    @staticmethod
    def __create_blackboard_client() -> blackboard.Blackboard:
        writer = blackboard.Blackboard()
        return writer

    @classmethod
    def add_all_status_cars(cls, amount_agents_car: int):
        for i in range(amount_agents_car):
            # parament show can body get box
            cls._instance.writer.set(variable_name=f"is_keeper{i}_box", value=False)

            # parameter show can body do attack
            cls._instance.writer.set(variable_name=f"attack{i}", value=False)

            # parameter show has body box or not
            cls._instance.writer.set(variable_name=f"has_cargo{i}", value=False)

            # parameters show need body recharge or not
            cls._instance.writer.set(variable_name=f"need_recharge{i}", value=False)

            # parameters show how many patron have
            cls._instance.writer.set(variable_name=f"amount_patrons{i}", value=3)

            # parameters show have free recharge or not
        cls._instance.writer.set(variable_name=f"free_recharge{1}", value=False)
        cls._instance.writer.set(variable_name=f"free_recharge{2}", value=False)

    @classmethod
    def add_key(cls, name: str, value: typing.Any = False):
        cls._instance.writer.set(variable_name=name, value=value)

    @classmethod
    def change_value_key_blackboard(cls, key: str, value: typing.Any):
        cls._instance.writer.set(variable_name= key, value= value)

    @classmethod
    def set_dst_position(cls, id_car):
        cls._instance.writer.set(variable_name=f"dst_pos{id_car}", value=None)

    @classmethod
    def set_src_position(cls, id_car):
        cls._instance.writer.set(variable_name=f"src_pos{id_car}", value=None)

    @classmethod
    def get_value_key_blackboard(cls, key: str) -> typing.Any:
        return cls._instance.writer.get(key)


class HandlerLogic:
    @staticmethod
    def find_the_best_box(self, position_box, rewards: list[float]):
        sort_reward = sorted(rewards)

        for reward in sort_reward:
            pass
        #     return position






