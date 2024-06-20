from py_trees import blackboard
import typing

''' 
Этот класс определяет и следит за установкой значений на черной доске а так же полностью управляет переменными состояния

main parameters: 
1. is_keeper{idx}_box -- является ли игровой объект тем, которому разрешено брать груз или нет
True = да, False - Not 
2. attack{idx} -- может ли игровой объект атаковать 
3. has_cargo{idx} -- имеет ли игровой объект груз или нет
4. need_recharge{idx} -- нужна ли игровому объекту перезарядка или не нужн
5. free_recharge{1}  -- ?? свободна ли станция (неизвестно имеется или нет)
6. amount_patrons{idx}  -- кол-во патронов у игрового объекта
7. dst{idx} -- назначение пункта назначения у игрового объекта 
9. pos_box{idx} -- позиция коробко для награды 
10. "is_landing{idx}" -- имеется ли статус посадки у дрона
11. "take_cargo{idx}" -- нужно ли брать игровому объекту груз или нет
12. car_current_position{i}
13. "is_blocked{idx}" - заблокирован ли игровой объект 
14. "dst_position_obj_reached{idx}" - достиг ли игровой объект точку
15. "give_cargo{idx}" - нужно ли брать игровому объекту отдавать груз 
16. "current_position{idx}" -- текущая позиция дрона
17. obj_position{idx}" -- домашняя позиция игрового обхекта (координаты его стартовой площадки)
18. "need_takeoff{idx}" -- нужно ли взлетать дрону или нет 
19. "need_land{idx}" -- нужно ли совершать посадку
20. "recharge_position_station{idx}" -- позиция площадки перезарядкии
21. "box_reward_position" - позиция награды коробочки
'''


