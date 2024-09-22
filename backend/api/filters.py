"""Фильтрация для API."""

import django_filters

from recipes.models import Ingredient, Recipe
from users.models import CreateUser


class IngredientFilter(django_filters.FilterSet):
    """Пользовательский класс для настройки фильтрации IngredientFilter."""

    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith'
    )

    class Meta:
        """Класс определяет метаданные для фильтрации IngredientFilter."""

        model = Ingredient
        fields = ('name',)


class RecipeFilter(django_filters.FilterSet):
    """Пользовательский класс для настройки фильтрации RecipeFilter."""

    tags = django_filters.AllValuesMultipleFilter(
        field_name='tags__slug',
    )
    author = django_filters.ModelChoiceFilter(
        queryset=CreateUser.objects.all()
    )
    is_favorited = django_filters.NumberFilter(
        method='filter_is_favorited',
        label='Избранное'
    )
    is_in_shopping_cart = django_filters.NumberFilter(
        method='filter_is_in_shopping_cart',
        label='В корзине покупок'
    )

    def filter_is_favorited(self, queryset, name, value):
        """Функция для определения пользовательского поля."""
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(user_favorite__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Функция для определения пользовательского поля."""
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(user_cart__user=self.request.user)
        return queryset

    class Meta:
        """Класс определяет метаданные для фильтрации RecipeFilter."""

        model = Recipe
        fields = ('tags', 'author')
