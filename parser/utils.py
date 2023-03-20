import json

def lower_bound(array, element):
    left = 0
    right = len(array) - 1
    while (right - left > 1):
        middle = (left + right) // 2
        if array[middle] > element: right = middle
        else: left = middle
    return right

def get_season(timestamp):
    if timestamp.month < 7:
        return timestamp.year
    return timestamp.year + 1

def get_seasons(period):
    return range(get_season(period[0]), get_season(period[-1]) + 1)

def write_data(path, data):
    f = open(path, 'w')
    json.dump(data, f)
    f.truncate()
    f.close()