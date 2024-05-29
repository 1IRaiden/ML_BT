from py_trees import blackboard
from py_trees import common


class AIManagerBlackboard:
    def __init__(self):
        self.writer = AIManagerBlackboard.__create_blackboard_client()

    @staticmethod
    def __create_blackboard_client():
        writer = blackboard.Client(name="General")
        return writer

    def add_key(self, key: str = "is_keeper_key"):
        self.writer.register_key(key=key, access=common.Access.WRITE)
        self.writer.set('is_keeper_key', True)


