import typing
import time
from py_trees.behaviour import Behaviour
from py_trees.common import Status
from py_trees.composites import Sequence
from py_trees import logging as log_tree



class Action(Behaviour):
    def __init__(self, name, max_attempt_count=1):
        super(Action, self).__init__(name)
        self.max_attempt_count = max_attempt_count
        self.attempt_count = max_attempt_count

    def setup(self):
        self.logger.debug("  %s [Action::setup()]" % self.name)

    def initialise(self):
        self.attempt_count = self.max_attempt_count
        self.logger.debug("  %s [Action::initialise()]" % self.name)

    def update(self):
        self.attempt_count -=1
        self.logger.debug("  %s [Action::update()]" % self.name)
        time.sleep(3)
        if not self.attempt_count:
            return Status.SUCCESS
        return Status.RUNNING

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
    open_grip = Action("open_grip", 2)
    approach_object = Action("approach_object", 5)
    close_grip = Action("close_grip", 3)

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
    for i in range(1, 10):
        try:
            print("new_tick")
            tree.tick_once()
            time.sleep(0.1)
        except KeyboardInterrupt:
            break

