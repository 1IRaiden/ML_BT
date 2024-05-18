import time
from abc import ABC, abstractmethod
from pioneer_sdk import Pioneer

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


class Car(Vehicle):
    def __init__(self, id):
        super().__init__()
        self.x = 0
        self.y = 0
        self.YOUR_POSITION = (0, 0)
        self.speed = 1
        self.dst = (0,0)
        self.id = id
        self.connect: Pioneer = ...

    def set_connection(self, ip, port):
        self.connect: Pioneer = Pioneer(ip=ip, mavlink_port=port, logger=True)
        time.sleep(1)

    def is_connected(self) -> bool :
        status = True if self.connect != None else False
        return status

    def include_arm(self):
        self.connect.arm()

    def movement(self, x, y=0, z=0):
        self.connect.takeoff()
        self.connect.go_to_local_point(x, y, z, 0)
        while not self.connect.point_reached():
            pass

    def get_coordinate_position(self):
        pos = self.connect.get_local_position_lps()
        print(pos)





