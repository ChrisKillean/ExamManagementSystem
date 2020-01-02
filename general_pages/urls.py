from django.urls import path
from django.contrib import admin

from .views import Homepage


app_name = "general_pages"

urlpatterns = [
    path('', Homepage.as_view(), name='home')
]