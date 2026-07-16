from django.urls import path
from . import views

# namespace
app_name = 'CalEd'

urlpatterns = [
    path('', views.index, name='index'),
    path('index/', views.index, name='index'),
    path('api/districts/', views.district_geo_json, name='district_data'),
    path('api/counties/', views.county_geo_json, name='county_data'),
    path('project_about/', views.project_about, name='project_about'),
    path('notebooks/', views.notebooks, name='notebooks'),
    path('notebooks/SepIntoYears/', views.SepIntoYears, name='SepIntoYears'),
    path('notebooks/TransparentCADataCombiner/', views.TransparentCADataCombiner, name='TransparentCADataCombiner'),
    path('notebooks/WebScraperApp/', views.WebScraperApp, name='WebScraperApp'),
    path('notebooks/SalaryAggregate/', views.SalaryAggregate, name='SalaryAggregate'),
    path('notebooks/ToPostgreSQL/', views.ToPostgreSQL, name='ToPostgreSQL'),

    path('links/', views.links, name='links'),
]
