import time

import py_trees.trees
from py_trees.behaviour import Behaviour
from py_trees.common import Status, OneShotPolicy
from py_trees.composites import Sequence, Parallel, Selector
from py_trees import common
import py_trees.decorators as de
from py_trees.trees import BehaviourTree
from py_trees import blackboard
from ML_BT.ML_Behaviour.BTAgents import AIManagerBlackboard


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


class Initiate(Behaviour):
    def __init__(self, name):
        super().__init__(name)

    def update(self):
        print('checking active of car')
        return Status.SUCCESS


class Movement(Behaviour):
    def __init__(self, name, is_keeper=False):
        super().__init__(name)
        self.time_movement = 10
        self.is_keeper = is_keeper

    def update(self):
        time.sleep(1)
        self.time_movement -= 1
        if self.time_movement <= 0:
            self.time_movement = 5
            if self.is_keeper:
                return Status.SUCCESS
        # rint('Movement is Continue')
        return Status.RUNNING


class MoveToTarget(Behaviour):
    def __init__(self, name, is_keeper):
        super().__init__(name)
        self.time_movement = 5
        self.is_keeper = is_keeper

    def update(self) -> common.Status:
        if self.is_keeper:
            time.sleep(1)
            self.time_movement -= 1
            if self.time_movement <= 0:
                self.time_movement = 5
                print('was target', self.time_movement)
                return Status.SUCCESS
            else:
                return Status.RUNNING

        return Status.FAILURE


class Stop(Behaviour):
    def __init__(self, name):
        super().__init__(name)

    def update(self):
        print("done stop")
        time.sleep(2)
        return Status.SUCCESS


class Attack(Behaviour):
    def __init__(self, name,  get_amount_patrons, update_amount_patrons, need_attack=False):
        super().__init__(name)
        self.amount = get_amount_patrons()
        self.need_attack = need_attack
        self.t = update_amount_patrons

    def update(self):
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
    def __init__(self, name):
        super().__init__(name)

    def update(self):
        time.sleep(1)
        print('Cargo is taken')
        return Status.SUCCESS


class GiveCargo(Behaviour):
    def __init__(self, name):
        super().__init__(name)

    def update(self):
        time.sleep(1)
        print('Cargo is given')
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


class Agent:
    reader = AIManagerBlackboard().writer

    def __init__(self, name):
        self.name = name
        self.tree = BehaviourTree(self.create_behaviour_tree())

    def create_behaviour_tree(self):
        # Actions
        action_initiate = Initiate("initiate")
        ac_initiate = de.OneShot(name='hit', child=action_initiate,
                                 policy=common.OneShotPolicy.ON_SUCCESSFUL_COMPLETION)

        action_movement = Movement('movement', Agent.reader.get(f"is_keeper{self.name}_box"))

        action_move_target = MoveToTarget('target', Agent.reader.get(f"is_keeper{self.name}_box"))
        action_move_target_1 = MoveToTarget('target', Agent.reader.get(f"is_keeper{self.name}_box"))

        action_attack = Attack('attack', self.get_amount_patrons, self.update_amount_patrons,
                                 Agent.reader.get(f"attack{self.name}"))
        action_attack_1 = Attack('attack_1', self.get_amount_patrons, self.update_amount_patrons,
                                 Agent.reader.get(f"attack{self.name}"))
        action_attack_2 = Attack('attack_2', self.get_amount_patrons, self.update_amount_patrons,
                                 Agent.reader.get(f"attack{self.name}"))

        action_take_cargo = TakeCargo('take')
        action_give_cargo = GiveCargo('give')
        action_recharge = Recharge('recharge')

        action_stop = Stop('stop')
        action_stop_1 = Stop('stop_1')

        # Group free behaviour action for random position
        action_order_behaviour = Parallel(name="action_order_behaviour",
                                          policy=common.ParallelPolicy.SuccessOnSelected([action_movement]),
                                          children=[action_movement, action_attack])

        # Get plan action for take_cargo
        action_cargo_take = Sequence(name='cargoTake', memory=True)
        action_cargo_take.add_children([action_move_target,
                                        action_stop,
                                        action_take_cargo])

        # Get opportunity for attack using cargo
        action_order_behaviour_2 = Parallel(name="action_order_behaviour_2",
                                            policy=common.ParallelPolicy.SuccessOnSelected([action_cargo_take]),
                                            children=[action_cargo_take, action_attack_1])

        # create sequence for giving cargo
        action_cargo_give = Sequence(name='cargoGive', memory=True)
        action_cargo_give.add_children([action_move_target_1,
                                        action_stop_1,
                                        action_give_cargo])

        action_order_behaviour_3 = Parallel(name="action_order_behaviour_3",
                                            policy=common.ParallelPolicy.SuccessOnSelected([action_cargo_give]),
                                            children=[action_cargo_give, action_attack_2])

        action_cargo_order = Sequence(name='order', memory=True, children=[
            action_order_behaviour_2,
            action_order_behaviour_3])

        # choice strategy
        action_choice_strategy = Selector(name="choice_strategy", memory=True, children=[
            action_cargo_order,
            action_order_behaviour])

        root = Sequence(name="sequence", memory=True)

        root.add_children([
            ac_initiate,
            action_choice_strategy,
        ])
        return root

    def start_tick(self):
        try:
            while True:
                self.tree.tick()
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n  Manual cycle interruption (Ctrl+C)")

    def update_amount_patrons(self, new_amount):
        Agent.reader.set(f"amount_patrons{self.name}", new_amount)

    def get_amount_patrons(self):
        return Agent.reader.get(f"amount_patrons{self.name}")





















