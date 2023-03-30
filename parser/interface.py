import json
import pandas as pd
from numpy import nan
from .utils import lower_bound
from .stats import Team, Player

def process_data(games, season, team):
    data = {'players':dict(), 'team':dict()}
    players = set()
    for game in games:
        players = players | set(game['players'])
    team_data = Team(games)
    games_team_data = team_data.get_games_stats()
    for game_index in range(len(games)):
        games[game_index]['team'] = games_team_data[game_index]
    for player in players:
        player_data = Player(games, player)
        data['players'][player] = player_data.get_mean()
        data['players'][player]['games_skipped'] = player_data.games_skipped
        data['players'][player]['position'] = get_position(player, team, season)
    data['team'] = team_data.get_mean()
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
    
    data['team'] = load_factors(team, factors)
    data['players'] = dict()
    
    for player in basic['Player'][:-1]:
        data['players'][player] = load_player_data(player, basic)
    for player in advanced['Player'][:-1]:
        data['players'][player] = data['players'][player] | load_player_data(player, advanced)
        data['players'][player]['did_play'] = 1
    
    for player in inactive[team]:
        data['players'][player] = {'did_play': 0}

    return data, float(basic.iloc[-1]['PTS'])

def load(season, team, start, end):
    index = json.load(open(f"./data/{season}/index/index.json", "r"))[team]
    indexed_games = list(map(lambda x: x[:-7], index))
    indexed_games = list(map(pd.Timestamp, indexed_games))

    start_game = lower_bound(indexed_games, start)
    if start <= indexed_games[start_game - 1]: start_game -= 1
    end_game = lower_bound(indexed_games, end) - 1
    if indexed_games[end_game] == end: end_game = max(end_game - 1, 0)
    if end >= indexed_games[-1]: end_game += 1

    if end_game + 1 == start_game: end_game += 1

    
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