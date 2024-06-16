import time
from ML_BT.ML_Behaviour.CarAction import *
from ML_BT.ML_Behaviour.DroneAction import *
from typing import Union
from py_trees.composites import Sequence, Parallel, Selector
from py_trees.trees import BehaviourTree
import py_trees.decorators as de


class Agent:
    reader = AIManagerBlackboard().writer
    nav_map_2d = None
    nav_map_3d = None

    HAS_CARS_IN_GAMES = False
    HAS_DRONE_IN_GAME = False

    def __init__(self, obj: Union[Car, Drone]):
        self.game_obj = obj
        self.tree = BehaviourTree(self.create_behaviour_tree())

    @classmethod
    def change_value_status(cls, status_a, status_b):
        cls.HAS_CARS_IN_GAMES = status_a
        cls.HAS_DRONE_IN_GAME = status_b

    @classmethod
    def set_nav_map_for_game(cls, *, nav_map_2d=None, nav_map_3d=None):
        if cls.HAS_CARS_IN_GAMES:
            cls.nav_map_2d = nav_map_2d
        if cls.HAS_DRONE_IN_GAME:
            cls.nav_map_3d = nav_map_3d

    def create_behaviour_tree(self):
        if isinstance(self.game_obj, Car):
            return self.create_behaviour_tree_car()
        if isinstance(self.game_obj, Drone):
            return self.create_behaviour_tree_drone()

    def create_behaviour_tree_car(self):
        # Actions
        action_initiate = Initiate("initiate", self.game_obj)
        ac_initiate = de.OneShot(name='hit', child=action_initiate,
                                 policy=common.OneShotPolicy.ON_SUCCESSFUL_COMPLETION)

        action_movement = Movement('movement', self.game_obj, Agent.nav_map_2d)            #
        action_move_target = MoveToTarget('target', self.game_obj,  Agent.nav_map_2d)
        action_move_target_1 = MoveToTarget('target', self.game_obj, Agent.nav_map_2d)

        action_attack = Attack('attack') # self.get_amount_patrons, self.update_amount_patrons,
                               # AIManagerBlackboard.get_attack_idx_status(self.game_obj.id))
        action_attack_1 = Attack('attack_1')
        action_attack_2 = Attack('attack_2')

        action_take_cargo = TakeCargo('take', self.game_obj)
        action_give_cargo = GiveCargo('give', self.game_obj)
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

    def create_behaviour_tree_drone(self):
        # Actions
        action_initiate = InitiateDr("initiate", self.game_obj)
        ac_initiate = de.OneShot(name='hit', child=action_initiate,
                                 policy=common.OneShotPolicy.ON_SUCCESSFUL_COMPLETION)

        action_movement = MovementDr('movement', self.game_obj, Agent.nav_map_3d)
        action_move_target = MoveToTargetDr('target', self.game_obj, Agent.nav_map_3d)
        action_move_target_1 = MoveToTargetDr('target', self.game_obj, Agent.nav_map_3d)

        action_attack = AttackDr('attack')
        action_attack_1 = AttackDr('attack_1')
        action_attack_2 = AttackDr('attack_2')

        action_take_cargo = TakeCargoDr('take', self.game_obj)
        action_give_cargo = GiveCargoDr('give', self.game_obj)
        action_recharge = Recharge('recharge')

        action_stop = Stop('stop')
        action_stop_1 = Stop('stop_1')

        action_takeoff_start = TakeOff("takeoff_start", drone=self.game_obj)
        action_takeoff_cargo = TakeOff("takeoff_cargo", drone=self.game_obj)

        # this parameter will realise in future
        action_takeoff_recharge = TakeOff("takeoff_recharge", drone=self.game_obj)

        action_landing_end = Landing("landing_end", drone=self.game_obj)
        action_landing_cargo = Landing("landing_end", drone=self.game_obj)

        # this parameter will realise in future
        action_takeoff_recharge = Landing("takeoff_recharge", drone=self.game_obj)

        # Group free behaviour action for random position
        action_order_behaviour = Parallel(name="action_order_behaviour",
                                          policy=common.ParallelPolicy.SuccessOnSelected([action_movement]),
                                          children=[action_movement, action_attack])

        # Перед движением в воздухе необходимо взлететь:
        action_start_movement = Sequence("takeoff and checking", memory=True)
        action_start_movement.add_children([action_order_behaviour])

        # Get plan action for take_cargo
        action_cargo_take = Sequence(name='cargoTake', memory=True)
        action_cargo_take.add_children([action_move_target,
                                        action_stop,
                                        action_landing_cargo,
                                        action_take_cargo])

        # Get opportunity for attack using cargo
        action_order_behaviour_2 = Parallel(name="action_order_behaviour_2",
                                            policy=common.ParallelPolicy.SuccessOnSelected([action_cargo_take]),
                                            children=[action_cargo_take, action_attack_1])

        # create sequence for giving cargo
        action_cargo_give = Sequence(name='cargoGive', memory=True)
        action_cargo_give.add_children([action_takeoff_cargo,
                                        action_move_target_1,
                                        action_stop_1,
                                        action_landing_end,
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
            action_start_movement])

        root = Sequence(name="sequence", memory=True)

        root.add_children([
            ac_initiate,
            action_takeoff_start,
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
