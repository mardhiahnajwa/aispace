from django.urls import path
from . import views

app_name = 'agentic_rag'

urlpatterns = [
    path('chat/', views.chat, name='chat'),
    path('history/', views.history, name='history'),
    path('health/', views.health, name='health'),
]
