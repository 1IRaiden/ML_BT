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


'''
=====================
    О декораторах: 

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

===============================

Поговорим об основных дейсвиях машинках:
    - Attack
    - Movement
    - Recharge
    - MovementToTarget
    - Stop
    - TakeCargo
    - GiveCargo 
    - Blocking
    - Initiate
Их особенности будет представлены ниже перед описанием каждого из класса...
'''


def status_blocked(idx):
    return AIManagerBlackboard.get_blocked_status_idx(idx)


""" 
==============================
class Nav позволяет задать поведение по умолчанию для классов наследников,
то есть задать навигационую карту для иных дейсвий которые будут 
требовать взаимодейсвия с ней
"""


class Nav:
    def __init__(self, nav_map):
        self.map = nav_map


"""
Класс Initiate определяет будет ли дрон или машинка активной для агента (об агентах будет рассказано в другом скрипте)
** Требует дописать логику которая будет определять его активность - один из способов это сделать - 
исследовать текущие координаты машинки, насколько мне известно при неактивности машинки координаты будут крайне большие
"""

class Initiate(Behaviour):
    def __init__(self, name, car: Car):
        super().__init__(name)
        self.game_car = car

    def update(self):
        if IF_FORWARD:
            self.game_car.set_connection('localhost', f'{8000 + self.game_car.id}')
        time.sleep(1)
        return Status.SUCCESS


"""
Класс Movement определяет хаотичное движение тела. Как было сказано ранее в каких-то дейсвиях необходима навигационная карта.
Основная задача этого действия получить начальное положение и конечное положение и получить от класса BuildNavMap2D 
путь через вершина которого необходимо двигаться. Так же этот класс проверяет достиг ли объект конечного своего состояния или нет
Каждый промежуток времени time_movement происходит прерывание маршрута и данные маршрута изменяются. Так же только этот класс может заставить машинку
поехать на станцию перезарядки 
"""


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
        # self.src = AIManagerBlackboard.get_current_position_idx(self.game_car.id)
        # self.src = BuildNavMap2D.get_number_node_from_position(self.src)
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

"""
Реализация этого дейсвия похожа на реализацию просто действия Movement - разница в том, 
что здесь назначается вполне конечная физическая точка, или позиция коробки или позиция домашней стартовой площадки
Так же здесь тело не испытывает прерывания маршрута, а просто пытается достич его до последнего
"""


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

"""Этот класс большой логикой не обладает, его задача просто добавить задержку, если будет вознать проблема при движении"""


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


"""
Класс Attack как и любой другой класс создан для логирования статуса атаки, 
он позволяет отлеживать логику и статус каждой машинки
"""


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

"""
Класс takeCargo следит за тем, чтобы дать команду машинке драть груз, предварительно проверяя статусы дейсвительно ли машинка является той,
которая должна взять груз в случае неудачи будет выдан результат Failure. Данная логика реализована через blackboard 
О blackboard будет расскахано отдельно
"""


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


"""
Класс GiveCargo следит за тем, чтобы дать команду машинке отдать груз, данный класс устанавливает и разрешает машине дать команду на отдачу груза
Данная логика реализована через blackboard О blackboard будет расскахано отдельно
"""


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


"Класс Recharge - отвечает за перезарядку Дрона, то есть позволяет грузу сделать перезарядку"


class Recharge(Behaviour):
    def __init__(self, name, car: Car):
        super().__init__(name)
        self.time_recharge = 30
        self.game_car = car

    def update(self):
        if status_blocked(self.game_car.id):
            return Status.FAILURE

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

"""
Статус для этого класса проверяет на протяжении всех действий, если параметр blocked = True, то тогда
дерево попадет сюда 
"""


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























