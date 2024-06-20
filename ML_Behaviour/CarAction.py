import time
import typing
import numpy as np
from ML_BT.Vehicle.Vehicle import Car
from py_trees.behaviour import Behaviour
from py_trees.common import Status
from py_trees import common
from ML_BT.ML_Behaviour.BTAgents import AIManagerBlackboard
from ML_BT.SystemNavigation.Navigation import BuildNavMap2D, FindNavPath
from ML_BT.Config import IF_FORWARD


# This code get manage by car
'''
    Main Action for car:
- Attack
- Movement
- Recharge
- MovementToTarget
- Stop
- TakeCargo
- GiveCargo 

    Decorators:
1. de.OneShot - Executes the child node until the first successful completion, after which it always returns SUCCESS,
    preventing the child node from being executed again.
2. de.Condition- The Condition decorator executes the child node and converts the status to SUCCESS
    or FAILURE depending on the fulfillment of a certain condition.
3. de.FailureIsRunning, de.FailureIsSuccess, de.RunningIsFailure, de.SuccessIsFailure -- this executes are clear
4. de.Inverter - The Inverter inverts the final status of the node — turns SUCCESS into FAILURE and vice versa.
5. de.Count - The Count decorator executes the child node until the number of its successful    
    executions reaches the specified limit
6. de.EternalGuard - The EternalGuard decorator remains active and returns the RUNNING status until the child n
ode reaches the SUCCESS or FAILURE state. If the child node terminates,
 EternalGuard returns the same status as the child node and resets to start again from the initial state.
7. de.Retry - The Retry decorator repeats the execution attempts of the child node, if it ends with a FAILURE result,
 before the specified number of attempts. If the child node has not returned SUCCESS after all attempts,
  the decorator returns FAILURE.
8.de.Timeout - The Timeout decorator wraps a child node and aborts its execution if it exceeds the specified time limit.
 If the time expires, the decorator returns FAILURE, otherwise it is the result of the execution of the child node.
'''

'''
    Features of working with blackboard:
    1. Registration:

    reader = Client(name='K')
    reader.register_key(key="is_keeper_key", access=common.Access.READ)

    2. Referring to the result:
    result = reader.get(name="is_keeper_key")
    result = reader.is_keeper_key       
'''
# this scripts has not solution using web protocol it is issue future


def status_blocked(idx):
    return AIManagerBlackboard.get_blocked_status_idx(idx)


class Nav:
    def __init__(self, nav_map):
        self.map = nav_map


class Initiate(Behaviour):
    def __init__(self, name, car: Car):
        super().__init__(name)
        self.game_car = car

    def update(self):
        if IF_FORWARD:
            self.game_car.set_connection('localhost', f'{8000 + self.game_car.id}')
        time.sleep(1)
        return Status.SUCCESS


class Movement(Behaviour, Nav):
    def __init__(self, name, car: Car, graph_map):
        Behaviour.__init__(self, name)
        Nav.__init__(self, graph_map)
        self.time_movement = 7
        self.game_car = car
        self.src = 1
        self.dst = None
        self.real_dst = None
        self.recharge = False

    def update(self):
        print(f"[logger:: {self.game_car.id} :: Movement]: Change on status movement car")
        if not self.dst:
            # get information about station
            if AIManagerBlackboard.get_recharge_idx_status(self.game_car.id):
                print(f"[logger:: {self.game_car.id}:: Movement]: Drone prepare fly to station recharge")
                # free recharge? Пусть будет станция 0:
                dst = AIManagerBlackboard.get_recharge_position_station(1)
                dst = BuildNavMap2D.get_number_node_from_position(dst[:-1])
                self.recharge = True
            else:
                dst = np.random.randint(0, 99)
                self.recharge = False

            way = FindNavPath.find_path_A(self.map, self.src, dst)
            self.src = dst
            position = BuildNavMap2D.get_coordinate_path(self.map, way)
            self.dst = position
            self.real_dst = position.copy()

        if AIManagerBlackboard.get_is_keeper_idx_status(self.game_car.id):
            print(f"[logger:: {self.game_car.id} :: Movement]: Change on status movement_to_target - car")
            return Status.SUCCESS

        start_time = time.time()
        idx_max = 0
        for i, pos in enumerate(self.dst):
            if status_blocked(self.game_car.id):
                return Status.FAILURE
            AIManagerBlackboard.set_dst_position_idx(self.game_car.id, (pos[0], pos[1], 0))
            if IF_FORWARD:
                self.game_car.move_for_target(self.game_car.id, pos[0], pos[1])
                idx_max = i
                end_time = time.time()
                if (end_time - start_time) > self.time_movement:
                    break
            else:
                time.sleep(1)
                if AIManagerBlackboard.get_status_reaching_dst_target(self.game_car.id):
                    AIManagerBlackboard.set_status_reaching_dst_target(self.game_car.id, False)
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


