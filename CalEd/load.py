from pathlib import Path
from django.contrib.gis.utils import LayerMapping
from .models import County, SchoolDistrict

county_mapping = {
    'county': 'NAME',
    'geometry': 'geometry'
}

county_shp = Path(__file__).parent / 'data' / 'CA_Counties.shp'

district_mapping = {
    'geoid': 'geoid',
    'county': 'county',
    'district': 'district',
    'year': 'year',
    'grade_low': 'grade_low',
    'grade_high': 'grade_high',
    'geometry': 'geometry'
}

schoolyears = ['2018-19', '2020-21', '2021-22', '2022-23', '2023-24']
base_dir = Path('/media/ike/Data Science/Datasets/Public Schools Exploration/Data')

def run(verbose=True):
    for schoolyear in schoolyears:
        district_shp = base_dir / schoolyear / 'DistrictAreas' / f'CADistrictAreas{schoolyear}.shp'
        lm = LayerMapping(SchoolDistrict, district_shp, district_mapping, transform=False)
        lm.save(strict=True, verbose=verbose)
    # lm2 = LayerMapping(County, county_shp, county_mapping, transform=True, source_srs=3857)
    # lm2.save(strict=True, verbose=verbose)
