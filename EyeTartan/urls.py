from django.urls import path
from . import views

# namespace
app_name = 'EyeTartan'

urlpatterns = [
    path('', views.index, name='index'),
    # path('notebooks/', views.notebooks, name='notebooks'),
    path('notebooks/TartanExplore/', views.tartan_explore, name='TartanExplore'),
    path('notebooks/TartanExploreDataImageGen/', views.tartan_explore_image_gen, name='TartanExploreDataImageGen'),
]