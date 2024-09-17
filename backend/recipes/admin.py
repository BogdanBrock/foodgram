"""Админ-зона для API."""

from django.contrib import admin

from .models import (
    Favorite, Ingredient, IngredientRecipe,
    Recipe, ShoppingCart, Tag, TagRecipe
)


class RecipeAdmin(admin.ModelAdmin):
    """Класс для управление админ-зоной."""

    list_display = [
        'name',
        'author',
        'favorites_count_display'
    ]
    search_fields = [
        'name',
        'author'
    ]
    list_filter = ['tags']

    def favorites_count_display(self, obj):
        """Функция для отображения количества рецептов в избранном."""
        return obj.user_favorite.count()

    favorites_count_display.short_description = 'Добавлений в избранное'


class IngredientAdmin(admin.ModelAdmin):
    """Класс для управление админ-зоной."""

    list_display = ['name', 'measurement_unit']
    search_fields = ['name']


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag)
admin.site.register(TagRecipe)
admin.site.register(IngredientRecipe)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)
