from django.urls import path
from . import views

# namespace
app_name = 'GaelicScotland'

urlpatterns = [
    path('', views.index, name='index'),
    path('api/scottish-constituencies/', views.constituency_geojson, name='scottish-constituencies'),
    path('notebooks/', views.notebooks, name='notebooks')

]