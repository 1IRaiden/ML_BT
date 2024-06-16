from enum import Enum


AMOUNT_CAR = 0
ALL_AI_OBJECT = 0


class TypeObject(Enum):
    geo_car = "EduBotObject",
    geo_drone = 'PioneerObject'

import json
data = {
    'pos': ((2.4, 2.6), (1.1, 1.6), (2.3, 1.4), (6.5, 7.8))
}

with open('obstacle.json', 'w') as f:
    json.dump(data, f, indent=2)
