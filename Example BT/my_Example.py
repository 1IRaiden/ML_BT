import time
from py_trees.behaviour import Behaviour
from py_trees.common import Status, OneShotPolicy
from py_trees.composites import Sequence, Parallel
from py_trees import logging as log_tree
import py_trees.decorators as de
from py_trees.trees import BehaviourTree


# takeoff

class AloneTakeoff(Behaviour):
    def __init__(self, name):
        super(AloneTakeoff, self).__init__(name)
        self.first = True

    def initialise(self):
        self.logger.debug("  %s [Action::initialise()]" % self.name)

    def update(self):
        if self.first:
            #self.logger.debug("  %s [Action::update()]" % self.name)
            self.logger.debug("Взлёт выполнен")
            self.first = not self.first
            return Status.SUCCESS
        else:
            self.logger.debug("Я не выполняюсь")
            return Status.FAILURE

    def terminate(self, new_status):
        self.logger.debug(f"%s Action::terminate {self.name} to {new_status}")


class Action(Behaviour):
    def __init__(self, name):
       super(Action, self).__init__(name)

    def initialise(self):
        self.logger.debug("  %s [Action::initialise()]" % self.name)

    def update(self):
        self.logger.debug("  %s [Action::update()]" % self.name)
        time.sleep(1)
        self.logger.debug("Я постоянно выполняюсь")
        return Status.SUCCESS

    # def terminate(self, new_status):
    #    self.logger.debug(f"%s Action::terminate {self.name} to {new_status}")

class LateAction(Behaviour):
    def __init__(self, name):
        super(LateAction, self).__init__(name)

    def initialise(self):
        self.logger.debug("  %s [LateAction::initialise()]" % self.name)

    def update(self):
        time.sleep(4)
        return Status.SUCCESS


def make_bt():
    root = Sequence(name="sequence", memory=True)
    takeoff = AloneTakeoff("takeoff")
    zv = de.OneShot(name= "takeoff", child=takeoff, policy=OneShotPolicy.ON_SUCCESSFUL_COMPLETION)
    smthAction = Action("action")
    attack = Action("Attack")


    late = LateAction("late")
    late_st = de.Timeout('late_st', child=late, duration=3)


    root.add_children([
        zv,
        late_st,
        smthAction,
    ])
    return root

if __name__ == "__main__":
    log_tree.level = log_tree.level.DEBUG
    root = make_bt()
    tree = BehaviourTree(root)
    try:
        while True:
            print('\n', '\n', "вызывается tick", '\n', '\n')
            tree.tick()
            time.sleep(0.1)  # Добавьте задержку, чтобы управлять частотой тиков
    except KeyboardInterrupt:
        print("\nМануальное прерывание цикла (Ctrl+C)")
