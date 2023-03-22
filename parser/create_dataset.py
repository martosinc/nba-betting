import os
import pandas as pd
import interface

date_offset = 10
skipped_games_barrier = 3
datadir = "./data/"
player_statline = ['3P%', 'TOV%', 'DRB%', 'PF', 'FTr', 'FG', 'FT%', 'BLK', 'FTA', 'BPM', 'TOV', 'eFG%', 'STL', 'DRtg', 'TRB', 'BLK%', 'AST', 'PTS', 'ORtg', 'STL%', 'TRB%', '3P', 'FG%', 'USG%', 'FT', 'ORB%', '3PA', 'ORB', '3PAr', 'MP', 'DRB', '+/-', 'TS%', 'AST%', 'FGA']
factor_statline = ['FT/FGA', 'ORtg', 'TOV%', 'ORB%', 'eFG%', 'Pace']
season_starts = {'2020':11}

def get_starters(game_data):
    starters = dict(map(lambda x: (x, list(game_data['players'].keys())[0]), ['PG', 'SG', 'SF', 'PF', 'C']))
    for player, player_data in game_data['players'].items():
        position = player_data['position']
        if starters[position] == -1 or player_data.get('MP', 0) > game_data['players'][starters[position]].get('MP', 0) and player_data['games_skipped'] < skipped_games_barrier:
            starters[position] = player
    return starters.values()

def team_record(team, team_data, team_starters):
    team_record = [team, *team_data['factors'].values()]
    for starter in team_starters:
        statline = dict(map(lambda x: (x, 0), player_statline))
        for stat_name, stat in team_data['players'][starter].items(): 
            if stat_name in statline:
                statline[stat_name] = stat
        # team_record.extend([starter, *statline.values()])
        team_record.extend(statline.values())
    return team_record
    

def create_record(home, visitor, home_data, visitor_data, winner):
    home_starters = get_starters(home_data)
    visitor_starters = get_starters(visitor_data)
    return team_record(home, home_data, home_starters) + team_record(visitor, visitor_data, visitor_starters) + [winner]

def create_game_record(season, game):
    home = game[-7:-4]
    visitor = game[-3:]
    date = pd.Timestamp(game[:-7])
    season_start = 10
    if season in season_starts:
        season_start = season_starts[season]
    if 7 < date.month < season_start:
        date = pd.Timestamp(f'{season}-{season_start}-20')
    home_data = interface.load(season, home, date - pd.DateOffset(date_offset), date)
    visitor_data = interface.load(season, visitor, date - pd.DateOffset(date_offset), date)
    _, home_points = interface.load_game_data(home, os.path.join(datadir, season, game) + '/')
    _, visitor_points = interface.load_game_data(visitor, os.path.join(datadir, season, game) + '/')
    winner = int(home_points > visitor_points)
    return create_record(home, visitor, home_data, visitor_data, winner)

def get_columns():
    home_column = ['Home']
    home_column.extend(map(lambda stat: 'Home ' + stat, factor_statline))
    for player in ['PG', 'SG', 'SF', 'PF', 'C']:
        home_column.extend(map(lambda stat: 'Home ' + player + ' ' + stat, player_statline))
    visitor_column = ['Visitor']
    visitor_column.extend(map(lambda stat: 'Visitor ' + stat, factor_statline))
    for player in ['PG', 'SG', 'SF', 'PF', 'C']:
        visitor_column.extend(map(lambda stat: 'Visitor ' + player + ' ' + stat, player_statline))
    return home_column + visitor_column + ['Winner']

def create_dataset():
    for season in os.listdir(datadir):
        df = pd.DataFrame(columns=get_columns())
        for game in os.listdir(datadir + season):
            if len(game) > 15:
                record = create_game_record(season, game)
                df.loc[len(df)] = record
        df.to_csv(f'dataset/season{season}.csv', index=False)
        print(f'Loaded season {season}')