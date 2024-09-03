from django.contrib import admin

from .models import Recipe, Tag, Ingredient, TagRecipe, IngredientRecipe, Favorite, ShoppingCart


class RecipeAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'text',
        'image',
        'is_favorited',
        'is_in_shopping_cart',
        'cooking_time',
        'author'
    ]
    list_editable = [
        'text',
        'image',
        'is_favorited',
        'is_in_shopping_cart',
        'cooking_time',
        'author'
    ]
    search_fields = ['name']
    list_filter = ['author']
    filter_horizontal = [
        'tags',
        'ingredients'
    ]


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(TagRecipe)
admin.site.register(IngredientRecipe)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)
