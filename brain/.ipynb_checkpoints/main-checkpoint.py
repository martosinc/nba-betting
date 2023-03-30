import pandas as pd
import 
load_additional_dates = input('Enter additional dates to be loaded(y/n)?:').lower() == 'y'
if load_additional_dates:
    start = pd.Timestamp(input('Start:'))
    end = pd.Timestamp(input('End:'))
    