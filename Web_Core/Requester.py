import json
import requests
from typing import Dict


class Core:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(Core, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.command = 'http://10.10.2.63:31222/game?target=get&type_command=player&command=visualization'

    def do_require_on_server(self):
        response = requests.get(self.command)
        return response


class BoxRegard:
    def __init__(self):
        self.color = None
        self.current_position = None
        self.is_cargo = None

    def add_color(self, color: tuple):
        self.color = color

    def add_position(self, position: list):
        self.current_position = position

    def set_status_is_cargo(self, status: bool):
        self.is_cargo = status


class Researcher:
    @staticmethod
    def current_position_players(data: Dict):
        # Contain information about color teams
        color_team = []

        # this array contain id all object
        ids = []

        # this list contain information about current position
        current_positions = []

        # this list contain information about has cargo or not
        is_cargo = []

        # this list contain information about amount bullet
        nums_bullet = []

        # this list contain information about blocked
        is_blocked = []

        player_info: list = data["data"]['players_info']

        for command in player_info:
            color_team.append(command['name_team'])
            players: list = command['players']

            for player in players:
                ids.append(player['id'])
                current_positions.append(player['current_pos'][:-1])
                is_blocked.append(player['is_blocked'])

                data_roles = player['data_role']
                is_cargo.append(data_roles['is_cargo'])
                nums_bullet.append(data_roles['num_bullet'])

        return ids, current_positions, is_cargo, nums_bullet, is_blocked, color_team

    @staticmethod
    def get_config_information(data: Dict, name_teams: str):
        status = "Weapoint_RolePolygon"
        home_positions = []
        my_positions_ids = []
        recharge_position = []
        types_object = []

        player_info: list = data["data"]['players_info']
        polygon_data: list = data["data"]["polygon_data"]

        for command in player_info:
            players: list = command['players']
            for player in players:
                if command['name_team'] == name_teams:
                    my_positions_ids.append(player['id'])
                    home_positions.append(player['home_pos'])
                    types_object.append(player['type_object'][0])

        for polygon in polygon_data:
            if polygon['name_role'] == status:
                recharge_position.append(polygon['current_pos'][:-1])

        return home_positions, my_positions_ids, recharge_position, types_object

    # wrong
    @staticmethod
    def get_position_cargos(data: Dict):
        polygon_data: list = data["data"]["polygon_data"]
        boxs = []

        i = 1
        for main_info in polygon_data:
            box = BoxRegard()
            if main_info['name_role'] == 'Fabric_RolePolygon':
                box.add_color(tuple(main_info['vis_info']['color']))
                box.set_status_is_cargo(main_info['data_role']['is_cargo'])
                box.add_position(main_info['current_pos'][:-1])
                boxs.append(box)
                i += 1
                if i == 4:
                    break
        return boxs

    @staticmethod
    def get_obstacle_position():
        with open('obstacle.json', 'r') as f:
            obstacles = json.load(f)
            return obstacles['pos']



# path = r'C:\Users\user\Desktop\Проекты\MachineLeaning\MachineLearning\ML_BT\game_core.json'
# with open(path, 'r') as file:
#     data =json.load(file)
#
# print(Researcher.get_position_cargos(data))









