"""Фильтрация для API."""

import django_filters

from recipes.models import Ingredient


class CustomFilter(django_filters.FilterSet):
    """Пользовательский класс для настройки фильтрации."""

    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith'
    )

    class Meta:
        """Класс определяет метаданные для фильтрации CustomFilter."""

        model = Ingredient
        fields = ['name']
