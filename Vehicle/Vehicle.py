import time
from pioneer_sdk import Pioneer
from abc import ABC, abstractmethod
from ML_BT.SystemNavigation.ManagerMovement import AIManager
from ML_BT.Vehicle.edubot_sdk import EdubotGCS


class Vehicle(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def set_connection(self, ip, port):
        pass

    @abstractmethod
    def is_connected(self):
        pass

    @abstractmethod
    def include_arm(self):
        pass

    @abstractmethod
    def move_for_target(self, _id, x, y=0):
        pass


class Drone(Vehicle):
    def __init__(self, id):
        super().__init__()
        self.x = 0
        self.y = 0
        self.dst = (0, 0)
        self.id = id
        self.connect: Pioneer = ...

    def set_connection(self, ip, port):
        self.connect: Pioneer = Pioneer(ip=ip, mavlink_port=port, logger=False)
        print("Success")

    def takeoff(self):
        self.connect.takeoff()
        print("Взлет")
        time.sleep(2)

    def land(self):
        self.connect.land()

    def is_connected(self) -> bool:
        if self.connect:
            return True
        else:
            return False

    def include_arm(self):
        self.connect.arm()

    def move_for_target(self, _id, x, y=0, z=0):
        self.connect.go_to_local_point(x, y, z, 0)
        while not self.connect.point_reached():
            time.sleep(0.3)

    # This method return position points
    def get_coordinate_position(self, _id):
        try:
            data = self.connect.get_local_position_lps()
            if data:
                self.x = data[0]
                self.y = data[1]
                AIManager.update_position_cars(_id, data[0], data[1])
        except Exception:
            pass
        finally:
            time.sleep(0.1)


class Car(Vehicle):
    def __init__(self, id):
        super().__init__()
        self.connect: EdubotGCS = ...
        self.x = 0
        self.y = 0
        self.dst = (0, 0)
        self.id = id

    def set_connection(self, ip, port):
        try:
            self.connect = EdubotGCS(ip=ip, mavlink_port=port)
            print(ip, port)
        except Exception:
            print("Не удалось подключиться к машинке")

    def is_connected(self) -> bool:
        if not self.connect:
            return False
        else:
            return True

    def move_for_target(self, _id, x, y=0):
        self.connect.go_to_local_point(x, y)
        while not self.connect.point_reached():
            time.sleep(0.3)

    def include_arm(self):
        time.sleep(1)











