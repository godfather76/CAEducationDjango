from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.gis.db.models.functions import Transform, Centroid
from json import loads
from .models import *

def index(request):
    return render(request, 'GaelicScotland/index.html', {})

def constituency_geojson(request):
    # 1. Database-level Spatial Processing:
    # - Transform SRID to 4326 (WGS84) in SQL
    # - Simplify topology (0.001 tolerance reduces vertex count drastically without visual quality loss)
    # - Pre-calculate Centroid in SQL
    scottish_constituencies = Shape.objects.annotate(
        geom_4326=Transform('geometry', 4326),
        centroid_4326=Transform(Centroid('geometry'), 4326)
    )

    # 2. Fetch demographic dictionaries
    gaelic_data = GaelicLanguageScottish.objects.values('constituency_id', 'population_over_3', 'no_gaelic')
    gaelic_map = {item['constituency_id']: item for item in gaelic_data}

    trans_data = TransStatus.objects.values(
        'constituency_id', 'population_over_16', 'no_trans_history', 'yes_trans_history', 'not_answered'
    )
    trans_map = {item['constituency_id']: item for item in trans_data}

    features = []
    for constituency in scottish_constituencies:
        c_id = constituency.constituency_id
        gaelic = gaelic_map.get(c_id, {})
        trans = trans_map.get(c_id, {})

        pop_over_3 = int(gaelic.get('population_over_3', 0))
        no_gaelic = int(gaelic.get('no_gaelic', 0))
        num_some_gaelic = pop_over_3 - no_gaelic

        pop_over_16 = int(trans.get('population_over_16', 0))
        yes_trans = int(trans.get('yes_trans_history', 0))
        not_trans = int(trans.get('no_trans_history', 0))
        not_answered = int(trans.get('not_answered', 0))

        perc_some_gaelic = round((num_some_gaelic / pop_over_3) * 100, 2) if pop_over_3 else 0.0
        perc_no_gaelic = round((no_gaelic / pop_over_3) * 100, 2) if pop_over_3 else 0.0

        perc_trans = round((yes_trans / pop_over_16) * 100, 2) if pop_over_16 else 0.0
        perc_not_trans = round((not_trans / pop_over_16) * 100, 2) if pop_over_16 else 0.0
        perc_not_answered = round((not_answered / pop_over_16) * 100, 2) if pop_over_16 else 0.0

        # Extract pre-computed centroid coords [lng, lat]
        centroid_point = constituency.centroid_4326
        centroid_coords = [centroid_point.x, centroid_point.y] if centroid_point else None

        # Simplify the geometry in Python before sending to the frontend
        # Tolerance of 0.001 degrees (roughly 111 meters) trims excess vertices
        simplified_geom = constituency.geom_4326.simplify(0.001, preserve_topology=True)

        features.append({
            'type': 'Feature',
            'geometry': loads(simplified_geom.geojson),
            'properties': {
                'constituency': constituency.constituency,
                'centroid': centroid_coords,
                'pop_over_3': pop_over_3,
                'perc_no_gaelic': perc_no_gaelic,
                'perc_some_gaelic': perc_some_gaelic,
                'num_no_gaelic': no_gaelic,
                'num_some_gaelic': num_some_gaelic,
                'pop_over_16': pop_over_16,
                'num_trans': yes_trans,
                'perc_trans': perc_trans,
                'perc_not_trans': perc_not_trans,
                'num_not_trans': not_trans,
                'perc_not_answered': perc_not_answered,
                'num_not_answered': not_answered,
            }
        })

    return JsonResponse({'type': 'FeatureCollection', 'features': features})

def notebooks(request):
    return render(request, 'GaelicScotland/notebooks.html', {})