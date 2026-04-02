from django.urls import path
from . import views

urlpatterns = [
    path('table-matching/', views.table_matching),
]