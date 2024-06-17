import random
import time
import typing
from enum import Enum
import json
from ML_BT.ML_Behaviour.BTAgents import AIManagerBlackboard
from ML_BT.Web_Core.Requester import Core, Researcher, BoxRegard
from collections import Counter


class Colors(Enum):
    color_one = (0, 0, 0)
    color_two = (1, 1, 1)
    color_three = (2, 2, 2)


class AIBehaviour:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(AIBehaviour, cls).__new__(cls)
        return cls._instance

    def __init__(self, core: Core, my_indexes):
        self.core = core
        self.my_position = my_indexes
        self.blocked = None
        self.attack_radius = 0.5
        self.amount_box = 3
        self.nums_bullets = None
        self.current_positions = None

    def get_config_data(self):
        pass

    def start_behaviour(self, data):
        while True:
            # data = self.core.do_require_on_server()
            ids, current_positions, is_cargo, nums_bullet, is_blocked, color_team \
                = Researcher.current_position_players(data)

            self.nums_bullets = nums_bullet
            self.set_status_num_bullets_on_blackboard()

            self.blocked = is_blocked
            boxs: list[BoxRegard] = Researcher.get_position_cargos(data)

            self.current_positions = self.determine_attack_status(current_positions, is_blocked, ids)
            self.choice_one_drones(boxs)
            break

    def set_status_num_bullets_on_blackboard(self):
        for idx in self.my_position:
            AIManagerBlackboard.set_amount_patrons_idx(idx, self.nums_bullets[idx])

    def determine_attack_status(self, current_position: list, is_blocked: list[bool], ids: list):
        my_coordinates = {}
        enemy_coordinates = {}

        # get idx my and enemy
        set_my_pos = set(self.my_position)
        set_all = set(ids)
        common_elements = set_my_pos.intersection(set_all)
        set_all.difference_update(common_elements)

        enemy_ids = list(set_all)

        for i in self.my_position:
            my_coordinates[i] = current_position[i]

        for i in enemy_ids:
            enemy_coordinates[i] = current_position[i]

        couples = self.find_distance_between_game_object(my_coordinates, enemy_coordinates)
        for couple in couples:
            if is_blocked[couple[0]]:
                AIManagerBlackboard.set_attack_status_idx(couple[0], True)
        return my_coordinates

    def find_distance_between_game_object(self, my_coordinates: dict, enemy_coordinates: dict):
        indexes_two = []
        for i, my_pos in my_coordinates.items():
            for j, enemy_pos in enemy_coordinates.items():
                dx = abs(my_pos[0] - enemy_pos[0])
                dy = abs(my_pos[1] - enemy_pos[1])
                dz = abs(my_pos[2] - enemy_pos[2])

                if dx < self.attack_radius and dy < self.attack_radius:
                    couple = (i, j)
                    indexes_two.append(couple)

        return indexes_two

    def __auto_get_data(self, box):
        sorted_distance_xy_dict = self.find_nearly_game_object_key(box.current_position)
        idx = self.__find_object_not_blocked(sorted_distance_xy_dict)
        if idx:
            AIManagerBlackboard.set_keeper_status(idx, True)
            AIManagerBlackboard.set_box_reward_position(box.current_position)
            print(f"Назначен дрон с индексом {idx} и груз с цветом {box.color}")

    def choice_one_drones(self, box_info: list[BoxRegard]):
        statuses = []
        for box in box_info:
            statuses.append(box.is_cargo)

        counter = Counter(statuses)
        match counter[False]:
            case 3:
                for box in box_info:
                    if box.color == Colors.color_one.value:
                        self.__auto_get_data(box)
                        break
            case 2:
                FAR = True
                for box in box_info:
                    if box.color == Colors.color_one.value:
                        if not box.is_cargo:
                            self.__auto_get_data(box)
                            FAR = False
                            break
                if FAR:
                    for box in box_info:
                        if box.color == Colors.color_two.value:
                            if not box.is_cargo:
                                self.__auto_get_data(box)
                                FAR = False
                                break
                if FAR:
                    for box in box_info:
                        if box.color == Colors.color_three.value:
                            if not box.is_cargo:
                                self.__auto_get_data(box)
                                FAR = False
                                break
            case 1:
                for box in box_info:
                    if not box.is_cargo:
                        self.__auto_get_data(box)
                        break
            case _:
                print("Нет свободных грузов")

    def find_nearly_game_object_key(self, position_cargo):
        print(self.current_positions)
        distances_xy = {}
        for i, my_pos in self.current_positions.items():
            dx = abs(my_pos[0] - position_cargo[0])
            dy = abs(my_pos[1] - position_cargo[1])
            dz = abs(my_pos[2] - position_cargo[2])

            square_distance = dx**2 + dy**2
            distances_xy[i] = square_distance

        sorted_distance_xy = dict(sorted(distances_xy.items(), key=lambda item: item[1]))

        return sorted_distance_xy

    def __find_object_not_blocked(self, sorted_distance_xy_dict):
        for i, _ in sorted_distance_xy_dict.items():
            if not self.blocked[i]:
                return i
        return None









    '''


    @staticmethod
    def set_unable_node():
        node = np.random.randint(0, 99)
        typ = random.choice(('friendly', 'unfriendly'))
        return node, typ



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


    @classmethod
    def is_safe(cls, currents_position):
        if cls.__evaluate_distance_between_object(currents_position):
            return
        else:
            # Логика изменения координат
            print("situation not safe")



    '''

