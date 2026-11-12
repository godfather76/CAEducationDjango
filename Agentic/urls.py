from django.urls import path
from . import views

# namespace
app_name = 'Agentic'

urlpatterns = [
    path('', views.index, name='index'),
    path('index/', views.index, name='index'),
    path('chat/', views.chat_with_character, name='chat'),
]