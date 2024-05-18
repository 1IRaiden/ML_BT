import random
import numpy as np


class AIManager:
    def __init__(self):
        pass

    def set_unable_node(self):
        node = np.random.randint(0, 99)
        typ = random.choice(('friendly', 'unfriendly'))
        return node, typ

    def get_position_players(self):
        pass


