from django.urls import path
from . import views

# namespace
app_name = 'EyeTartan'

urlpatterns = [
    path('', views.index, name='index'),
]