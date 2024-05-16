import typing
import time
from py_trees.behaviour import Behaviour
from py_trees.common import Status
from py_trees.composites import Sequence, Parallel
from py_trees import logging as log_tree
from py_trees.decorators import Inverter



class Action(Behaviour):
    def __init__(self, name, max_attempt_count=1):
        super(Action, self).__init__(name)

    def setup(self):
        self.logger.debug("  %s [Action::setup()]" % self.name)

    def initialise(self):
        self.logger.debug("  %s [Action::initialise()]" % self.name)

    def update(self):
        self.logger.debug("  %s [Action::update()]" % self.name)
        time.sleep(3)
        return Status.FAILURE

    def terminate(self, new_status):
        self.logger.debug(f"%s Action::terminate {self.name} to {new_status}")



class Condition(Behaviour):
    def __init__(self, name):
        super(Condition, self).__init__(name)

    def setup(self):
        self.logger.debug("  %s [Condition::setup()]" % self.name)

    def initialise(self):
        self.logger.debug("  %s [Condition::initialise()]" % self.name)

    def update(self):
        self.logger.debug("  %s [Condition::update()]" % self.name)
        time.sleep(1)
        # return Status.FAILURE
        return Status.SUCCESS

    def terminate(self, new_status):
        self.logger.debug(f"%s Condition::terminate {self.name} to {new_status}")


def make_bt():
    root = Sequence(name="sequence", memory=True)

    check_battery = Condition("check_batterly")
    open_grip = Inverter("open_grip_Inverter", Action("open_grip"))
    approach_object = Inverter("approach_object_Inverter", Action("approach_object"))
    close_grip = Inverter("close_grip_Inverter", Action("close_grip"))

    root.add_children([
        check_battery,
        open_grip,
        approach_object,
        close_grip
    ])
    return root


if __name__ == "__main__":
    log_tree.level = log_tree.level.DEBUG
    tree = make_bt()
    tree.tick_once()