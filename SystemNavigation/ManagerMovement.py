import json
import random
import threading
import time
import typing
import numpy as np
import json


class AIManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(AIManager, cls).__new__(cls, *args, *kwargs)
        return cls._instance

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
            pos_box_1 = container['box_1']
            pos_box_2 = container['box_2']
            pos_box_3 = container['box_3']
            pos = [pos_box_1, pos_box_2, pos_box_3]
            pos_boxs.extend(pos)

            box_1_reward = container['reward_1']
            box_2_reward = container['reward_2']
            box_3_reward = container['reward_3']
            reward = [box_1_reward, box_2_reward, box_3_reward]
            rewards.extend(reward)
        return pos_boxs, rewards

    def set_unable_node(self):
        node = np.random.randint(0, 99)
        typ = random.choice(('friendly', 'unfriendly'))
        return node, typ

    @classmethod
    def update_position_cars(cls, _id, x, y):
        AIManager.car_positions[_id] = (x, y)

    def get_position_players(self):
        pass

    @classmethod
    def is_safe(cls):
        while True:
            # AIManager.event.clear()
            if cls.__evaluate_distance_between_object():
                pass
            else:
                print("situation not safe")
            time.sleep(2)
            print(cls.event.is_set())

    @staticmethod
    def get_position_obstacle():
        pos_obstacle = ((2.4, 2.6), (1.1, 1.6), (2.3, 1.4), (6.5, 7.8))
        return pos_obstacle

    @classmethod
    def __evaluate_distance_between_object(cls) -> bool:
        coordinates = list(cls.car_positions.values())
        points = np.array(coordinates, dtype=np.float32)
        dist_matrix = np.linalg.norm(points[:, np.newaxis, :] - points[np.newaxis, :, :], axis=2)
        if np.all(dist_matrix > 0.5):
            return True
        else:
            return False



