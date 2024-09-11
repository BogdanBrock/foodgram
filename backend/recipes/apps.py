"""Приложение recipes."""

from django.apps import AppConfig


class RecipesConfig(AppConfig):
    """Класс для создания приложения."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recipes'
    verbose_name = 'Каталог рецептов'
