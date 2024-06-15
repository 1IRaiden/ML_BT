from ML_BT.ML_Behaviour.CarAction import *
from ML_BT.ML_Behaviour.DroneAction import *
from typing import Union
from ML_BT.Config import HAS_CARS_IN_GAMES, HAS_DRONE_IN_GAME


class Agent:
    reader = AIManagerBlackboard().writer
    nav_map = None

    def __init__(self, name, nav_map, obj: Union[Car, Drone]):
        self.game_obj = obj
        Agent.nav_map = nav_map
        self.name = name
        self.set_start_blackboard_position()
        self.tree = BehaviourTree(self.create_behaviour_tree())

    # this method set start position for cars when creating agents
    def set_start_blackboard_position(self):
        AIManagerBlackboard.add_key(f"car_start_position{self.name}", self.game_obj.YOUR_POSITION)
        # print(Agent.reader.get(f"car_start_position{self.name}"))

    def create_behaviour_tree(self):
        if HAS_CARS_IN_GAMES:
            return self.create_behaviour_tree_car()
        if HAS_DRONE_IN_GAME:
            return self.create_behaviour_tree_drone()

    def create_behaviour_tree_car(self):
        # Actions
        action_initiate = Initiate("initiate", self.game_obj)
        ac_initiate = de.OneShot(name='hit', child=action_initiate,
                                 policy=common.OneShotPolicy.ON_SUCCESSFUL_COMPLETION)

        action_movement = Movement('movement', self.game_obj, Agent.nav_map, Agent.reader.get(f"is_keeper{self.name}_box"))

        action_move_target = MoveToTarget('target', self.game_obj, Agent.reader.get(f"is_keeper{self.name}_box"), Agent.nav_map)
        action_move_target_1 = MoveToTarget('target', self.game_obj, Agent.reader.get(f"is_keeper{self.name}_box"), Agent.nav_map)

        action_attack = Attack('attack', self.get_amount_patrons, self.update_amount_patrons,
                                 Agent.reader.get(f"attack{self.name}"))
        action_attack_1 = Attack('attack_1', self.get_amount_patrons, self.update_amount_patrons,
                                 Agent.reader.get(f"attack{self.name}"))
        action_attack_2 = Attack('attack_2', self.get_amount_patrons, self.update_amount_patrons,
                                 Agent.reader.get(f"attack{self.name}"))

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

        action_movement = MovementDr('movement', self.game_obj, Agent.nav_map, Agent.reader.get(f"is_keeper{self.name}_box"))

        action_move_target = MoveToTargetDr('target', self.game_obj, Agent.reader.get(f"is_keeper{self.name}_box"),
                                          Agent.nav_map)
        action_move_target_1 = MoveToTargetDr('target', self.game_obj, Agent.reader.get(f"is_keeper{self.name}_box"),
                                            Agent.nav_map)

        action_attack = AttackDr('attack', self.get_amount_patrons, self.update_amount_patrons,
                               Agent.reader.get(f"attack{self.name}"))
        action_attack_1 = AttackDr('attack_1', self.get_amount_patrons, self.update_amount_patrons,
                                 Agent.reader.get(f"attack{self.name}"))
        action_attack_2 = AttackDr('attack_2', self.get_amount_patrons, self.update_amount_patrons,
                                 Agent.reader.get(f"attack{self.name}"))

        action_take_cargo = TakeCargo('take', self.game_obj)
        action_give_cargo = GiveCargo('give', self.game_obj)
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
        action_start_movement.add_children([action_takeoff_start, action_order_behaviour])


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
            action_choice_strategy,
        ])
        return root

    # def create_behaviour_tree_drone(self):
    #     return

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
