from django.http import JsonResponse
from django.core.cache import cache
from django.shortcuts import render
from django.db.models import Q
from django.apps import apps
from GW2Predict.models import *
from datetime import datetime, timedelta
import pandas as pd
from keras.models import load_model
import joblib



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

    predict_data = (PredictData.objects
                    .filter(item_id=item_id))
    data_lookup = {x.name: x for x in predict_data}
    print(predict_data)
    features = {'buy_open': predict_data['buy_open'],
                'buy_high': predict_data['high'],
                'buy_low': predict_data['low'],
                'buy_close': predict_data['close'],
                'sell_open': predict_data['open'],
                'sell_high': predict_data['high'],
                'sell_low': predict_data['low'],
                'sell_close': predict_data['close'],
                'buy_sma': predict_data['value'],
                'sell_sma': predict_data['value']}

    df = pd.DataFrame(features, index=[0])

    preprocess = joblib.load('GW2Predict/models/preprocess.joblib')
    x = preprocess.transform(df)
    model = load_model('GW2Predict/models/model.keras')
    y_pred = model.predict(x)

    y_preprocess = joblib.load('GW2Predict/models/y_preprocess.joblib')

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