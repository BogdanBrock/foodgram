"""Данные для маршрутизации API."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CustomUserViewSet,
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet
)


router_v1 = DefaultRouter()
router_v1.register('recipes', RecipeViewSet, basename='recipes')
router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')
router_v1.register('users', CustomUserViewSet, basename='users')

urlpatterns = [
    path('', include(router_v1.urls)),
    path('<str:short_url>/', RecipeViewSet.as_view(
        {'get': 'redirect_to_recipe'},
        name='redirect_to_recipe'
    )),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
