import time
import numpy as np
from ML_BT.Vehicle.Vehicle import Drone
from py_trees.behaviour import Behaviour
from py_trees.common import Status
from py_trees import common
from ML_BT.ML_Behaviour.BTAgents import AIManagerBlackboard
from ML_BT.SystemNavigation.Navigation import FindNavPath, BuildNavMap3D
from ML_BT.Config import IF_FORWARD


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
        if IF_FORWARD:
            self.drone.set_connection('localhost', f'{8000 + self.drone.id}')
            self.drone.include_arm()
        time.sleep(3)
        return Status.SUCCESS


class TakeOff(Behaviour):
    def __init__(self, name, drone: Drone):
        super().__init__(name)
        self.drone = drone

    def update(self) -> common.Status:
        if status_blocked(self.drone.id):
            return Status.FAILURE
        if IF_FORWARD:
            landing = AIManagerBlackboard.get_drone_landing_idx_status(self.drone.id)
            if landing:
                print("Дрон взлетел")
                self.drone.takeoff()
                AIManagerBlackboard.set_status_drone_landing(self.drone.id, False)
        else:
            AIManagerBlackboard.set_takeoff_status_drone(self.drone.id, True)
            print(f"[logger:: {self.drone.id} :: TakeOff]:  drone must takeoff")
            time.sleep(1)

        return Status.SUCCESS


class Landing(Behaviour):
    def __init__(self, name, drone: Drone):
        super().__init__(name)
        self.drone = drone

    def update(self) -> common.Status:
        if IF_FORWARD:
            status = AIManagerBlackboard.get_drone_landing_idx_status(self.drone.id)
            if not status:
                self.drone.land()
                AIManagerBlackboard.set_status_drone_landing(self.drone.id, True)
                print("Посадка дрона совершена")
                if status_blocked(self.drone.id):
                    return Status.FAILURE
        else:
            AIManagerBlackboard.set_landing_status_drone(self.drone.id, True)
            print(f"[logger:: {self.drone.id}:: Landing]: set new status -- drone must land")
        return Status.SUCCESS


class MovementDr(Behaviour, Nav3D):
    def __init__(self, name, drone: Drone, graph_map):
        Behaviour.__init__(self, name)
        Nav3D.__init__(self, graph_map)
        self.time_movement = 7
        self.drone = drone
        self.src = 0
        self.dst = None
        self.real_dst = None
        self.recharge = False

    def update(self):
        self.src = AIManagerBlackboard.get_current_position_idx(self.drone.id)
        print(f"[logger:: {self.drone.id} :: MovementDr]: Movement")
        # check :: AIManagerBlackboard.set_takeoff_status_drone(self.drone.id, False)
        while AIManagerBlackboard.get_takeoff_status_drone(self.drone.id):
            time.sleep(0.3)
        print(f"[logger:: {self.drone.id} :: MovementDr]: Drone fly")

        self.src = BuildNavMap3D.get_number_node_from_position(self.src)
        if not self.dst:
            # get information about station
            if AIManagerBlackboard.get_recharge_idx_status(self.drone.id):
                print(f"[logger:: {self.drone.id}:: Movement]: Drone prepare fly to station recharge")
                # free recharge? Пусть будет станция 1:
                dst = AIManagerBlackboard.get_recharge_position_station(1)
                dst = BuildNavMap3D.get_number_node_from_position(dst)
                self.recharge = True
            else:
                dst = np.random.randint(0, 6*6*6)
                self.recharge = False
            way = FindNavPath.find_path_A_3D(self.map, self.src, dst)
            self.src = dst
            position = BuildNavMap3D.get_coordinate_path(self.map, way)
            self.dst = position
            self.real_dst = position.copy()

        if AIManagerBlackboard.get_is_keeper_idx_status(self.drone.id):
            print(f"[logger:: {self.drone.id}:: Movement]: Change on status movement_to_target - drone")
            return Status.SUCCESS

        start_time = time.time()
        idx_max = 0
        for i, pos in enumerate(self.dst):
            if status_blocked(self.drone.id):
                return Status.FAILURE
            AIManagerBlackboard.set_dst_position_idx(self.drone.id, (pos[0], pos[1], pos[2]))
            if IF_FORWARD:
                self.drone.move_for_target(self.drone.id, pos[0], pos[1], pos[2])
                idx_max = i
                end_time = time.time()
                if (end_time - start_time) > self.time_movement:
                    break
            else:
                time.sleep(1)
                if AIManagerBlackboard.get_status_reaching_dst_target(self.drone.id):
                    AIManagerBlackboard.set_status_reaching_dst_target(self.drone.id, False)
                    idx_max = i
                    end_time = time.time()
                    if (end_time - start_time) > self.time_movement:
                        break

        self.real_dst = self.real_dst[idx_max + 1:]
        self.dst = self.real_dst.copy()

        if not self.dst:
            if self.recharge:
                return Status.SUCCESS

        return Status.RUNNING


