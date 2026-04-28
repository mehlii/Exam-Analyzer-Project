# analysis/urls.py
# Türkçe not: /analysis/ altındaki URL'ler.

from django.urls import path

from . import views

app_name = "analysis"

urlpatterns = [
    path("history/", views.history, name="history"),
    path("<int:pk>/", views.detail, name="detail"),
]

