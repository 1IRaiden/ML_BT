import time
import typing
import numpy as np
from ML_BT.Vehicle.Vehicle import Car
from py_trees.behaviour import Behaviour
from py_trees.common import Status
from py_trees import common
from ML_BT.ML_Behaviour.BTAgents import AIManagerBlackboard
from ML_BT.SystemNavigation.Navigation import BuildNavMap2D, FindNavPath


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


class Nav:
    def __init__(self, nav_map):
        self.map = nav_map


class Initiate(Behaviour):
    def __init__(self, name, car: Car):
        super().__init__(name)
        self.game_car = car

    def update(self):
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

    def update(self):
        if not self.dst:
            dst = np.random.randint(0, 99)
            way = FindNavPath.find_path_A(self.map, self.src, dst)
            self.src = dst
            position = BuildNavMap2D.get_coordinate_path(self.map, way)
            self.dst = position
            self.real_dst = position.copy()

        if AIManagerBlackboard.get_is_keeper_idx_status(self.game_car.id):
            return Status.SUCCESS

        start_time = time.time()
        idx_max = 0
        for i, pos in enumerate(self.dst):
            self.game_car.move_for_target(self.game_car.id, pos[0], pos[1])
            idx_max = i
            end_time = time.time()
            if (end_time - start_time) > self.time_movement:
                break

        self.real_dst = self.real_dst[idx_max + 1:]
        self.dst = self.real_dst.copy()

        return Status.RUNNING


class MoveToTarget(Behaviour, Nav):
    def __init__(self, name, car: Car, graph_map):
        Behaviour.__init__(self, name=name)
        Nav.__init__(self, nav_map=graph_map)
        self.game_car = car
        self.src = [0, 0]
        self.dst = None
        self.target_position = None

    def update(self) -> common.Status:
        if not AIManagerBlackboard.get_is_keeper_idx_status(self.game_car.id):
            return Status.FAILURE

        src = None
        dst = None
        if not self.dst:
            if not AIManagerBlackboard.get_has_cargo_idx_status(self.game_car.id):
                self.target_position = [7, 8]  #AIManagerBlackboard.get_value_key_blackboard("pos_box2")
            else:
                self.target_position = AIManagerBlackboard.get_home_position(self.game_car.id)
                print("target position", self.target_position)

            src = BuildNavMap2D.get_number_node_from_position(self.src)
            dst = BuildNavMap2D.get_number_node_from_position(self.target_position)

        way = FindNavPath.find_path_A(self.map, src, dst)
        position = BuildNavMap2D.get_coordinate_path(self.map, way)

        self.dst = position

        if AIManagerBlackboard.get_is_keeper_idx_status(self.game_car.id):
            for i, pos in enumerate(self.dst):
                print("movement")
                self.game_car.move_for_target(self.game_car.id, pos[0], pos[1])
                self.src = (pos[0], pos[1])
            self.dst = []
            return Status.SUCCESS


class Stop(Behaviour):
    def __init__(self, name):
        super().__init__(name)

    def update(self):
        time.sleep(2)
        return Status.SUCCESS


class Attack(Behaviour):
    def __init__(self, name):  #get_amount_patrons, update_amount_patrons,
                 #need_attack=False):
        super().__init__(name)
        #self.amount = get_amount_patrons()
        #self.need_attack = need_attack
        #self.t = update_amount_patrons

    def update(self):
        print("Атака")
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


class TakeCargo(Behaviour):
    def __init__(self, name, car):
        super().__init__(name)
        self.game_car = car

    def update(self):
        time.sleep(1)
        print('Cargo is taken')
        AIManagerBlackboard.set_status_has_cargo(self.game_car.id, True)
        return Status.SUCCESS


class GiveCargo(Behaviour):
    def __init__(self, name, car):
        super().__init__(name)
        self.game_car = car

    def update(self):
        time.sleep(1)
        print('Cargo is given')
        AIManagerBlackboard.set_status_has_cargo(self.game_car.id, False)
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























