from django.contrib.gis import admin
from .models import *

admin.site.register(AggByCountyTA)
admin.site.register(AggByDistrictTA)
admin.site.register(County)
admin.site.register(SchoolDistrict)
admin.site.register(ELAMathTestScore)
admin.site.register(ScienceTestScore)
admin.site.register(StudentGroup)

