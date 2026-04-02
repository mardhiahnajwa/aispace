"""Google Agent URLs."""
from django.urls import path
from . import views

app_name = 'google_agent'

urlpatterns = [
    path('chat/', views.chat, name='chat'),
    path('reset/', views.reset_chat, name='reset_chat'),
]
