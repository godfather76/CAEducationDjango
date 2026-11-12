from django.urls import path
from . import views

# namespace
app_name = 'GW2Predict'

urlpatterns = [
    path('', views.index, name='index'),
    path('api/predict/', views.predict, name='predict'),
    path('project_about/', views.project_about, name='project_about'),
    path('notebooks/', views.notebooks, name='notebooks'),
    path('notebooks/EDA/', views.EDA, name='EDA'),
    path('notebooks/ParquetCombine/', views.ParquetCombine, name='ParquetCombine'),
    path('notebooks/Preprocessing/', views.Preprocessing, name='Preprocessing'),
    path('notebooks/Model3d/', views.Model3d, name='Model3d'),
    path('notebooks/Model7d/', views.Model7d, name='Model7d'),
    path('notebooks/Model30d/', views.Model30d, name='Model30d')

]