class MoveToTarget(Behaviour, Nav):
    def __init__(self, name, car: Car, graph_map):
        Behaviour.__init__(self, name=name)
        Nav.__init__(self, nav_map=graph_map)
        self.game_car = car
        self.src = AIManagerBlackboard.get_home_position(self.game_car.id)
        self.dst = None
        self.target_position = None

    def update(self) -> common.Status:
        if not AIManagerBlackboard.get_is_keeper_idx_status(self.game_car.id):
            print(f"[logger:: {self.game_car.id} :: MoveToTarget]: Happen mistake and car turn in up coincide")
            print(f"[logger:: {self.game_car.id} :: MoveToTarget]: Status cancel for")
            return Status.FAILURE

        src = None
        dst = None
        if not self.dst:
            if not AIManagerBlackboard.get_has_cargo_idx_status(self.game_car.id):
                self.target_position = AIManagerBlackboard.get_box_reward_position()[:-1]
                print(f"[logger:: {self.game_car.id} :: MoveToTarget]: For car get box position", self.target_position)
            else:
                self.target_position = AIManagerBlackboard.get_home_position(self.game_car.id)
                print(f"[logger:: {self.game_car.id} :: MoveToTarget]: For car get home position", self.target_position)

            src = BuildNavMap2D.get_number_node_from_position(self.src)
            dst = BuildNavMap2D.get_number_node_from_position(self.target_position)

        way = FindNavPath.find_path_A(self.map, src, dst)
        position = BuildNavMap2D.get_coordinate_path(self.map, way)

        self.dst = position

        if AIManagerBlackboard.get_is_keeper_idx_status(self.game_car.id):
            for i, pos in enumerate(self.dst):
                if status_blocked(self.game_car.id):
                    return Status.FAILURE
                AIManagerBlackboard.set_dst_position_idx(self.game_car.id, (pos[0], pos[1], 0))
                if IF_FORWARD:
                    self.game_car.move_for_target(self.game_car.id, pos[0], pos[1])
                    self.src = (pos[0], pos[1])
                else:
                    while not AIManagerBlackboard.get_status_reaching_dst_target(self.game_car.id):
                        time.sleep(1)
                        print(f"[logger:: {self.game_car.id} :: MoveToTarget]: Car try get into destination")
                        # break
                    AIManagerBlackboard.set_status_reaching_dst_target(self.game_car.id, False)

                self.dst = []
            return Status.SUCCESS


class Stop(Behaviour):
    def __init__(self, name, car: Car):
        super().__init__(name)
        self.game_car = car

    def update(self):
        if status_blocked(self.game_car.id):
            return Status.FAILURE
        print(f"[logger:: {self.game_car.id} :: Stop]: Car {self.game_car.id} change state")
        time.sleep(1)
        return Status.SUCCESS


class Attack(Behaviour):
    def __init__(self, name, car: Car):
        super().__init__(name)
        self.game_car = car
        self.amount_patrons = 0

    def update(self):
        if status_blocked(self.game_car.id):
            return Status.FAILURE
        self.amount_patrons = AIManagerBlackboard.get_amount_patrons_idx(self.game_car.id)
        if AIManagerBlackboard.get_attack_idx_status(self.game_car.id):
            if self.amount_patrons > 0:
                print(f"[logger:: {self.game_car.id} :: Attack]:  Машинка совершает удачную атаку")
            else:
                print(f"[logger:: {self.game_car.id} :: Attack]: Машинка не способна удачную атаку")

        return Status.SUCCESS


class TakeCargo(Behaviour):
    def __init__(self, name, car):
        super().__init__(name)
        self.game_car = car

    def update(self):
        time.sleep(1)
        if status_blocked(self.game_car.id):
            return Status.FAILURE

        AIManagerBlackboard.set_take_cargo_status_idx(self.game_car.id, True)
        print(f"[logger:: {self.game_car.id} :: TakeCargo]: Set new status for can take cargo")
        while not AIManagerBlackboard.get_has_cargo_idx_status(self.game_car.id):
            time.sleep(1)
            if not AIManagerBlackboard.get_is_keeper_idx_status(self.game_car.id):
                print(f"[logger:: {self.game_car.id} :: TakeCargo]: my status was cancel --> Movement")
                return Status.FAILURE

            # break
        AIManagerBlackboard.set_take_cargo_status_idx(self.game_car.id, False)
        # AIManagerBlackboard.set_status_has_cargo(self.game_car.id, True)
        print(f"[logger:: {self.game_car.id} :: TakeCargo]: Cargo success taken car state changed")
        return Status.SUCCESS


class GiveCargo(Behaviour):
    def __init__(self, name, car):
        super().__init__(name)
        self.game_car = car

    def update(self):
        time.sleep(1)
        if status_blocked(self.game_car.id):
            return Status.FAILURE

        AIManagerBlackboard.set_give_cargo_status_idx(self.game_car.id, True)
        print(f"[logger:: {self.game_car.id} :: GiveCargo]: Set new status for can give cargo")

        while not AIManagerBlackboard.get_has_cargo_idx_status(self.game_car.id):
            # AIManagerBlackboard.set_status_has_cargo(self.game_car.id, False)
            time.sleep(1)
        AIManagerBlackboard.set_keeper_status(self.game_car.id)
        print(f"[logger:: {self.game_car.id} :: GiveCargo]: Cargo success give car state changed must start new round")
        return Status.SUCCESS


class Recharge(Behaviour):
    def __init__(self, name, car: Car):
        super().__init__(name)
        self.time_recharge = 30
        self.game_car = car

    def update(self):
        time.sleep(1)
        print(f"[logger:: {self.game_car.id}:: Recharge]: Car prepare for to recharge")
        self.time_recharge -= 1
        if self.time_recharge <= 0:
            while AIManagerBlackboard.get_recharge_idx_status(self.game_car.id):
                time.sleep(0.2)
            print(f"[logger:: {self.game_car.id}:: RechargeDr]: Recharge is finished")
            return Status.SUCCESS
        else:
            return Status.RUNNING


class Blocked(Behaviour):
    def __init__(self, name, car: Car):
        super().__init__(name)
        self.time = 30
        self.car = car

    def update(self):
        status = AIManagerBlackboard.get_blocked_status_idx(self.car.id)
        if status:
            print(f"[log ger:: {self.car.id} :: Blocked]: game car is blocked on 30 second")
            time.sleep(30)

        return Status.SUCCESS























