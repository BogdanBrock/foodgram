"""Представления для работы с моделями приложения API."""

import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from django.http import FileResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import permissions, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from .pagination import CustomPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    AvatarSerializer,
    UserSerializer,
    FavoriteSerializer,
    FollowSerializer,
    IngredientSerializer,
    RecipeSerializer,
    RecipeGetSerializer,
    ShoppingCartSerializer,
    TagSerializer,
    UserWithRecipesSerializer
)
from recipes.models import (
    Favorite, Ingredient, IngredientRecipe,
    Recipe, ShoppingCart, Tag
)
from users.models import Follow


User = get_user_model()


class RecipeViewSet(viewsets.ModelViewSet):
    """Класс для обработки данных."""

    queryset = Recipe.objects.all()
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnly,
    )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = CustomPagination
    file_path = None

    def get_serializer_class(self):
        """Функция для изменения сериализатора."""
        if self.action == 'list' or self.action == 'retrieve':
            return RecipeGetSerializer
        return RecipeSerializer

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request):
        """Функция для того, чтобы скачать список ингредиентов."""
        user = request.user
        ingredients = IngredientRecipe.objects.filter(
            recipe__user_cart__user=user
        ).values(
            'ingredient_id'
        ).annotate(
            amount=Sum('amount')
        ).values_list(
            'ingredient__name',
            'ingredient__measurement_unit',
            'amount'
        )
        str_data = ''
        for name, measurement_unit, amount in ingredients:
            ingredient = (f'{name} ({measurement_unit}) - {amount}\n')
            str_data += ingredient
        self.save_download_shopping_cart(str_data)
        return FileResponse(open(self.file_path, 'rb'))

    @staticmethod
    def save_download_shopping_cart(str_data):
        """Функция для хранения покупок в файле."""
        folder_path = os.path.join(settings.BASE_DIR, 'download_shopping_cart')
        os.makedirs(folder_path, exist_ok=True)
        existing_files = os.listdir(folder_path)
        if not existing_files:
            number = '0'
        else:
            number = max(
                [f.split('_')[2].split('.')[0] for f in existing_files]
            )
        RecipeViewSet.file_path = os.path.join(
            folder_path, f'shopping_cart_{str(int(number) + 1)}.txt'
        )
        with open(RecipeViewSet.file_path, 'w', encoding='utf-8') as f:
            f.write(str_data)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        """Функция для добавление рецепта в корзину."""
        recipe = self.get_object()
        data = {
            'user': request.user.id,
            'recipe': recipe.id
        }
        serializer = ShoppingCartSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        """Функция для удаления рецепта из корзины."""
        recipe = self.get_object()
        delete_cnt, _ = ShoppingCart.objects.filter(
            user=request.user,
            recipe=recipe
        ).delete()
        if not delete_cnt:
            raise serializers.ValidationError(
                'Попытка удалить рецепт, которого нет в корзине'
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        """Функция для добавления рецепта в избранное."""
        recipe = self.get_object()
        data = {
            'user': request.user.id,
            'recipe': recipe.id
        }
        serializer = FavoriteSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        """Функция для удаления рецепта из избранного."""
        recipe = self.get_object()
        delete_cnt, _ = Favorite.objects.filter(
            user=request.user.id,
            recipe=recipe
        ).delete()
        if not delete_cnt:
            raise serializers.ValidationError(
                'Попытка удалить рецепт, которого нет в корзине'
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['get'],
        url_path='get-link',
    )
    def get_link(self, request, pk=None):
        """Функция для получения короткой ссылки."""
        instance = self.get_object()
        short_url = request.build_absolute_uri(f'/api/{instance.short_url}')
        data = {'short-link': short_url}
        return Response(data)

    @staticmethod
    def redirect_to_recipe(request, short_url):
        """Функция для перехода к рецепту по короткой ссылке."""
        instance = get_object_or_404(Recipe, short_url=short_url)
        url = request.build_absolute_uri().split('/api')[0]
        short_url = url + f'/recipes/{instance.id}/'
        return HttpResponseRedirect(short_url)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление для обработки данных."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление для обработки данных."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class CustomUserViewSet(UserViewSet):
    """Представление для обработки данных."""

    serializer_class = UserSerializer
    pagination_class = CustomPagination

    @action(
        detail=False,
        methods=['get'],
        serializer_class=UserWithRecipesSerializer
    )
    def subscriptions(self, request):
        """Функция для отображения подписчиков."""
        queryset = User.objects.filter(followers__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def subscribe(self, request, id=None):
        """Функция для подписки на пользователя."""
        following = self.get_object()
        data = {
            'user': request.user.id,
            'following': following.id
        }
        serializer = FollowSerializer(
            data=data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id=None):
        """Функция для отписки на пользователя."""
        following = self.get_object()
        delete_cnt, _ = Follow.objects.filter(
            user=request.user,
            following=following
        ).delete()
        if not delete_cnt:
            raise serializers.ValidationError(
                'Вы пытаетесь удалить несуществующую подписку'
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['put'],
        url_path='me/avatar',
        permission_classes=[permissions.IsAuthenticated]
    )
    def avatar(self, request, pk=None):
        """Функция для изменения аватара."""
        user = User.objects.get(username=request.user.username)
        serializer = AvatarSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @avatar.mapping.delete
    def delete_avatar(self, request, pk=None):
        """Функция для удаления аватара."""
        user = User.objects.get(username=request.user.username)
        user.avatar = None
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        ['get'],
        detail=False,
        permission_classes=[permissions.IsAuthenticated]
    )
    def me(self, request, *args, **kwargs):
        """Функция для отображения страницы текущего пользователя."""
        return super().me(request, *args, **kwargs)
