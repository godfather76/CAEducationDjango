from django.urls import path
from . import views

# namespace
app_name = 'Frontman'

urlpatterns = [
    path('', views.index, name='index'),
    path('about', views.about, name='about'),
]