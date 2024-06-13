import json
from typing import Dict

# data = {
#     'car_1': (2, 2.5, 0),
#     'car_2': (2, -2.5, 0),
#     'car_3': (-2, 2.5, 0),
# }
# path = "config.json"

# data = {
#     'box_1': (4, 5, 0),
#     'box_2': (2, 2.5, 0),
#     'box_3': (0, 7, 0),
#     'reward_1': 10,
#     'reward_2': 5,
#     'reward_3': 20,
# }


data = {
    'current_position_car_1': (5, 7, 0),
    'current_position_car_2': (3, 1, 0),
    'current_position_car_3': (1, 1, 0),
}


path = "config.json"
path_reward = "config_box.json"
path_current = "current_positions.json"



with open(path_current, 'w') as file:
  json.dump(data, file, indent=4)

# def get_start_position_from_config(file: str):
#     positions = []
#     with open(file, 'r') as f:
#         data: Dict = json.load(f)
#         for pos in data.values():
#             positions.append(pos)
#         return positions

# with open(path_reward, 'r') as f:
#     container = json.load(f)
#     pos_box_1 = container['box_1']
#     pos_box_2 = container['box_2']
#     pos_box_3 = container['box_3']
#
#     box_1_reward = container['reward_1']
#     box_2_reward = container['reward_2']
#     box_3_reward = container['reward_3']
#
# print(pos_box_1, pos_box_2, pos_box_3, box_1_reward, box_2_reward, box_3_reward)


# po = get_start_position_from_config(path)
# print(po)