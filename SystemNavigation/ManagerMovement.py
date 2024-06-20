import sys
import numpy as np
import time
import typing
from ML_BT.Config import IF_FORWARD
from enum import Enum
from ML_BT.ML_Behaviour.BTAgents import AIManagerBlackboard
from ML_BT.Web_Core.Requester import Core, Researcher, BoxRegard
from collections import Counter
from dataclasses import dataclass, asdict
from abc import ABC


class Colors(Enum):
    color_one = (0, 0, 0)
    color_two = (1, 1, 1)
    color_three = (2, 2, 2)


class Template(ABC):
    def set_status(self, status: bool):
        pass

    def set_status_attack(self, status: bool):
        pass

    def reset(self):
        pass


@dataclass
class Model3D(Template):
    id: int
    ax1: int = 1500
    ax2: int = 1500
    ax3: int = 1500
    ax4: int = 0
    status: bool = False
    status_attack: bool = False

    def set_status(self, status: bool):
        self.status = status

    def set_status_attack(self, status: bool):
        self.status_attack = status

    def reset(self):
        self.ax1 = 1500
        self.ax2 = 1500
        self.ax3 = 1500
        self.ax4 = 0
        self.status = False
        self.status_attack = False


@dataclass
class Model2D(Template):
    id: int
    ax1: int = 1500
    ax2: int = 1500
    ax3: int = 0
    status: bool = False
    status_attack: bool = False

    def set_status(self, status: bool):
        self.status = status

    def set_status_attack(self, status: bool):
        self.status_attack = status

    def reset(self):
        self.ax1 = 1500
        self.ax2 = 1500
        self.ax3 = 0
        self.status = False
        self.status_attack = False


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
        self.current_positions = None
        self.nums_bullets = None
        self.amount_drone = None
        self.amount_car = None
        self.store : typing.Dict[int, typing.Union[Model2D, Model3D]] = {}

        self.attack_radius = 0.5
        self.amount_box = 3
        self.inaccuracy = 0.4
        self.P = 500
        self.time = 1

        # color chose cargo
        self.keeper: int = -1
        self.box: typing.Optional[BoxRegard] = None

        self.first = True

    def set_amounts_parameters(self, amount_drone: list, amount_car: list):
        self.amount_car = amount_car
        self.amount_drone = amount_drone

    def start_behaviour(self, data):
        for item in self.amount_car:
            inf = Model2D(item)
            self.store[item] = inf
            # print(self.store[item])

        for item in self.amount_drone:
            inf = Model3D(item)
            self.store[item] = inf
            # print(self.store[item])

        while True:
            time.sleep(self.time)
            # data = self.core.do_require_on_server()
            ids, current_positions, is_cargo, nums_bullet, is_blocked, color_team \
                = Researcher.current_position_players(data)

            position_recharge = Researcher.get_information_about_charges(data)
            for i, pos in enumerate(position_recharge):
                AIManagerBlackboard.set_recharge_position_station(i, pos)

            # logic amount bullets
            self.nums_bullets = nums_bullet
            self.set_status_num_bullets_on_blackboard()

            self.blocked = is_blocked
            self.__set_cargo_status_for_players(is_cargo)

            # logic choose box
            boxs: list[BoxRegard] = Researcher.get_position_cargos(data)
            self.current_positions = self.determine_attack_status(current_positions, is_blocked, ids)
            self.set_current_position_on_blackboard()

            if not IF_FORWARD:
                try:
                    self.determine_status_dst_from_game_object(current_positions)
                    if len(self.amount_drone) > 0:
                        for number_drone in self.amount_drone:
                            # takeoff
                            res_takeoff = AIManagerBlackboard.get_takeoff_status_drone(number_drone)
                            if res_takeoff:
                                self.store[number_drone].set_status(True)
                                # perhaps need delay ...
                                AIManagerBlackboard.set_takeoff_status_drone(number_drone, False)
                            else:
                                self.store[number_drone].set_status(False)

                            # landing
                            res_landing = AIManagerBlackboard.get_landing_status_drone(number_drone)
                            if res_landing:
                                self.store[number_drone].set_status(True)
                                # perhaps need delay ...
                                AIManagerBlackboard.set_landing_status_drone(number_drone, False)
                            else:
                                self.store[number_drone].set_status(False)
                            # logic using this parameters ...
                except Exception as e:
                    print(f"Возникла ошибка {e}")

            if self.first:
                self.choice_one_drones(boxs)
                self.first = not self.first

            # for item in self.my_position:
            #   print(self.store[item])

            if not self.check_has_cargo():

                '''In this case, the freedom of the cargo is checked, taking into account its location, 
                but it is quite possible that information about enemy objects will need to be used'''
                if self.box:
                    if not Researcher.status_for_keeper(data, self.box):
                        sys.stderr.write("Status was changed: Manager")
                        AIManagerBlackboard.set_keeper_status(self.keeper, False)
                        if not self.check_has_is_keeper():
                            self.choice_one_drones(boxs)

            for item in self.my_position:
                map_action = asdict(self.store[item])
                # Отправляем запрос с данными по json на сервер

            for item in self.my_position:
                self.store[item].reset()

    def set_status_num_bullets_on_blackboard(self):
        for idx in self.my_position:
            AIManagerBlackboard.set_amount_patrons_idx(idx, self.nums_bullets[idx])

    def set_current_position_on_blackboard(self):
        for idx in self.my_position:
            AIManagerBlackboard.set_current_position_idx(idx, self.current_positions[idx])

    def determine_attack_status(self, current_position: list, is_blocked: list[bool], ids: list):
        AIManagerBlackboard.set_status_need_recharge(9, True) ################
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
            if not is_blocked[couple[0]]:
                # We set the attack status in case of success and otherwise sets the status of the need to recharge
                if self.nums_bullets[couple[0]] > 0:
                    AIManagerBlackboard.set_attack_status_idx(couple[0], True)
                    self.store[couple[0]].set_status_attack(True)
                    AIManagerBlackboard.set_status_need_recharge(couple[0], False)
                else:
                    AIManagerBlackboard.set_status_need_recharge(couple[0], True)

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
            self.box = box
            self.keeper = idx
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

    def determine_status_dst_from_game_object(self, currents_positions: list):
        for i in self.my_position:
            # dst_position = AIManagerBlackboard.get_dst_position_idx(i)
            dst_position = AIManagerBlackboard.get_home_position(i)
            x, y, z = dst_position
            x1, y1, z1 = currents_positions[i]
            dx, dy, dz = abs(x1-x), abs(y1-y), abs(z1-z)
            dst_distance_square = dx**2+dy**2+dz**2
            inaccuracy = self.inaccuracy
            if dst_distance_square < inaccuracy:
                AIManagerBlackboard.set_status_reaching_dst_target(i, True)
            else:
                distance_vector = np.array([x-x1, y-y1, z-z1])
                length_distance_vector = np.linalg.norm(distance_vector)
                k = self.P / length_distance_vector

                project_x = (x - x1) * k
                project_y = (y - y1) * k
                project_z = (z - z1) * k

                ax1 = 1500 + project_x
                ax2 = 1500 + project_y
                ax3 = 1500 + project_z
                ax4 = 0

                if i in self.amount_car:
                    self.store[i].ax1 = round(ax1)
                    self.store[i].ax2 = round(ax2)
                    self.store[i].ax3 = ax4
                else:
                    self.store[i].ax1 = round(ax1)
                    self.store[i].ax2 = round(ax2)
                    self.store[i].ax3 = round(ax3)
                    self.store[i].ax4 = ax4

    def __set_cargo_status_for_players(self, is_cargo: list):
        for i in self.my_position:
            AIManagerBlackboard.set_status_has_cargo(i, is_cargo[i])

    def check_has_is_keeper(self):
        statuses_keeper = []
        for i in self.my_position:
            statuses_keeper.append(AIManagerBlackboard.get_is_keeper_idx_status(i))
        return any(statuses_keeper)

    def check_has_cargo(self):
        statuses_has_cargo = []
        for i in self.my_position:
            statuses_has_cargo.append(AIManagerBlackboard.get_has_cargo_idx_status(i))
        return any(statuses_has_cargo)


