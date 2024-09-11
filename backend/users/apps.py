"""Приложение users."""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Класс для создания приложения."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    verbose_name = 'Пользователи'
