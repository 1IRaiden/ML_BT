import random
import threading
import time
import numpy as np


class AIManager:
    _instance = None
    car_positions = {}
    event = threading.Event()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(AIManager, cls).__new__(cls, *args, *kwargs)
        return cls._instance

    @staticmethod
    def get_start_position_from_config():
        start_position = (0, 0)
        return start_position

    @classmethod
    def get_event_status(cls):
        return cls.event.is_set()

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
        cls.event.set()
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



