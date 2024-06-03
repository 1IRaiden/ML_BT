import time
from pioneer_sdk import Pioneer
from abc import ABC, abstractmethod
from ML_BT.SystemNavigation.ManagerMovement import AIManager


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
    def move_for_target(self, _id, x, y=0, z=0):
        pass


class Car(Vehicle):
    def __init__(self, id):
        super().__init__()
        self.x = 0
        self.y = 0
        self.YOUR_POSITION = (0, 0)
        self.dst = (0, 0)
        self.id = id
        self.connect: Pioneer = ...

    def set_connection(self, ip, port):
        self.connect: Pioneer = Pioneer(ip=ip, mavlink_port=port, logger=False)
        self.connect.takeoff()

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
            #if AIManager.get_event_status():
            # print("I not think", AIManager.get_event_status())
            #if AIManager.event.is_set():
                #self.get_coordinate_position(_id)
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








