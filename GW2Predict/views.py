from multiprocessing.dummy import current_process

from django.http import JsonResponse
from django.shortcuts import render
from django.db.models import Q
from django.apps import apps
from GW2Predict.models import *
from datetime import datetime, timedelta
import pandas as pd
from keras.models import load_model
import joblib
import requests
from bs4 import BeautifulSoup
import numpy as np


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

    model = apps.get_app_config('GW2Predict').model
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

    # We'll decide based on month which festival to check for

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


def gather_and_preprocess_k20(item_id):
    # Get item data from AllItems model
    item_data = AllItems.objects.get(pk=item_id)
    # get today's date
    now = datetime.now()
    # Get Festival data from Wiki
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
    if festivals_dict:
        possible_festivals = festivals_dict.keys()

def gather_and_preprocess_k15(item_id):
    item_data = AllItems.objects.get(pk=item_id)
    # Get current buy and sell price, supply, and demand from the API
    prices_url = f'https://api.guildwars2.com/v2/commerce/prices/{item_id}'
    # Get json of the price data from the Guild Wars 2 API via requests
    res = requests.get(url=prices_url).json()
    # Create a dictionary with the data we need from the API and AllItems model
    res_dict = {'id': item_id,
                'current_buy_price': res['buys']['unit_price'],
                'current_sell_price': res['sells']['unit_price'],
                'supply_demand_ratio': res['sells']['quantity'] / (res['buys']['quantity'] + 1),
                'type': item_data.type,
                'vendor_value': item_data.vendor_value,
                'rarity': item_data.rarity,
                'level': item_data.level}

    # Check for NoSell in flags (it was the only flag that survived KBest mutual_info_regression
    if 'NoSell' in item_data.flags:
        res_dict['NoSell'] = 1
    else:
        res_dict['NoSell'] = 0
    # Check for Activity in game_types (it was the only game type that survived KBest with mutual_info_regression
    if 'Activity' in item_data.game_types:
        res_dict['Activity'] = 1
    else:
        res_dict['Activity'] = 0

    # Make a dataframe we can pass into our preprocessing.
    df = pd.DataFrame([res_dict], index=[0])
    x_dict = {}
    for d in ['3', '7', '30']:
        preprocess = joblib.load(f'GW2Predict/models/preprocess_{d}d.joblib')
        x_dict[f'{d}'] = preprocess.transform(df)
        x_dict[f'{d}'] = x_dict[f'{d}'].drop(columns='passthrough__id')

    return x_dict, res_dict



def predict(request):
    item_name = request.GET.get('item_name')
    item_id = AllItems.objects.get(name=item_name).id

    x_dict, res_dict = gather_and_preprocess_k15(item_id)
    input_id = np.array([item_id])

    predictions = {}
    for d, x in x_dict.items():
        model = load_model(f'GW2Predict/models/model_{d}d.keras')
        y_pred_scaled = model.predict([input_id, x])
        y_preprocess = joblib.load(f'GW2Predict/models/y_preprocess_{d}d.joblib')
        y_pred_actual = y_preprocess.inverse_transform(y_pred_scaled)
        predictions[f'{d}d'] = determine_denominations(y_pred_actual[0][0])

    # Get today's date:
    date = datetime.today()
    features = {'item_name': item_name,
                'item_id': item_id,
                'current_buy_price': determine_denominations(res_dict['current_buy_price']),
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
    return(render, 'GW2Predict/notebooks.html')