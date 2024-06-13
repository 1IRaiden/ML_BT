import json

path = 'game.json'
_path = 'f.json'

with open(_path, 'r') as f:
    data: dict = json.load(f)

data_keys = []



print(data)
print(data.keys())

print(data['players_info']['players'])