class AIManagerBlackboard:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(AIManagerBlackboard, cls).__new__(cls, *args, *kwargs)
            cls._instance.writer = AIManagerBlackboard.__create_blackboard_client()
        return cls._instance

    @staticmethod
    def __create_blackboard_client() -> blackboard.Blackboard:
        writer = blackboard.Blackboard()
        return writer

    @classmethod
    def add_recharge_information(cls, pos_a: list[int], pos_b: list[int]):
        cls._instance.writer.set(variable_name=f"pos_recharge{1}", value=pos_a)
        cls._instance.writer.set(variable_name=f"pos_recharge{2}", value=pos_b)
        cls._instance.writer.set(variable_name=f"free_recharge{1}", value=False)
        cls._instance.writer.set(variable_name=f"free_recharge{2}", value=False)

    @classmethod
    def add_home_position(cls, my_positions_ids, home_positions):
        for idx, home_pos in zip(my_positions_ids, home_positions):
            cls._instance.writer.set(variable_name=f"obj_position{idx}", value=home_pos)

    @classmethod
    def __get_home_position_all(cls, my_positions_ids):
        home_positions = []
        for idx in my_positions_ids:
            home_positions.append(cls._instance.writer.get(f"obj_position{idx}"))
        return home_positions

    @classmethod
    def set_main_status_for_game_object(cls, indexes: list[int]):
        for idx in indexes:
            cls._instance.writer.set(variable_name=f"is_keeper{idx}_box", value=False)
            cls._instance.writer.set(variable_name=f"attack{idx}", value=False)
            cls._instance.writer.set(variable_name=f"has_cargo{idx}", value=False)
            cls._instance.writer.set(variable_name=f"need_recharge{idx}", value=False)
            cls._instance.writer.set(variable_name=f"amount_patrons{idx}", value=3)
            cls._instance.writer.set(variable_name=f"is_blocked{idx}", value=False)
            cls._instance.writer.set(variable_name=f"dst_position_obj_reached{idx}", value = False)
            cls._instance.writer.set(variable_name=f"take_cargo{idx}", value = False)
            cls._instance.writer.set(variable_name=f"give_cargo{idx}", value=False)

    @classmethod
    def set_current_position_idx(cls, idx, position= (0, 0, 0)):
        cls._instance.writer.set(variable_name=f"current_position{idx}", value=position)

    @classmethod
    def set_take_cargo_status_idx(cls, idx, status: bool):
        cls._instance.writer.set(variable_name=f"take_cargo{idx}", value=status)

    @classmethod
    def set_give_cargo_status_idx(cls, idx, status: bool):
        cls._instance.writer.set(variable_name=f"give_cargo{idx}", value=status)

    @classmethod
    def set_recharge_position_station(cls, idx, position):
        cls._instance.writer.set(variable_name=f"recharge_position_station{idx}", value=position)

    @classmethod
    def set_status_all_drone_landing(cls, idx_drones):
        for idx in idx_drones:
            cls._instance.writer.set(variable_name=f"need_takeoff{idx}", value=False)
            cls._instance.writer.set(variable_name=f"need_land{idx}", value=False)

    @classmethod
    def set_box_reward_position(cls, position: list):
        cls._instance.writer.set(variable_name=f"box_reward_position", value=position)

    @classmethod
    def set_status_drone_landing(cls, idx, status):
        cls._instance.writer.set(variable_name=f"is_landing{idx}", value=status)

    @classmethod
    def set_status_has_cargo(cls, idx, status):
        cls._instance.writer.set(variable_name=f"has_cargo{idx}", value=status)

    @classmethod
    def set_status_need_recharge(cls, idx, status):
        cls._instance.writer.set(variable_name=f"need_recharge{idx}", value=status)

    @classmethod
    def set_keeper_status(cls, idx, status=False):
        cls._instance.writer.set(variable_name=f"is_keeper{idx}_box", value=status)

    @classmethod
    def set_attack_status_idx(cls, idx, status=False):
        cls._instance.writer.set(variable_name=f"attack{idx}", value=status)

    @classmethod
    def set_amount_patrons_idx(cls, idx, amount):
        cls._instance.writer.set(variable_name = f"amount_patrons{idx}", value=amount)

    @classmethod
    def set_blocked_status_idx(cls, idx, status):
        cls._instance.writer.set(variable_name = f"is_blocked{idx}", value=status)

    @classmethod
    def set_dst_position_idx(cls, idx, position):
        cls._instance.writer.set(variable_name = f"dst_position_obj{idx}", value=position)

    @classmethod
    def set_status_reaching_dst_target(cls, idx, status):
        cls._instance.writer.set(variable_name = f"dst_position_obj_reached{idx}", value=status)

    @classmethod
    def set_takeoff_status_drone(cls, idx, value: bool):
        cls._instance.writer.set(variable_name=f"need_takeoff{idx}", value=value)

    @classmethod
    def set_landing_status_drone(cls, idx, value):
        cls._instance.writer.set(variable_name=f"need_land{idx}", value=value)

    @classmethod
    def get_take_cargo_status_idx(cls, idx):
        status = cls._instance.writer.get(f"take_cargo{idx}")
        return status

    @classmethod
    def get_give_cargo_status_idx(cls, idx):
        status = cls._instance.writer.get(f"give_cargo{idx}")
        return status

    @classmethod
    def get_home_position(cls, idx):
        home_pos = cls._instance.writer.get(f"obj_position{idx}")
        return home_pos

    @classmethod
    def get_is_keeper_idx_status(cls, idx):
        keeper_status = cls._instance.writer.get(f"is_keeper{idx}_box")
        return keeper_status

    @classmethod
    def get_attack_idx_status(cls, idx):
        attack_status = cls._instance.writer.get(f"attack{idx}")
        return attack_status

    @classmethod
    def get_has_cargo_idx_status (cls, idx):
        has_cargo_status = cls._instance.writer.get(f"has_cargo{idx}")
        return has_cargo_status

    @classmethod
    def get_recharge_idx_status(cls, idx):
        recharge_status_idx = cls._instance.writer.get(f"need_recharge{idx}")
        return recharge_status_idx

    @classmethod
    def get_drone_landing_idx_status(cls, idx):
        status = cls._instance.writer.get(f"is_landing{idx}")
        return status

    @classmethod
    def get_amount_patrons_idx(cls, idx):
        amount = cls._instance.writer.get(f"amount_patrons{idx}")
        return amount

    @classmethod
    def get_blocked_status_idx(cls, idx):
        status = cls._instance.writer.get(f"is_blocked{idx}")
        return status

    @classmethod
    def get_box_reward_position(cls):
        position = cls._instance.writer.get(f"box_reward_position")
        return position

    @classmethod
    def get_dst_position_idx(cls, idx):
        position = cls._instance.writer.get(f"dst_position_obj{idx}")
        return position

    @classmethod
    def get_status_reaching_dst_target(cls, idx):
        status = cls._instance.writer.get(f"dst_position_obj_reached{idx}")
        return status

    @classmethod
    def get_takeoff_status_drone(cls, idx):
        status = cls._instance.writer.get(f"need_takeoff{idx}")
        return status

    @classmethod
    def get_landing_status_drone(cls, idx):
        cls._instance.writer.get(f"need_land{idx}")

    @classmethod
    def get_recharge_position_station(cls, idx):
        position = cls._instance.writer.get(f"recharge_position_station{idx}")
        return position

    @classmethod
    def get_current_position_idx(cls, idx):
        position = cls._instance.writer.get(f"current_position{idx}")
        return position






