# analysis/urls.py
# Türkçe not: /analysis/ altındaki URL'ler.
from django.urls import path

from . import views

app_name = "analysis"

urlpatterns = [
    path("", views.home_view, name="home"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("upload/", views.upload_view, name="upload"),
    path("history/", views.history_view, name="history"),
    path("<int:pk>/", views.detail_view, name="detail"),
]
