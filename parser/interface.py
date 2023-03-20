import json
import pandas as pd
from numpy import nan
from utils import lower_bound

def process_data(games, season, team):
    data = dict()
    players = set(games[-1])
    for player in players:
        statline = set()
        for game in games:
            if game.get(player) != None:
                statline = statline | set(game[player])
        data[player] = {k : sum(map(lambda game: 0 if game.get(player) == None or game[player].get(k) == None else game[player][k], games)) for k in statline}
    for player in players:
        if player == 'factors': continue
        try : data[player]['games_played']
        except: print(data)
        if data[player]['games_played']:
            data[player] = {k : data[player][k] / data[player]['games_played'] for k in set(data[player])}
            data[player] = {stat : round(data[player][stat], 2) for stat in set(data[player])}
        del data[player]['games_played']
        games_skipped = 0
        game_index = len(games) - 1
        while game_index >= 0 and games[game_index].get(player) != None and games[game_index][player]['games_played'] == 0:
            game_index -= 1
        games_skipped = len(games) - (game_index + 1)
        data[player]['games_skipped'] = games_skipped
        if 'Starter' not in data[player]:
            data[player]['Starter'] = 0
        data[player]['position'] = get_position(player, team, season)
    data['factors'] = {k : data['factors'][k] / len(games) for k in set(data['factors'])}
    data = {'players':data, 'factors':data['factors']}
    del data['players']['factors']
    return data

def load_player_data(player, data):
    player_idx = data.index[data['Player'] == player][0]
    player_data = data.to_dict(orient="records")[player_idx]
    del player_data['Player']
    return player_data

def load_factors(team, factors):
    team_index = factors.index[factors['Team'] == team][0]
    team_factors = factors.to_dict(orient="records")[team_index]
    del team_factors['Team']
    return team_factors

def load_game_data(team, game_path):
    data = dict()
    
    factors = pd.read_csv(game_path + "factors.csv")
    basic = pd.read_csv(game_path + team + ".csv")
    advanced = pd.read_csv(game_path + team + "Adv.csv")
    inactive = json.load(open(game_path + "inactive.json"))
    basic = basic.replace({nan:None})
    advanced = advanced.replace({nan:None})
    
    data['factors'] = load_factors(team, factors)
    
    for player in basic['Player'][:-1]:
        data[player] = load_player_data(player, basic)
    for player in advanced['Player'][:-1]:
        data[player] = data[player] | load_player_data(player, advanced)
        data[player]['games_played'] = 1
    
    for player in inactive[team]:
        data[player] = {'games_played': 0}

    return data, float(basic.iloc[-1]['PTS'])

def load(season, team, start, end):
    index = json.load(open(f"./data/{season}/index/index.json", "r"))[team]
    indexed_games = list(map(lambda x: x[:-7], index))
    indexed_games = list(map(pd.Timestamp, indexed_games))
    
    start_game = lower_bound(indexed_games, start)
    if start <= indexed_games[start_game - 1]: start_game -= 1
    end_game = lower_bound(indexed_games, end) - 1
    if end >= indexed_games[-1]: end_game += 1
    
    games = []
    for date_index in range(start_game, end_game + 1):
        game_data = load_game_data(team, f"./data/{season}/{index[date_index]}/")
        games.append(game_data[0])
    data = process_data(games, season, team)
    
    return data

def get_position(player, team, season):
    positions_path = f'./data/{season}/positions.json'
    positions = json.load(open(positions_path))
    try:
        return positions[team][player]
    except:
        return 'PG'