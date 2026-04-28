# accounts/apps.py
# Türkçe not: accounts uygulama konfigürasyonu.

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"

