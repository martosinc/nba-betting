import pandas as pd

class Team():
    def __init__(self, games_stats):
        self.games = []
        for game_stats in games_stats:
            self.team_game_stats(game_stats)
    def team_game_stats(self, game_stats):
        stats = game_stats['team']
        Team_PTS = 0
        Team_MP = 0
        Team_AST = 0
        Team_FG = 0
        Team_FT = 0
        Team_FGA = 0
        Team_FTA = 0
        Team_TOV = 0
        Team_ORB = 0
        Team_3P = 0
        for player_name in game_stats['players']:
            player = game_stats['players'][player_name]
            for stat, value in player.items():
                if value == None:
                    player[stat] = 0
            Team_PTS += player.get('PTS', 0)
            Team_MP += player.get('MP', 0)
            Team_AST += player.get('AST', 0)
            Team_FG += player.get('FG', 0)
            Team_FT += player.get('FT', 0)
            Team_FGA += player.get('FGA', 0)
            Team_FTA += player.get('FTA', 0)
            Team_TOV += player.get('TOV', 0)
            Team_ORB += player.get('ORB', 0)
            Team_3P += player.get('3P', 0)
        if Team_MP == 0: Team_MP = 10 ** -8
        Team_Scoring_Poss = Team_FG + (1 - (1 - (Team_FT / Team_FTA)) ** 2) * Team_FTA * 0.4
        Team_Play = Team_Scoring_Poss / (Team_FGA + Team_FTA * 0.4 + Team_TOV)
        ORB_Percentage = game_stats['team']['ORB%'] / 100
        Team_ORB_Weight = ((1 - ORB_Percentage) * Team_Play) / ((1 - ORB_Percentage) * Team_Play + ORB_Percentage * (1 - Team_Play))
        stats['PTS'] = Team_PTS
        stats['MP'] = Team_MP
        stats['AST'] = Team_AST
        stats['FG'] = Team_FG
        stats['FT'] = Team_FT
        stats['FGA'] = Team_FGA
        stats['FTA'] = Team_FTA
        stats['TOV'] = Team_TOV
        stats['ORB'] = Team_ORB
        stats['3P'] = Team_3P
        stats['Team_Scoring_Poss'] = Team_Scoring_Poss
        stats['Team_Play'] = Team_Play
        stats['Team_ORB_Weight'] = Team_ORB_Weight
        stats['ORB%'] = ORB_Percentage
        self.games.append(stats)
    def get_games_stats(self):
        return self.games
    def get_mean(self):
        return dict(pd.DataFrame(self.games).mean())
        
basic_player_stats = ['3P%', 'TOV%', 'DRB%', 'PF', 'FT', 'FG', 'FT%', 'BLK', 'FTA', 'BPM', 'TOV', 'eFG%', 'STL', 'DRtg', 'TRB', 'BLK%', 'AST', 'PTS', 'ORtg', 'STL%', 'TRB%', '3P', 'FG%', 'USG%', 'FT', 'ORB%', '3PA', 'ORB', '3PAr', 'MP', 'DRB', '+/-', 'TS%', 'AST%', 'FGA']
inf_small = 10 ** -8

