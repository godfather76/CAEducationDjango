from multiprocessing.dummy import current_process

from django.http import JsonResponse
from django.shortcuts import render
from django.db.models import Q
from .apps import GW2PredictConfig
from GW2Predict.models import *
from datetime import datetime, timedelta
import pandas as pd
import joblib
import requests
from bs4 import BeautifulSoup
import numpy as np
from math import pi


def determine_denominations(copper):
    if copper < 100:
        c = int(copper)
        return f'{c}c'
    elif copper < 10000:
        s = int(copper // 100)
        c = int(copper - (s * 100))
        return f'{s}s {c}c'
    else:
        g = int(copper // 10000)
        s = int((copper - (g * 10000)) // 100)
        c = int(copper - (g * 10000) - (s * 100))
        return f'{g}g {s}s {c}c'


def index(request):
    all_items = (
        AllItems.objects
        .values_list('name', flat=True)
        .filter(
            (Q(type='CraftingMaterial') |
            Q(type='Trophy')) &
            (~Q(flags__contains='AccountBound') &
            ~Q(flags__contains='SoulbindOnAcquire'))
        )).order_by('name')

    context = {'all_items': all_items,
               'available_models': ['3 Days', '7 Days', '30 Days']}

    return render(request, 'GW2Predict/index.html', context)


# The main feature we need to build is to keep track of the festivals in Guild Wars 2
# This is likely to be by far both the most important feature and the most prone to failure (since it will have
# to be updated manually)
def get_soup(url):
    # Request the HTML from the page
    page = requests.get(url)
    # Turn it into soup and return the soup
    return BeautifulSoup(page.content, 'html.parser')
# get_current_data()

def make_datetimes(soup):
    dates = [x.get_text().replace('(', '').replace(')', '')
                 for x in soup.find_all('small') if '—' in x.get_text()]
    dates = [(x.split('—')[0].strip(), x.split('—')[1].strip()) for x in dates]
    try:
        return [(int(datetime.strptime(x[0], '%Y-%m-%d').timestamp()),
                 int(datetime.strptime(x[1], '%Y-%m-%d').timestamp()))
                for x in dates][-1]
    except ValueError:
        new_list = []
        for x in dates:
            try:
                this_tuple = (int(datetime.strptime(x[0], '%Y-%m-%d').timestamp()),
                              int(datetime.strptime(x[1], '%Y-%m-%d').timestamp()),)
                new_list.append(this_tuple)
            except ValueError:
                continue
        return new_list[-1]

def get_festivals(month):
    lunar_new_year_url = 'https://wiki.guildwars2.com/wiki/Lunar_New_Year'
    super_adv_fest_url = 'https://wiki.guildwars2.com/wiki/Super_Adventure_Festival'
    dragon_bash_fest_url = 'https://wiki.guildwars2.com/wiki/Dragon_Bash'
    fest_four_wind_url = 'https://wiki.guildwars2.com/wiki/Festival_of_the_Four_Winds'
    halloween_url = 'https://wiki.guildwars2.com/wiki/Halloween'
    wintersday_url = 'https://wiki.guildwars2.com/wiki/Wintersday'

    # We'll decide based on month which festival(s) to check for

    if month in range(1, 3) or month == 12:
        lunar_new_year_soup = get_soup(lunar_new_year_url)
        lny_datetimes = make_datetimes(lunar_new_year_soup)
        wintersday_soup = get_soup(wintersday_url)
        w_datetimes = make_datetimes(wintersday_soup)
        return {'lunar_new_year': lny_datetimes,
                'wintersday': w_datetimes}
    elif month in range(4, 6):
        super_adv_fest_soup = get_soup(super_adv_fest_url)
        saf_datetimes = make_datetimes(super_adv_fest_soup)
        return {'super_adventure_festival': saf_datetimes}
    elif month in range(6,7):
        dragon_bash_fest_soup = get_soup(dragon_bash_fest_url)
        dbf_datetimes = make_datetimes(dragon_bash_fest_soup)
        return {'dragon_bash': dbf_datetimes}
    elif month in range(7, 9):
        fest_four_wind_soup = get_soup(fest_four_wind_url)
        ffw_datetimes = make_datetimes(fest_four_wind_soup)
        return {'festival_of_the_four_winds': ffw_datetimes}
    elif month in range(10, 12):
        halloween_soup = get_soup(halloween_url)
        h_datetimes = make_datetimes(halloween_soup)
        return {'halloween': h_datetimes}
    return None


def gather_and_preprocess(item_id):
    item_data = AllItems.objects.get(pk=item_id)
    # get today's date
    now = datetime.now()
    # Get Festival data from Wiki
    festivals = ('lunar_new_year', 'super_adventure_festival',
                 'dragon_bash', 'festival_of_the_four_winds',
                 'halloween', 'wintersday')
    try:
        festivals_dict = get_festivals(month=now.month)
    except:
        # If getting the festival dates fails, we grab this hardcoded list.
        festivals_dict = {'lunar_new_year': (1770076800, 1771891200),
                          'super_adventure_festival': (1776124800, 1777939200),
                          'dragon_bash': (1780358400, 1782172800),
                          'festival_of_the_four_winds': (1786406400, 1788220800),
                          'halloween': (1759795200, 1762214400),
                          'wintersday': (1765238400, 1767657600)}

    # Get current buy and sell price, supply, and demand from the API
    prices_url = f'https://api.guildwars2.com/v2/commerce/prices/{item_id}'
    # Get json of the price data from the Guild Wars 2 API via requests
    res = requests.get(url=prices_url).json()
    # Create a dictionary with the data we need from the API and AllItems model
    # STILL NEED:
    # SIN and COS of day of (week, month, year)
    # Festival
    res_dict = {'id': item_id,
                'current_buy_price': res['buys']['unit_price'],
                'current_sell_price': res['sells']['unit_price'],
                'supply_demand_ratio': res['sells']['quantity'] / (res['buys']['quantity'] + 1),
                'type': item_data.type,
                'vendor_value': item_data.vendor_value,
                'rarity': item_data.rarity,
                'level': item_data.level}

    # Check flags
    flags = ('NoSell', 'NoSalvage', 'Unique', 'NoMysticForge', 'DeleteWarning', 'NotUpgradeable')
    for f in flags:
        if f in item_data.flags:
            res_dict[f] = 1
        else:
            res_dict[f] = 0

    # Check game_types
    types = ('PvpLobby', 'Activity', 'Wvw', 'Dungeon', 'Pve')
    for t in types:
        if t in item_data.game_types:
            res_dict[t] = 1
        else:
            res_dict[t] = 0

    for festival in festivals:
        if festival not in festivals_dict.keys():
            res_dict[festival] = 0
            res_dict[f'{festival}_last_week'] = 0
            res_dict[f'{festival}_next_week'] = 0

    for festival, date_tuple in festivals_dict.items():
        if date_tuple[0] <= now.timestamp() <= date_tuple[1]:
            res_dict[festival] = 1
        else:
            res_dict[festival] = 0

        if date_tuple[0] <= (now - timedelta(7)).timestamp() <= date_tuple[1]:
            res_dict[f'{festival}_last_week'] = 1
        else:
            res_dict[f'{festival}_last_week'] = 0

        if date_tuple[0] <= (now + timedelta(7)).timestamp() <= date_tuple[1]:
            res_dict[f'{festival}_next_week'] = 1
        else:
            res_dict[f'{festival}_next_week'] = 0

    day_of_year = int(now.strftime('%j'))
    day_of_month = now.day
    # Handle year rollover if current month is December
    if now.month == 12:
        month_end = datetime(now.year, 12, 31).day
    else:
        month_end = (datetime(now.year, now.month + 1, 1) - timedelta(days=1)).day
    day_of_week = now.weekday()

    res_dict['sin_day_of_year'] = np.sin(2 * pi * day_of_year / 365)
    res_dict['sin_day_of_month'] = np.sin(2 * pi * day_of_month / month_end)
    res_dict['sin_day_of_week'] = np.sin(2 * pi * day_of_week / 7)

    res_dict['cos_day_of_year'] = np.cos(2 * pi * day_of_year / 365)
    res_dict['cos_day_of_month'] = np.cos(2 * pi * day_of_month / month_end)
    res_dict['cos_day_of_week'] = np.cos(2 * pi * day_of_week / 7)

    # Make a dataframe we can pass into our preprocessing.
    df = pd.DataFrame([res_dict], index=[0])
    x_dict = {}
    if res_dict['current_buy_price'] >= 10000:
        model_branch = 'luxury'
    else:
        model_branch = 'penny'
    for d in ['3', '7', '30']:
        preprocess = GW2PredictConfig.model_dict[f'{model_branch}_{d}d']['preprocess']
        x_dict[f'{d}'] = preprocess.transform(df)
        x_dict[f'{d}'] = x_dict[f'{d}'].drop(columns='passthrough__id')

    return x_dict, res_dict, model_branch



def predict(request):
    item_name = request.GET.get('item_name')
    try:
        item_id = (
            AllItems.objects
            .filter(
                (Q(type='CraftingMaterial') |
                 Q(type='Trophy')) &
                (~Q(flags__contains='AccountBound') &
                 ~Q(flags__contains='SoulbindOnAcquire'))
            )).get(name=item_name).id
    except AllItems.MultipleObjectsReturned:
        # IF there's more than one, just take the first one.
        item_id = (
            AllItems.objects
            .filter(
                (Q(type='CraftingMaterial') |
                 Q(type='Trophy')) &
                (~Q(flags__contains='AccountBound') &
                 ~Q(flags__contains='SoulbindOnAcquire'))
            )).all()[0].id

    x_dict, res_dict, model_branch = gather_and_preprocess(item_id)
    input_id = np.array([item_id])

    predictions = {}
    for d, x in x_dict.items():
        model = GW2PredictConfig.model_dict[f'{model_branch}_{d}d']['model']
        y_pred_scaled = model([input_id, x], training=False)
        y_preprocess = GW2PredictConfig.model_dict[f'{model_branch}_{d}d']['y_preprocess']
        y_pred_actual = y_preprocess.inverse_transform(y_pred_scaled)
        predictions[f'{d}d'] = determine_denominations(y_pred_actual[0][0])

    # Get today's date:
    date = datetime.today()
    features = {'item_name': item_name,
                'item_id': item_id,
                'current_buy_price': determine_denominations(res_dict['current_buy_price']),
                'model_branch': model_branch,
                'current_sell_price': determine_denominations(res_dict['current_sell_price']),
                '3d_date': (date + timedelta(days=3)).strftime('%m-%d-%Y'),
                '3d': predictions['3d'],
                '7d_date': (date + timedelta(days=7)).strftime('%m-%d-%Y'),
                '7d': predictions['7d'],
                '30d_date': (date + timedelta(days=30)).strftime('%m-%d-%Y'),
                '30d': predictions['30d']}

    return JsonResponse({'type': 'FeatureCollection', 'features': features})

def project_about(request):
    return render(request, 'GW2Predict/project_about.html')

def notebooks(request):
    return render(request, 'GW2Predict/notebooks.html')

def EDA(request):
    return render(request, 'GW2Predict/notebooks/EDA.html')

def ParquetCombine(request):
    return render(request, 'GW2Predict/notebooks/ParquetCombine.html')

def Preprocessing(request):
    return render(request, 'GW2Predict/notebooks/Preprocessing.html')

def Model3d(request):
    return render(request, 'GW2Predict/notebooks/Model3d.html')

def Model7d(request):
    return render(request, 'GW2Predict/notebooks/Model7d.html')

def Model30d(request):
    return render(request, 'GW2Predict/notebooks/Model30d.html')
