"""Приложение api."""

from django.apps import AppConfig


class ApiConfig(AppConfig):
    """Класс для создания приложения."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
