import os
import pandas as pd
from numpy import nan

def format_stats_data(data):
    data = data.drop('Unnamed: 0', axis=1)
    data = data.rename({"Starters": "Player"}, axis=1)
    data.insert(1, "Starter", [1] * 5 + [0] * (len(data) - 5))
    data = data.drop(5)
    data = data.replace('Did Not Play', nan)
    data = data.replace('Did Not Dress', nan)
    data['MP'] = data['MP'].map(lambda x: int(x.split(':')[0]) if type(x) == str and ':' in x else x)
    return data

def format_factors(data):
    data.drop('Unnamed: 0', axis=1, inplace=True)
    return data

def format_game_data(season, game):
    game_path = f"./data/{season}/{game}/"
    for file in os.listdir(game_path):
        if file[:3] == file[:3].upper():
            data = pd.read_csv(game_path + file)
            data = format_stats_data(data)
            data.to_csv(game_path + file, index=False)
    factors = pd.read_csv(game_path + "factors.csv")
    factors = format_factors(factors)
    factors.to_csv(game_path + "factors.csv", index=False)
            
def format_season(season):
    for game in os.listdir(f"./data/{season}"):
        if game[:4] == str(season) or game[:4] == str(season + 1):
            format_game_data(season, game)