import time
import numpy as np
from ML_BT.Vehicle.Vehicle import Car, Drone
from py_trees.behaviour import Behaviour
from py_trees.common import Status
from py_trees.composites import Sequence, Parallel, Selector
from py_trees import common
import py_trees.decorators as de
from py_trees.trees import BehaviourTree
from py_trees import blackboard
from pioneer_sdk import Pioneer
from ML_BT.ML_Behaviour.BTAgents import AIManagerBlackboard
from ML_BT.SystemNavigation.Navigation import BuildNavMap2D, FindNavPath, BuildNavMap3D


class Nav3D:
    def __init__(self, nav_map):
        self.map = nav_map


class InitiateDr(Behaviour):
    def __init__(self, name, drone: Drone):
        super().__init__(name)
        self.drone = drone

    def update(self):
        self.drone.set_connection('localhost', f'{8000 + self.drone.id}')
        # self.drone.include_arm()
        time.sleep(3)
        return Status.SUCCESS


class TakeOff(Behaviour):
    def __init__(self, name, drone: Drone):
        super().__init__(name)
        self.drone = drone

    def update(self) -> common.Status:
        if not False:
            self.drone.takeoff()
            time.sleep(2)

        return Status.SUCCESS


class Landing(Behaviour):
    def __init__(self, name, drone: Drone):
        super().__init__(name)
        self.drone = drone

    def update(self) -> common.Status:
        self.drone.land()
        return Status.SUCCESS


class MovementDr(Behaviour, Nav3D):
    def __init__(self, name, drone: Drone, graph_map, is_keeper=False):
        Behaviour.__init__(self, name)
        Nav3D.__init__(self, graph_map)
        self.time_movement = 7
        self.is_keeper = is_keeper
        self.game_car = drone
        self.src = 1
        self.dst = None
        self.real_dst = None

    def update(self):
        if not self.dst:
            dst = np.random.randint(0, 400)
            way = FindNavPath.find_path_A_3D(self.map, self.src, dst)
            self.src = dst
            position = BuildNavMap3D.get_coordinate_path(self.map, way)
            self.dst = position
            self.real_dst = position.copy()

        if self.is_keeper:
            return Status.SUCCESS

        start_time = time.time()
        idx_max = 0
        for i, pos in enumerate(self.dst):
            self.game_car.move_for_target(self.game_car.id, pos[0], pos[1], pos[2])
            idx_max = i
            end_time = time.time()
            if (end_time - start_time) > self.time_movement:
                break

        self.real_dst = self.real_dst[idx_max + 1:]
        self.dst = self.real_dst.copy()

        return Status.RUNNING


class MoveToTargetDr(Behaviour, Nav3D):
    def __init__(self, name, drone: Drone, is_keeper: bool, graph_map, current_position: list[float] = (0, 0)):
        Behaviour.__init__(self, name=name)
        Nav3D.__init__(self, nav_map=graph_map)
        self.game_car = drone
        self.src = current_position
        self.is_keeper = is_keeper
        self.has_cargo = False
        self.dst = None
        self.target_position = None

    def update(self) -> common.Status:
        if not self.is_keeper:
            return Status.FAILURE

        src = None
        dst = None
        if not self.dst:
            self.has_cargo = AIManagerBlackboard.get_value_key_blackboard(F'has_cargo{self.game_car.id}')
            if not self.has_cargo:
                self.target_position = AIManagerBlackboard.get_value_key_blackboard("pos_box2")
            else:
                self.target_position = self.game_car.YOUR_POSITION

            src = BuildNavMap3D.get_number_node_from_position(self.src)
            dst = BuildNavMap3D.get_number_node_from_position(self.target_position)
            print(src, dst)

        way = FindNavPath.find_path_A_3D(self.map, src, dst)
        position = BuildNavMap3D.get_coordinate_path(self.map, way)

        self.dst = position

        if self.is_keeper:
            for i, pos in enumerate(self.dst):
                self.game_car.move_for_target(self.game_car.id, pos[0], pos[1], pos[2])
                self.src = (pos[0], pos[1], pos[2])
            self.dst = []
            return Status.SUCCESS


class StopDr(Behaviour):
    def __init__(self, name):
        super().__init__(name)

    def update(self):
        time.sleep(2)
        return Status.SUCCESS


class AttackDr(Behaviour):
    def __init__(self, name):
        super().__init__(name)
    def update(self):
        print("Совершена удачная дрона атака")
        return Status.SUCCESS
        if self.need_attack:
            if self.amount > 1:
                print('Attack is done')
                self.amount -= 1
                self.t(self.amount)
            else:
                print('Attack is not done')
        else:
            print("attack not need")

        time.sleep(1)
        return Status.SUCCESS


class TakeCargoDr(Behaviour):
    def __init__(self, name, car):
        super().__init__(name)
        self.game_car = car

    def update(self):
        time.sleep(1)
        print('Cargo is taken')
        AIManagerBlackboard.change_value_key_blackboard(f"has_cargo{self.game_car.id}", True)
        return Status.SUCCESS


class GiveCargoDr(Behaviour):
    def __init__(self, name, drone: Drone):
        super().__init__(name)
        self.drone = drone

    def update(self):
        time.sleep(1)
        print('Cargo is given')
        AIManagerBlackboard.change_value_key_blackboard(f"has_cargo{self.drone.id}", False)
        return Status.SUCCESS


class Recharge(Behaviour):
    def __init__(self, name):
        super().__init__(name)
        self.time_recharge = 10

    def update(self):
        time.sleep(1)
        self.time_recharge -= 1
        if self.time_recharge <= 0:
            return Status.SUCCESS
        else:
            return Status.RUNNING


