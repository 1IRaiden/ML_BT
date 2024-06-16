import json
import time
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


# data = {
#     'current_position_car_1': (5, 7, 0),
#     'current_position_car_2': (3, 1, 0),
#     'current_position_car_3': (1, 1, 0),
# }
#

# path = "config.json"
# path_reward = "config_box.json"
# path_current = "current_positions.json"



# with open(path_current, 'w') as file:
#   json.dump(data, file, indent=4)

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


# ata = {"data":{"players_info":[{"city_team":"name city is now set","color_team":[0,0,255],"name_team":"Blue","players":[{"current_pos":[-10.0,-10.0,0.0,0.0],"data_object":{"stateObject":0},"data_role":{"bonus_list":[],"cargo_color":[],"health":100,"is_cargo":False,"is_shooting":False,"num_bullet":3,"state":0},"home_pos":[-0.68,0.187,0.0],"id":0,"is_blocked":False,"type_object":["PioneerObject"]},{"current_pos":[-10.0,-10.0,0.0,0.0],"data_object":{"stateObject":0},"data_role":{"bonus_list":[],"cargo_color":[],"health":100,"is_cargo":False,"is_shooting":False,"num_bullet":3,"state":0},"home_pos":[-4.25,-1.99,0.0],"id":1,"is_blocked":False,"type_object":["PioneerObject"]},{"current_pos":[-10.0,-10.0,0.0,0.0],"data_object":{"stateObject":0},"data_role":{"bonus_list":[],"cargo_color":[],"health":100,"is_cargo":False,"is_shooting":False,"num_bullet":3,"state":0},"home_pos":[-4.25,1.78,0.0],"id":2,"is_blocked":False,"type_object":["PioneerObject"]},{"current_pos":[-10.0,-10.0,0.0,0.0],"data_object":{"stateObject":0},"data_role":{"bonus_list":[],"cargo_color":[],"health":100,"is_cargo":False,"is_shooting":False,"num_bullet":3,"state":0},"home_pos":[-4.25,3.83,0.0],"id":3,"is_blocked":False,"type_object":["PioneerObject"]},{"current_pos":[20,20,0,0],"data_object":{"stateObject":0},"data_role":{"bonus_list":[],"cargo_color":[],"health":100,"is_cargo":False,"is_shooting":False,"num_bullet":3,"state":0},"home_pos":[[0,0,0]],"id":4,"is_blocked":False,"type_object":["PTZObject"]}],"score_team":0},{"city_team":"name city is now set","color_team":[255,0,0],"name_team":"Red","players":[{"current_pos":[-10.0,-10.0,0.0,0.0],"data_object":{"stateObject":0},"data_role":{"bonus_list":[],"cargo_color":[],"health":100,"is_cargo":False,"is_shooting":False,"num_bullet":3,"state":0},"home_pos":[4.35,-3.93,0.0],"id":5,"is_blocked":False,"type_object":["EduBotObject"]},{"current_pos":[-10.0,-10.0,0.0,0.0],"data_object":{"stateObject":0},"data_role":{"bonus_list":[],"cargo_color":[],"health":100,"is_cargo":False,"is_shooting":False,"num_bullet":3,"state":0},"home_pos":[4.35,-2.1,0.0],"id":6,"is_blocked":False,"type_object":["EduBotObject"]},{"current_pos":[-10.0,-10.0,0.0,0.0],"data_object":{"stateObject":0},"data_role":{"bonus_list":[],"cargo_color":[],"health":100,"is_cargo":False,"is_shooting":False,"num_bullet":3,"state":0},"home_pos":[4.35,1.77,0.0],"id":7,"is_blocked":False,"type_object":["EduBotObject"]},{"current_pos":[-10.0,-10.0,0.0,0.0],"data_object":{"stateObject":0},"data_role":{"bonus_list":[],"cargo_color":[],"health":100,"is_cargo":False,"is_shooting":False,"num_bullet":3,"state":0},"home_pos":[4.35,3.9,0.0],"id":8,"is_blocked":False,"type_object":["EduBotObject"]},{"current_pos":[20,20,0,0],"data_object":{"stateObject":0},"data_role":{"bonus_list":[],"cargo_color":[],"health":100,"is_cargo":False,"is_shooting":False,"num_bullet":3,"state":0},"home_pos":[[0,0,0]],"id":9,"is_blocked":False,"type_object":["PTZObject"]}],"score_team":0}],"polygon_data":[{"current_pos":[0.4,-2.52,0.0,0],"data_role":{"current_cargo_color":[],"current_conditions":0,"is_cargo":False,"num_cargo":0},"name_role":"Fabric_RolePolygon","vis_info":{"color":[0,0,0],"description":""}},{"current_pos":[-0.68,0.187,0.0,0],"data_role":{"current_cargo_color":[],"current_conditions":0,"is_cargo":False,"num_cargo":0},"name_role":"Fabric_RolePolygon","vis_info":{"color":[0,0,0],"description":""}},{"current_pos":[0.25,2.82,0.0,0],"data_role":{"current_cargo_color":[],"current_conditions":0,"is_cargo":False,"num_cargo":0},"name_role":"Fabric_RolePolygon","vis_info":{"color":[0,0,0],"description":""}},{"current_pos":[1000.0,1000.0,0.0,0],"data_role":{"current_cargo_color":[],"current_conditions":0,"is_cargo":False,"num_cargo":0},"name_role":"Fabric_RolePolygon","vis_info":{"color":[0,0,0],"description":""}},{"current_pos":[-4.25,-3.65,0.0,0],"data_role":{},"name_role":"TakeoffArea_RolePolygon","vis_info":{"color":[0,0,0],"description":"1"}},{"current_pos":[-4.25,-1.99,0.0,0],"data_role":{},"name_role":"TakeoffArea_RolePolygon","vis_info":{"color":[0,0,0],"description":"2"}},{"current_pos":[-4.25,1.78,0.0,0],"data_role":{},"name_role":"TakeoffArea_RolePolygon","vis_info":{"color":[0,0,0],"description":"3"}},{"current_pos":[-4.25,3.83,0.0,0],"data_role":{},"name_role":"TakeoffArea_RolePolygon","vis_info":{"color":[0,0,0],"description":"4"}},{"current_pos":[-4.25,-0.15,0.0,0],"data_role":{},"name_role":"Weapoint_RolePolygon","vis_info":{"color":[0,0,0],"description":"1"}},{"current_pos":[4.35,-0.2,0.0,0],"data_role":{},"name_role":"Weapoint_RolePolygon","vis_info":{"color":[0,0,0],"description":"2"}},{"current_pos":[4.35,-3.93,0.0,0],"data_role":{},"name_role":"TakeoffArea_RolePolygon","vis_info":{"color":[0,0,0],"description":"3"}},{"current_pos":[4.35,-2.1,0.0,0],"data_role":{},"name_role":"TakeoffArea_RolePolygon","vis_info":{"color":[0,0,0],"description":"4"}},{"current_pos":[4.35,1.77,0.0,0],"data_role":{},"name_role":"TakeoffArea_RolePolygon","vis_info":{"color":[0,0,0],"description":"5"}},{"current_pos":[4.35,3.9,0.0,0],"data_role":{},"name_role":"TakeoffArea_RolePolygon","vis_info":{"color":[0,0,0],"description":"5"}},{"current_pos":[4.35,1.77,0.0,0],"data_role":{},"name_role":"TakeoffArea_RolePolygon","vis_info":{"color":[0,0,0],"description":"5"}},{"current_pos":[4.35,3.9,0.0,0],"data_role":{},"name_role":"TakeoffArea_RolePolygon","vis_info":{"color":[0,0,0],"description":"5"}}]},"result": True,"status":0}
# ith open("game_core.json", 'w') as file:
#    json.dump(data, file, indent=4)