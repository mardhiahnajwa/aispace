"""
URL configuration for aispace project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('rag/', include('agentic_rag.urls')),
    path('google-agent/', include('google_agent.urls')),
    path('langchain_agent/', include('langchain_agent.urls')),
]