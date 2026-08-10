from django.urls import path
from . import views

# namespace
app_name = 'GW2Predict'

urlpatterns = [
    path('', views.index, name='index'),
    path('api/predict/', views.predict, name='predict'),
    path('project_about/', views.project_about, name='project_about'),
    path('notebooks/', views.notebooks, name='notebooks'),
]