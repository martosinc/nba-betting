import os, json
from .utils import get_seasons

def check_team(data, team):
    if team in data:
        return
    data[team] = []

def check_index(index_path):
    if os.path.exists(index_path):
        return
    os.mkdir(index_path)
    f = open(index_path + "/index.json", "w")
    f.write("{}")
    f.close()

def load_data(season, game, team):
    check_index(f"./data/{season}/index/") 
    f = open(f"./data/{season}/index/index.json", "r+")
    data = json.load(f)
    check_team(data, team)
    data[team].append(game)
    f.seek(0)
    json.dump(data, f)
    f.truncate()

def game_index(season, game):
    team1 = game[-7:][:3]
    team2 = game[-7:][4:]
    load_data(season, game, team1)
    load_data(season, game, team2)

def index_season(season):
    for game in sorted(os.listdir(f"./data/{season}/")):
        print(game)
        if len(game) > 15:
            game_index(season, game)

def index_seasons(period):
    for season in get_seasons(period):
        index_season(season)