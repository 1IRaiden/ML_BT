import random
import time
import typing
import numpy as np
import json
from ML_BT.ML_Behaviour.BTAgents import AIManagerBlackboard


class AIManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(AIManager, cls).__new__(cls, *args, *kwargs)
        return cls._instance

    def start_manager(self, path, ai_blackboard: AIManagerBlackboard):
        # time.sleep(10)
        while True:
            pos_boxs, rewards = AIManager.get_info_about_box(path)
            current_positions = AIManager.get_current_position_cars("Example BT/current_positions.json")

            for i, current_position in enumerate(current_positions):
                ai_blackboard.add_key(f"car_current_position{i}", current_position)
            AIManager.is_safe(current_positions)

            for i, pos_box in enumerate(pos_boxs, start=1):
                ai_blackboard.add_key(f"pos_box{i}", pos_box)

            for i, reward in enumerate(rewards, start=1):
                ai_blackboard.add_key(f"reward_box{i}", reward)

            time.sleep(2)

    @staticmethod
    def get_start_position_from_config(file: str):
        positions = []
        with open(file, 'r') as f:
            data: typing.Dict = json.load(f)
            for pos in data.values():
                positions.append(pos)
            return positions

    @staticmethod
    def get_info_about_box(path_reward: str):
        pos_boxs = []
        rewards = []
        with open(path_reward, 'r') as f:
            container = json.load(f)
            pos_box_1 = container['pos_box_1']
            pos_box_2 = container['pos_box_2']
            pos_box_3 = container['pos_box_3']
            pos = [pos_box_1, pos_box_2, pos_box_3]
            pos_boxs.extend(pos)

            box_1_reward = container['reward_1']
            box_2_reward = container['reward_2']
            box_3_reward = container['reward_3']
            reward = [box_1_reward, box_2_reward, box_3_reward]
            rewards.extend(reward)
        return pos_boxs, rewards

    @staticmethod
    def get_current_position_cars(js_file):
        current_positions = []
        with open(js_file, 'r') as f:
            all_pos = json.load(f)
            pos_curr_car_1 = all_pos["current_position_car_1"]
            pos_curr_car_2 = all_pos["current_position_car_2"]
            pos_curr_car_3 = all_pos["current_position_car_3"]
            po_currents = [pos_curr_car_1, pos_curr_car_2, pos_curr_car_3]
            current_positions.extend(po_currents)
        return current_positions

    @staticmethod
    def set_unable_node():
        node = np.random.randint(0, 99)
        typ = random.choice(('friendly', 'unfriendly'))
        return node, typ

    @classmethod
    def is_safe(cls, currents_position):
        if cls.__evaluate_distance_between_object(currents_position):
            return
        else:
            # Логика изменения координат
            print("situation not safe")

    @staticmethod
    def get_position_obstacle():
        pos_obstacle = ((2.4, 2.6), (1.1, 1.6), (2.3, 1.4), (6.5, 7.8))
        return pos_obstacle

    @classmethod
    def __evaluate_distance_between_object(cls, currents_position) -> bool:
        points = np.array(currents_position, dtype=np.float32)
        dist_matrix = np.linalg.norm(points[:, np.newaxis, :] - points[np.newaxis, :, :], axis=2)

        for i in range(len(dist_matrix)):
            for j in range(len(dist_matrix[i])):
                if i != j:
                    if dist_matrix[i][j] < 0.5:
                        return False
        return True


# MOTION PLANNING



