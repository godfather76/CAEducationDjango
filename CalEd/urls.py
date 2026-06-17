from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('index/', views.index, name='index'),
    path('api/districts/', views.district_geo_json, name='district_data'),
    path('api/counties/', views.county_geo_json, name='county_data'),
]
