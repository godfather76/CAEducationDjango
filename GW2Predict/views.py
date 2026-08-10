from django.http import JsonResponse
from django.core.cache import cache
from django.shortcuts import render
from django.db.models import Q
from django.apps import apps
from GW2Predict.models import *
import requests
from datetime import datetime, timedelta
import pandas as pd
from sklearn.preprocessing import StandardScaler
from keras.models import load_model
import joblib
import urllib.request
import json



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
    context = {'all_items': all_items}

    return render(request, 'GW2Predict/index.html', context)

def predict(request):
    item_name = request.GET.get('item_name')
    item_id = AllItems.objects.get(name=item_name).id
    cache_key = f'gw2_price_{item_id}'
    cached_data = cache.get(cache_key)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    if cached_data:
        data = cached_data
    else:
        url = f"https://www.gw2tp.com/api/trends-ohlc?id={item_id}&range=all&mode=line"
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
        except Exception as e:
            print(f'Socket connection failed: {e}')
            return JsonResponse({'Error retrieving data from gw2tp.com'}, status=500)

    tables = [
        'buy_ohlc',
        'sell_ohlc',
        'sell_sma',
        'buy_sma',
    ]

    features = {'buy_open': data['buy_ohlc'][-1]['open'],
                'buy_high': data['buy_ohlc'][-1]['high'],
                'buy_low': data['buy_ohlc'][-1]['low'],
                'buy_close': data['buy_ohlc'][-1]['close'],
                'sell_open': data['sell_ohlc'][-1]['open'],
                'sell_high': data['sell_ohlc'][-1]['high'],
                'sell_low': data['sell_ohlc'][-1]['low'],
                'sell_close': data['sell_ohlc'][-1]['close'],
                'buy_sma': data['buy_sma'][-1]['value'],
                'sell_sma': data['sell_sma'][-1]['value']}

    df = pd.DataFrame(features, index=[0])

    preprocess = joblib.load('GW2Predict/models/preprocess.joblib')
    x = preprocess.transform(df)
    model = load_model('GW2Predict/models/model.keras')
    y_pred = model.predict(x)

    y_preprocess = joblib.load('GW2Predict/models/y_preprocess.joblib')

    api_cache_key = f'gw2api_price_{item_id}'
    api_cached_data = cache.get(api_cache_key)
    if api_cached_data:
        api_data = api_cached_data
    else:
        api_url = f'https://api.guildwars2.com/v2/commerce/prices/{item_id}'
        api_req = urllib.request.Request(api_url, headers=headers)
        try:
            with urllib.request.urlopen(api_req, timeout=10) as response:
                api_data = json.loads(response.read().decode('utf-8'))
        except Exception as e:
            print(f'Socket connection failed: {e}')
            return JsonResponse({'Error retrieving data from GW2 API'}, status=500)

    for f in features.keys():
        features[f] = determine_denominations(features[f])

    data_datetime = datetime.fromtimestamp(data['buy_ohlc'][-1]['time'])
    features['current_buy_price'] = determine_denominations(api_data['buys']['unit_price'])
    features['data_date'] = data_datetime.strftime('%m-%d-%Y')
    features['3_day_date'] = (data_datetime + timedelta(days=3)).strftime('%m-%d-%Y')
    features['7_day_date'] = (data_datetime + timedelta(days=7)).strftime('%m-%d-%Y')
    features['30_day_date'] = (data_datetime + timedelta(days=30)).strftime('%m-%d-%Y')
    features['item_id'] = item_id
    features['item_name'] = item_name
    decoded = y_preprocess.inverse_transform(y_pred)
    features['3d'] = determine_denominations(int(decoded[0, 0]))
    features['7d'] = determine_denominations(int(decoded[0, 1]))
    features['30d'] = determine_denominations(int(decoded[0, 2]))

    return JsonResponse({'type': 'FeatureCollection', 'features': features})

def project_about(request):
    return render(request, 'GW2Predict/project_about.html')

def notebooks(request):
    return(render, 'GW2Predict/notebooks.html')