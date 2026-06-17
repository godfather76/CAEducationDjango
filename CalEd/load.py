from pathlib import Path
from django.contrib.gis.utils import LayerMapping
from .models import County, SchoolDistrict

county_mapping = {
    'county': 'NAME',
    'geometry': 'geometry'
}

county_shp = Path(__file__).parent / 'data' / 'CA_Counties.shp'

district_mapping = {
    'county': 'CountyName',
    'district_name': 'DistrictNa',
    'grade_low': 'GradeLow',
    'grade_high': 'GradeHigh',
    'geometry': 'geometry'
}

district_shp = Path(__file__).parent / 'data' / 'DistrictAreas2324.shp'

def run(verbose=True):
    lm = LayerMapping(SchoolDistrict, district_shp, district_mapping, transform=True, source_srs=3857)
    lm.save(strict=True, verbose=verbose)
    lm2 = LayerMapping(County, county_shp, county_mapping, transform=False)
    lm2.save(strict=True, verbose=verbose)
