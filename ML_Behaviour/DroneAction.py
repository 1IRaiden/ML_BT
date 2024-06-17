import time
import numpy as np
from ML_BT.Vehicle.Vehicle import Drone
from py_trees.behaviour import Behaviour
from py_trees.common import Status
from py_trees import common
from ML_BT.ML_Behaviour.BTAgents import AIManagerBlackboard
from ML_BT.SystemNavigation.Navigation import FindNavPath, BuildNavMap3D


def status_blocked(idx):
    status = AIManagerBlackboard.get_blocked_status_idx(idx)
    return status


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
        if status_blocked(self.drone.id):
            return Status.FAILURE
        landing = AIManagerBlackboard.get_drone_landing_idx_status(self.drone.id)
        if landing:
            print("Дрон взлетел")
            self.drone.takeoff()
            AIManagerBlackboard.set_status_drone_landing(self.drone.id, False)
            time.sleep(2)

        return Status.SUCCESS


class Landing(Behaviour):
    def __init__(self, name, drone: Drone):
        super().__init__(name)
        self.drone = drone

    def update(self) -> common.Status:
        status = AIManagerBlackboard.get_drone_landing_idx_status(self.drone.id)
        if not status:
            self.drone.land()
            AIManagerBlackboard.set_status_drone_landing(self.drone.id, True)
            print("Посадка дрона совершена")
            if status_blocked(self.drone.id):
                return Status.FAILURE
        return Status.SUCCESS


class MovementDr(Behaviour, Nav3D):
    def __init__(self, name, drone: Drone, graph_map):
        Behaviour.__init__(self, name)
        Nav3D.__init__(self, graph_map)
        self.time_movement = 7
        self.drone = drone
        self.src = 1
        self.dst = None
        self.real_dst = None

    def update(self):
        if not self.dst:
            dst = np.random.randint(0, 6*6*6)
            way = FindNavPath.find_path_A_3D(self.map, self.src, dst)
            self.src = dst
            position = BuildNavMap3D.get_coordinate_path(self.map, way)
            self.dst = position
            self.real_dst = position.copy()

        if AIManagerBlackboard.get_is_keeper_idx_status(self.drone.id):
            return Status.SUCCESS

        start_time = time.time()
        idx_max = 0
        for i, pos in enumerate(self.dst):
            if status_blocked(self.drone.id):
                return Status.FAILURE
            self.drone.move_for_target(self.drone.id, pos[0], pos[1], pos[2])
            idx_max = i
            end_time = time.time()
            if (end_time - start_time) > self.time_movement:
                break

        self.real_dst = self.real_dst[idx_max + 1:]
        self.dst = self.real_dst.copy()

        return Status.RUNNING


class MoveToTargetDr(Behaviour, Nav3D):
    def __init__(self, name, drone: Drone, graph_map):
        Behaviour.__init__(self, name=name)
        Nav3D.__init__(self, nav_map=graph_map)
        self.drone = drone
        self.src = AIManagerBlackboard.get_home_position(self.drone.id)
        self.dst = None
        self.target_position = None

    def update(self) -> common.Status:
        if not AIManagerBlackboard.get_is_keeper_idx_status(self.drone.id):
            return Status.FAILURE

        src = None
        dst = None
        if not self.dst:
            if not AIManagerBlackboard.get_has_cargo_idx_status(self.drone.id):
                self.target_position = AIManagerBlackboard.get_box_reward_position()[:-1]
            else:
                self.target_position = AIManagerBlackboard.get_home_position(self.drone.id)

            src = BuildNavMap3D.get_number_node_from_position(self.src)
            dst = BuildNavMap3D.get_number_node_from_position(self.target_position)

        way = FindNavPath.find_path_A_3D(self.map, src, dst)
        position = BuildNavMap3D.get_coordinate_path(self.map, way)

        self.dst = position

        if AIManagerBlackboard.get_is_keeper_idx_status(self.drone.id):
            for i, pos in enumerate(self.dst):
                if status_blocked(self.drone.id):
                    return Status.FAILURE
                self.drone.move_for_target(self.drone.id, pos[0], pos[1], pos[2])
                self.src = (pos[0], pos[1], pos[2])
            self.dst = []
            print("Дрон достиг назначенной цели")
            return Status.SUCCESS


class StopDr(Behaviour):
    def __init__(self, name, drone: Drone):
        super().__init__(name)
        self.drone = drone

    def update(self):
        if status_blocked(self.drone.id):
            return Status.FAILURE
        print("Дрон остановился")
        time.sleep(1)
        return Status.SUCCESS


class AttackDr(Behaviour):
    def __init__(self, name, drone: Drone):
        super().__init__(name)
        self.drone = drone
        self.amount_patrons = 0

    def update(self):
        if status_blocked(self.drone.id):
            return Status.FAILURE
        self.amount_patrons = AIManagerBlackboard.get_amount_patrons_idx(self.drone.id)
        if AIManagerBlackboard.get_attack_idx_status(self.drone.id):
            if self.amount_patrons > 0:
                print(f"Дрон {self.drone.id} совершает удачную атаку")
                AIManagerBlackboard.set_amount_patrons_idx(self.drone.id, self.amount_patrons - 1)
            else:
                print(f"Дрон {self.drone.id} не способна удачную атаку")
                AIManagerBlackboard.set_status_need_recharge(self.drone.id, True)

        return Status.SUCCESS


class TakeCargoDr(Behaviour):
    def __init__(self, name, drone):
        super().__init__(name)
        self.drone = drone

    def update(self):
        if status_blocked(self.drone.id):
            return Status.FAILURE
        time.sleep(1)
        print('Drone take cargo is taken')
        AIManagerBlackboard.set_status_has_cargo(self.drone.id, True)
        return Status.SUCCESS


class GiveCargoDr(Behaviour):
    def __init__(self, name, drone: Drone):
        super().__init__(name)
        self.drone = drone

    def update(self):
        if status_blocked(self.drone.id):
            return Status.FAILURE
        time.sleep(1)
        print('Drone give give give Cargo is given')
        AIManagerBlackboard.set_status_has_cargo(self.drone.id, False)
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


class BlockedDr(Behaviour):
    def __init__(self, name, drone: Drone):
        super().__init__(name)
        self.time = 30
        self.drone = drone

    def update(self):
        print("Im gere")
        status = AIManagerBlackboard.get_blocked_status_idx(self.drone.id)
        if status:
            print("Blocked")
            time.sleep(30)
        return Status.SUCCESS

