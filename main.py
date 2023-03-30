import pandas as pd
import parser.loader as loader
import parser.indexation as indexation
import parser.formatting as formatter
from parser.utils import get_season
load_additional_dates = input('Load additional dates(y/n)?:').lower() == 'y'
if load_additional_dates:
    start = pd.Timestamp(input('Start:'))
    end = pd.Timestamp(input('End:'))
    period = pd.date_range(start, end)
    # loader.load_dates(period)
    indexation.index_seasons(period)
    formatter.format_seasons(period)
    
import joblib
import parser.create_dataset as processor
import model.strategy as strategy

model = joblib.load('model/model.pkl')

stake = int(input('Enter stake:'))
    
while (date := input('Enter game date:')) != '0':
       home = input('Enter home team:')
       visitor = input('Enter visitor team:')
       game = date + visitor + '-' + home
       season = str(get_season(pd.Timestamp(date)))
       record = pd.Series(dict(zip(processor.get_columns(), processor.create_game_record(season, game, True))))
       record = record.drop(['Home', 'Visitor', 'Winner'])
       prediction = model.predict_proba(record)
       print('Model prediction:', prediction)
       print('Enter bookmaker coefficents:')
       bookmaker = [1 / float(input(home + ':')), 1 / float(input(visitor + ':'))]
       bet = strategy.bet(stake, prediction, bookmaker)
       print(f'Bet on {home}:', bet[0])
       print(f'Bet on {visitor}:', bet[1])