from bs4 import BeautifulSoup as bs, Comment, Tag
import requests
import pandas as pd
import os
import json
import time

base_site = "https://www.basketball-reference.com"
base_url = lambda day, month, year: f"{base_site}/boxscores/?month={month}&day={day}&year={year}"

def load_page(url):
    time.sleep(3)
    content = requests.get(url).text
    return bs(content, 'lxml')

def load_game(url, date):
    page = load_page(url)
    season = page.select('u')[-1].contents[0][:4]
    datetime = date.strftime('%Y-%m-%d')
    team1 = page.findAll('li', {'class': 'full'})[1].find('a')['href'].split('/')[2]
    team2 = page.findAll('li', {'class': 'full'})[2].find('a')['href'].split('/')[2]
    
    game_path = lambda x='': f'./data/{season}/{datetime + team1 + "-" + team2}/' + x
    
    os.makedirs(game_path(), exist_ok=True)
    
    factors = pd.read_html(str(bs(page.select('#all_four_factors')[0].findAll(text = lambda text:isinstance(text, Comment))[0], 'lxml').select('table')[0]))[0]
    factors.columns = list(map(lambda x: x[1], factors.columns))
    factors = factors.rename({factors.columns[0]: 'Team'}, axis=1)
    factors.to_csv(game_path('factors.csv'))
    
    basic = pd.read_html(str(page.select(f'#box-{team1}-game-basic')))[0]
    advanced = pd.read_html(str(page.select(f'#box-{team1}-game-advanced')))[0]

    basic.columns = list(map(lambda x: x[1], basic.columns))
    advanced.columns = list(map(lambda x: x[1], advanced.columns))
    basic.to_csv(game_path(team1 + '.csv'))
    advanced.to_csv(game_path(team1 + 'Adv.csv'))
    
    basic = pd.read_html(str(page.select(f'#box-{team2}-game-basic')))[0]
    advanced = pd.read_html(str(page.select(f'#box-{team2}-game-advanced')))[0]
    
    basic.columns = list(map(lambda x: x[1], basic.columns))
    advanced.columns = list(map(lambda x: x[1], advanced.columns))
    basic.to_csv(game_path(team2 + '.csv'))
    advanced.to_csv(game_path(team2 + 'Adv.csv'))
    
    inactive = page.find_all(lambda x: 'Inactive' in x.contents[0] if len(x.contents) > 0 else False)[0].parent
    records = list(inactive.children)
    records = list(filter(lambda x: type(x) == Tag, records))
    records = list(filter(lambda x: len(x.contents) > 0, records))
    records = list(map(lambda x: x.contents[0], records))
    records = list(map(lambda x: x.contents[0] if type(x) == Tag else x, records))
    
    inactive1 = records[records.index(team1) + 1:records.index(team2)]
    inactive2 = records[records.index(team2) + 1:]
    inactive = dict()
    inactive[team1] = inactive1
    inactive[team2] = inactive2
    f = open(game_path('inactive.json'), 'w')
    json.dump(inactive, f)
    f.truncate()
    f.close()
    

def load_games(date):
    url = base_url(date.day, date.month, date.year)
    page = load_page(url)
    if page.findAll('strong')[1].contents[0] == 'No games played on this date.':
        return
    gamelinks = page.select('.game_summaries')[0].select('.gamelink')
    gamelinks = list(map(lambda x: x.select('a')[0]['href'], gamelinks))
    for link in gamelinks:
        load_game(base_site + link, date)

def load_dates(period = pd.date_range(start="2022-12-01", end="2023-01-03")):
    total_time = len(period)
    i = 0
    print('Total dates to be loaded:', total_time)
    for date in period:
        load_games(date)
        print(f"Completed {(i+1)}/{total_time}")
        i+=1