class MoveToTargetDr(Behaviour, Nav3D):
    def __init__(self, name, drone: Drone, graph_map):
        Behaviour.__init__(self, name=name)
        Nav3D.__init__(self, nav_map=graph_map)
        self.drone = drone
        self.src = 0
        self.dst = None
        self.target_position = None

    def update(self) -> common.Status:
        self.src = AIManagerBlackboard.get_home_position(self.drone.id)
        print(f"[logger:: {self.drone.id} :: MoveToTargetDr]:")
        # check :: AIManagerBlackboard.set_takeoff_status_drone(self.drone.id, False) ###
        if not AIManagerBlackboard.get_is_keeper_idx_status(self.drone.id):
            print(f"[logger:: {self.drone.id} :: MoveToTargetDr]: Happen mistake and car turn in up coincide")
            print(f"[logger:: {self.drone.id} :: MoveToTargetDr]: Status cancel for")
            return Status.FAILURE

        while AIManagerBlackboard.get_takeoff_status_drone(self.drone.id):
            time.sleep(0.3)
        print(f"[logger:: {self.drone.id} :: MoveToTargetDr]: Drone start fly")

        src = None
        dst = None
        if not self.dst:
            # check :: AIManagerBlackboard.set_status_has_cargo(self.drone.id, True)
            if not AIManagerBlackboard.get_has_cargo_idx_status(self.drone.id):
                self.target_position = AIManagerBlackboard.get_box_reward_position()
                print(f"[logger:: {self.drone.id} :: MoveToTargetDr]: For drone get box position", self.target_position)
            else:
                self.target_position = AIManagerBlackboard.get_home_position(self.drone.id)
                print(f"[logger:: {self.drone.id} :: MoveToTargetDr]: For drone get home position", self.target_position)

                src = BuildNavMap3D.get_number_node_from_position(self.src)
            dst = BuildNavMap3D.get_number_node_from_position(self.target_position)

        way = FindNavPath.find_path_A_3D(self.map, src, dst)
        position = BuildNavMap3D.get_coordinate_path(self.map, way)

        self.dst = position

        if AIManagerBlackboard.get_is_keeper_idx_status(self.drone.id):
            for i, pos in enumerate(self.dst):
                if status_blocked(self.drone.id):
                    return Status.FAILURE
                AIManagerBlackboard.set_dst_position_idx(self.drone.id, (pos[0], pos[1], pos[2]))
                if IF_FORWARD:
                    self.drone.move_for_target(self.drone.id, pos[0], pos[1], pos[2])
                    self.src = (pos[0], pos[1], pos[2])
                else:
                    while not AIManagerBlackboard.get_status_reaching_dst_target(self.drone.id):
                        time.sleep(1)
                        print(f"[logger:: {self.drone.id} :: MoveToTargetDr]: drone try get into destination")
                        AIManagerBlackboard.set_status_reaching_dst_target(self.drone.id, True) ####
                    AIManagerBlackboard.set_status_reaching_dst_target(self.drone.id, False)
            self.dst = []
            print(f"[logger:: {self.drone.id} :: MoveToTargetDr]: drone arrived in destination")
            return Status.SUCCESS