class Player():
    def __init__(self, games_stats, player):
        self.player = player
        self.games = []
        for game_stats in games_stats:
            self.player_game_stats(game_stats)
        self.process_skipped_games()
    def get_stats(self, player_stats):
        for stat in basic_player_stats:
            if player_stats.get(stat) == None:
                player_stats[stat] = inf_small
            if player_stats.get(stat) == 0:
                player_stats[stat] = inf_small
        return player_stats
    def player_game_stats(self, game_stats):
        if game_stats['players'].get(self.player) == None: return {}
        player_stats = self.get_stats(game_stats['players'][self.player])
        team_stats = game_stats['team']
        qAST = ((player_stats['MP'] / (team_stats['MP'] / 5)) * (1.14 * ((team_stats['AST'] - player_stats['AST']) / team_stats['FG']))) +\
               ((((team_stats['AST'] / team_stats['MP']) * player_stats['MP'] * 5 - player_stats['AST']) / ((team_stats['FG'] / team_stats['MP']) * player_stats['MP'] * 5 -\
               player_stats['FG'] + .01)) * (1 - (player_stats['MP'] / (team_stats['MP'] / 5))))
        FG_Part = player_stats['FG'] * (1 - 0.5 * ((player_stats['PTS'] - player_stats['FT']) / (2 * player_stats['FGA'])) * qAST)
        AST_Part = 0.5 * (((team_stats['PTS'] - team_stats['FT']) - (player_stats['PTS'] - player_stats['FT'])) / (2 * (team_stats['FG'] - player_stats['FGA'] + inf_small))) * player_stats['AST']
        FT_Part = (1 - (1 - (player_stats['FT'] / player_stats['FTA'])) ** 2) * 0.4 * player_stats['FTA']
        ORB_Part = player_stats['ORB'] * team_stats['Team_ORB_Weight'] * team_stats['Team_Play']
        ScPoss = (FG_Part + AST_Part + FT_Part) * (1 - (team_stats['ORB'] / team_stats['Team_Scoring_Poss']) * team_stats['Team_ORB_Weight'] * team_stats['Team_Play']) + ORB_Part
        FGxPoss = (player_stats['FGA'] - player_stats['FG']) * (1 - 1.07 * team_stats['ORB%'])
        FTxPoss = ((1 - (player_stats['FT'] / player_stats['FTA'])) ** 2) * 0.4 * player_stats['FTA']
        TotalPoss = ScPoss + FGxPoss + FTxPoss + team_stats['TOV']
        PProd_FG_Part = 2 * (player_stats['FG'] + 0.5 * player_stats['3P']) * (1 - 0.5 * ((player_stats['PTS'] - player_stats['FT']) / (2 * player_stats['FGA'])) * qAST)
        PProd_AST_Part = 2 * ((team_stats['FG'] - player_stats['FG'] + 0.5 * (team_stats['3P'] - player_stats['3P'])) / (team_stats['FG'] - player_stats['FG'])) * 0.5 *\
                             (((team_stats['PTS'] - team_stats['FT']) - (player_stats['PTS'] - player_stats['FT'])) / (2 * (team_stats['FGA'] - player_stats['FGA']))) * player_stats['AST']
        PProd_ORB_Part = player_stats['ORB'] * team_stats['Team_ORB_Weight'] * team_stats['Team_Play'] * (team_stats['PTS'] / (team_stats['FG'] + (1 - (1 - (team_stats['FT'] / team_stats['FTA'])) ** 2) * 0.4 * team_stats['FTA']))
        PProd = (PProd_FG_Part + PProd_AST_Part + player_stats['FT']) * (1 - (team_stats['ORB'] / team_stats['Team_Scoring_Poss']) * team_stats['Team_ORB_Weight'] * team_stats['Team_Play']) + PProd_ORB_Part
        ORtg = 100 * (PProd / TotalPoss)
        Floor = ScPoss / TotalPoss
        MarginalOffense = PProd - 0.92 * 1.083 * ScPoss
        MarginalPPW = 0.32 * 100 * (team_stats['Pace'] / 91.7)
        OffWS = MarginalOffense / MarginalPPW
        player_stats['qAST'] = qAST
        player_stats['FG_Part'] = FG_Part
        player_stats['AST_Part'] = AST_Part
        player_stats['FT_Part'] = FT_Part
        player_stats['ORB_Part'] = ORB_Part
        player_stats['ScPoss'] = ScPoss
        player_stats['FGxPoss'] = FGxPoss
        player_stats['TotalPoss'] = TotalPoss
        player_stats['PProd_FG_Part'] = PProd_FG_Part
        player_stats['PProd_AST_Part'] = PProd_AST_Part
        player_stats['PProd_ORB_Part'] = PProd_ORB_Part
        player_stats['PProd'] = PProd
        player_stats['ORtg'] = ORtg
        player_stats['Floor'] = Floor
        player_stats['MarginalOffense'] = MarginalOffense
        player_stats['MarginalPPW'] = MarginalPPW
        player_stats['OffWS'] = OffWS
        self.games.append(player_stats)
        return player_stats
    def process_skipped_games(self):
        len_games = len(self.games)
        last_game_index = 0
        while last_game_index < len_games and self.games[last_game_index]['did_play'] == 0:
            last_game_index += 1
        for game in self.games: del game['did_play']
        self.games_skipped = last_game_index
    def get_mean(self):
        return dict(pd.DataFrame(self.games).mean())