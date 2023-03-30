import os
import pandas as pd
from . import interface

date_offset = 20
skipped_games_barrier = 3
datadir = "./data/"
player_statline = ['MP', 'FG', 'FGA', 'FG%', '3P', '3PA', '3P%', 'FT', 'FTA', 'FT%', 'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', '+/-', 'TS%', 'eFG%', '3PAr', 'FTr', 'ORB%', 'DRB%', 'TRB%', 'AST%', 'STL%', 'BLK%', 'TOV%', 'USG%', 'ORtg', 'DRtg', 'BPM', 'qAST', 'FG_Part', 'AST_Part', 'FT_Part', 'ORB_Part', 'ScPoss', 'FGxPoss', 'TotalPoss', 'PProd_FG_Part', 'PProd_AST_Part', 'PProd_ORB_Part', 'PProd', 'Floor', 'MarginalOffense', 'MarginalPPW', 'OffWS']
factor_statline = ['Pace', 'eFG%', 'TOV%', 'ORB%', 'FT/FGA', 'ORtg', 'PTS', 'MP', 'AST', 'FG', 'FT', 'FGA', 'FTA', 'TOV', 'ORB', '3P', 'Team_Scoring_Poss', 'Team_Play', 'Team_ORB_Weight']
season_starts = {'2020':11}

def get_starters(game_data):
    starters = dict(map(lambda x: (x, list(game_data['players'].keys())[0]), ['PG', 'SG', 'SF', 'PF', 'C']))
    for player, player_data in game_data['players'].items():
        position = player_data['position']
        if starters[position] == -1 or player_data.get('MP', 0) > game_data['players'][starters[position]].get('MP', 0) and player_data['games_skipped'] < skipped_games_barrier:
        # if starters[position] == -1 or (player_data['Starter'] > game_data['players'][starters[position]]['Starter'] or (player_data.get('PTS', 0) > game_data['players'][starters[position]].get('PTS', 0))) and player_data['games_skipped'] < skipped_games_barrier:
            starters[position] = player
    return starters.values()

def team_record(team, team_data, team_starters):
    team_record = [team]
    for factor in factor_statline:
        team_record.append(team_data['team'][factor])
    for starter in team_starters:
        statline = dict(map(lambda x: (x, 0), player_statline))
        for stat_name, stat in team_data['players'][starter].items(): 
            if stat_name in statline:
                statline[stat_name] = stat
        team_record.extend(statline.values())
    return team_record
    

def create_record(home, visitor, home_data, visitor_data, winner, date):
    home_starters = get_starters(home_data)
    visitor_starters = get_starters(visitor_data)
    return [date] + team_record(home, home_data, home_starters) + team_record(visitor, visitor_data, visitor_starters) + [winner]

def create_game_record(season, game):
    home = game[-3:]
    visitor = game[-7:-4]
    date = pd.Timestamp(game[:-7])
    season_start = 10
    if season in season_starts:
        season_start = season_starts[season]
    if 7 < date.month < season_start:
        date = pd.Timestamp(f'{int(season) - 1}-{season_start}-25')
    home_data = interface.load(season, home, date - pd.DateOffset(date_offset), date)
    visitor_data = interface.load(season, visitor, date - pd.DateOffset(date_offset), date)
    _, home_points = interface.load_game_data(home, os.path.join(datadir, season, game) + '/')
    _, visitor_points = interface.load_game_data(visitor, os.path.join(datadir, season, game) + '/')
    winner = int(home_points > visitor_points)
    return create_record(home, visitor, home_data, visitor_data, winner, date)

def get_columns():
    home_column = ['Home']
    home_column.extend(map(lambda stat: 'Home ' + stat, factor_statline))
    for player in ['PG', 'SG', 'SF', 'PF', 'C']:
        home_column.extend(map(lambda stat: 'Home ' + player + ' ' + stat, player_statline))
    visitor_column = ['Visitor']
    visitor_column.extend(map(lambda stat: 'Visitor ' + stat, factor_statline))
    for player in ['PG', 'SG', 'SF', 'PF', 'C']:
        visitor_column.extend(map(lambda stat: 'Visitor ' + player + ' ' + stat, player_statline))
    return ['Date'] + home_column + visitor_column + ['Winner']

def create_dataset():
    for season in sorted(os.listdir(datadir)):
        df = pd.DataFrame(columns=get_columns())
        for game in os.listdir(datadir + season):
            if len(game) > 15:
                record = create_game_record(season, game)
                df.loc[len(df)] = record
        df.to_csv(f'dataset/season{season}.csv', index=False)
        print(f'Loaded season {season}')