class StopDr(Behaviour):
    def __init__(self, name, drone: Drone):
        super().__init__(name)
        self.drone = drone

    def update(self):
        if status_blocked(self.drone.id):
            return Status.FAILURE
        print(f"[logger:: {self.drone.id} :: StopDr]: Drone {self.drone.id} change state")
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
            else:
                print(f"Дрон {self.drone.id} не способна удачную атаку")

        return Status.SUCCESS


class TakeCargoDr(Behaviour):
    def __init__(self, name, drone):
        super().__init__(name)
        self.drone = drone

    def update(self):
        time.sleep(1)
        if status_blocked(self.drone.id):
            return Status.FAILURE

        # check :: AIManagerBlackboard.set_landing_status_drone(self.drone.id, False)
        while AIManagerBlackboard.get_landing_status_drone(self.drone.id):
            time.sleep(1)
        AIManagerBlackboard.set_take_cargo_status_idx(self.drone.id, True)
        print(f"[logger:: {self.drone.id} :: TakeCargo]: Set new status for can take cargo")

        while not AIManagerBlackboard.get_has_cargo_idx_status(self.drone.id):
            time.sleep(1)
            if not AIManagerBlackboard.get_is_keeper_idx_status(self.drone.id):
                print(f"[logger:: {self.drone.id} :: TakeCargo]: my status was cancel --> Movement")
                return Status.FAILURE
            # check :: break

        AIManagerBlackboard.set_take_cargo_status_idx(self.drone.id, False)
        print(f"[logger:: {self.drone.id} :: TakeCargo]: Cargo success taken drone state changed")
        return Status.SUCCESS


class GiveCargoDr(Behaviour):
    def __init__(self, name, drone: Drone):
        super().__init__(name)
        self.drone = drone

    def update(self):
        print(f"[logger:: {self.drone.id} :: GiveCargo]:")
        time.sleep(1)
        if status_blocked(self.drone.id):
            return Status.FAILURE

        # check :: AIManagerBlackboard.set_landing_status_drone(self.drone.id, False)
        while AIManagerBlackboard.get_landing_status_drone(self.drone.id):
            time.sleep(1)
        AIManagerBlackboard.set_give_cargo_status_idx(self.drone.id, True)
        print(f"[logger:: {self.drone.id} :: GiveCargoDr]: Set new status for can give cargo")

        while not AIManagerBlackboard.get_has_cargo_idx_status(self.drone.id):
            time.sleep(1)
            # check :: break
        AIManagerBlackboard.set_keeper_status(self.drone.id)
        print(f"[logger:: {self.drone.id} :: GiveCargo]: Cargo success give car state changed must start new round")
        return Status.SUCCESS


class RechargeDr(Behaviour):
    def __init__(self, name, drone: Drone):
        super().__init__(name)
        self.drone = drone
        self.time_recharge = 30

    def update(self):
        time.sleep(1)
        while AIManagerBlackboard.get_landing_status_drone(self.drone.id):
            time.sleep(0.2)

        print(f"[logger:: {self.drone.id}:: RechargeDr]: Drone prepare for to recharge")
        time.sleep(1)
        self.time_recharge -= 1
        if self.time_recharge <= 0:

            while AIManagerBlackboard.get_recharge_idx_status(self.drone.id):
                time.sleep(0.2)
            print(f"[logger:: {self.drone.id}:: RechargeDr]: Recharge is finished")

            return Status.SUCCESS
        else:
            return Status.RUNNING


class BlockedDr(Behaviour):
    def __init__(self, name, drone: Drone):
        super().__init__(name)
        self.time = 30
        self.drone = drone

    def update(self):
        status = AIManagerBlackboard.get_blocked_status_idx(self.drone.id)
        if status:
            print(f"[logger:: {self.drone.id} :: Blocked]: game car is blocked on 30 second")
            time.sleep(self.time)
        return Status.SUCCESS

