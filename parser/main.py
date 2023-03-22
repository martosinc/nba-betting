import pandas as pd
import loader
import indexation
import formatting
import create_dataset

action = int(input('Load dates(1) or create dataset(2) or both(12):'))
if action == 1 or action == 12:
    start = pd.Timestamp(input('Start date:'))
    end = pd.Timestamp(input('End date:'))
    period = pd.date_range(start, end)
    loader.load_dates(period)
    indexation.index_seasons(period)
    formatting.format_seasons(period)
if action == 2 or action == 12:
    create_dataset.create_dataset()