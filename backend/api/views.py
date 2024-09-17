"""Представления для работы с моделями приложения API."""

import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import permissions, serializers, status, viewsets
from rest_framework.reverse import reverse
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import CustomFilter
from .pagination import CustomPagination
from .permissions import AuthorOrReadOnly
from .serializers import (
    RecipeSerializer,
    TagSerializer,
    IngredientSerializer,
    CustomUserSerializer,
    RecipeMinifiedSerializer,
    AvatarSerializer,
    UserWithRecipesSerializer,
    IngredientInRecipeSerializer
)
from recipes.models import (
    Favorite, Ingredient, IngredientRecipe,
    Recipe, ShoppingCart, Tag
)
from users.models import Follow


User = get_user_model()


class RecipeViewSet(viewsets.ModelViewSet):
    """Класс для обработки данных."""

    serializer_class = RecipeSerializer
    permission_classes = [AuthorOrReadOnly]
    filter_backend = [DjangoFilterBackend]
    pagination_class = CustomPagination

    def perform_create(self, serializer):
        """Функция для изменения автора."""
        serializer.save(author=self.request.user)

    def get_object(self):
        """Функция для получения отдельного объекта."""
        obj = get_object_or_404(Recipe, pk=self.kwargs['pk'])
        self.check_object_permissions(self.request, obj)
        return obj

    def get_queryset(self):
        """Функция для получения списка объектов."""
        queryset = Recipe.objects.all().order_by('-created_at')
        current_user = self.request.user
        if not current_user.is_authenticated:
            return queryset
        tags = self.request.GET.getlist('tags')
        query_params = self.request.query_params
        is_in_shopping_cart = query_params.get(
            'is_in_shopping_cart'
        )
        is_favorited = query_params.get(
            'is_favorited'
        )
        author = query_params.get('author')
        if tags:
            queryset = queryset.prefetch_related('tags').filter(
                tags__slug__in=tags
            ).distinct()
        if author == 'me':
            queryset = queryset.filter(author=current_user)
        elif author is not None:
            queryset = queryset.filter(author=author)
        if is_favorited == '1':
            queryset = queryset.filter(user_favorite__user=current_user)
        if is_in_shopping_cart == '1':
            return Recipe.objects.filter(user_cart__user=current_user)
        return queryset

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        """
        Функция для добавление в корзину рецепта
        и удаления из корзины рецепта.
        """
        recipe = self.get_object()
        if request.method == 'POST':
            try:
                get_object_or_404(
                    ShoppingCart,
                    user=request.user,
                    recipe=recipe
                )
            except Http404:
                ShoppingCart.objects.create(
                    user=request.user,
                    recipe=recipe
                )
            else:
                raise serializers.ValidationError(
                    'Нельзя добавить в корзину один и тот же рецепт'
                )
            serializer = RecipeMinifiedSerializer(recipe)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        try:
            recipe_in_cart = get_object_or_404(
                ShoppingCart,
                user=request.user,
                recipe=recipe
            )
        except Http404:
            raise serializers.ValidationError(
                'Попытка удалить рецепт, которого нет в корзине'
            )
        recipe_in_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request):
        """Функция для того, чтобы скачать список ингредиентов."""
        current_user = request.user
        recipe_list = IngredientRecipe.objects.filter(
            recipe__user_cart__user=current_user
        )
        serializer = IngredientInRecipeSerializer(recipe_list, many=True)
        data = serializer.data
        str_data = ''
        for instance in data:
            if instance['name'] in str_data:
                continue
            for number in range(len(data)):
                if instance['id'] == data[number]['id']:
                    continue
                if instance['name'] == data[number]['name']:
                    amount = data[number]['amount']
                    new_amount = amount + instance['amount']
                    instance['amount'] = new_amount
            ingredient = (f'{instance["name"]} '
                          f'({instance["measurement_unit"]}) - '
                          f'{instance["amount"]}\n')
            str_data += ingredient

        folder_path = os.path.join(settings.BASE_DIR, 'download_shopping_cart')
        os.makedirs(folder_path, exist_ok=True)
        existing_files = os.listdir(folder_path)
        if not existing_files:
            number = '0'
        else:
            number = max(
                [f.split('_')[2].split('.')[0] for f in existing_files]
            )
        file_path = os.path.join(
            folder_path, f'shopping_cart_{str(int(number) + 1)}.txt'
        )
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(str_data)
        return FileResponse(open(file_path, 'rb'))

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        """
        Функция для добавления рецепта в избранное
        и удаления рецепта из избранного.
        """
        recipe = self.get_object()
        if request.method == 'POST':
            try:
                get_object_or_404(
                    Favorite,
                    user=request.user,
                    recipe=recipe
                )
            except Http404:
                Favorite.objects.create(
                    user=request.user,
                    recipe=recipe
                )
            else:
                raise serializers.ValidationError(
                    'Нельзя добавить в избранное один и тот же рецепт'
                )
            serializer = RecipeMinifiedSerializer(recipe)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        try:
            favorite = get_object_or_404(
                Favorite,
                user=request.user,
                recipe=recipe
            )
        except Http404:
            raise serializers.ValidationError(
                'Попытка удалить рецепт из избранного, которого там нет '
            )
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['get'],
        url_path='get-link'
    )
    def get_link(self, request, pk=None):
        """Функция для получения ссылки."""
        instance = self.get_object()
        data = {
            'short-link': reverse(
                'recipes-detail',
                args=[instance.pk],
                request=request
            )
        }
        return Response(data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление для обработки данных."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление для обработки данных."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CustomFilter
    pagination_class = None


class CustomUserViewSet(UserViewSet):
    """Представление для обработки данных."""

    serializer_class = CustomUserSerializer
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
        methods=['delete', 'post'],
        url_path='subscribe',
        serializer_class=UserWithRecipesSerializer,
        permission_classes=[permissions.IsAuthenticated]
    )
    def subscribe_and_unsubscribe(self, request, id=None):
        """Функция для подспки и отписки на пользователя."""
        instance = get_object_or_404(User, id=self.kwargs['id'])
        if request.method == 'POST':
            if instance == request.user:
                raise serializers.ValidationError(
                    'Нельзя подписаться на самого себя'
                )
            try:
                follow = get_object_or_404(
                    Follow,
                    user=request.user,
                    following=instance
                )
            except Http404:
                Follow.objects.create(user=request.user, following=instance)
            else:
                raise serializers.ValidationError(
                    'Нельзя подписаться еще раз на пользователя'
                )
            serializer = self.get_serializer(instance)
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
                headers=headers
            )
        try:
            follow = get_object_or_404(
                Follow,
                user=request.user,
                following=instance
            )
        except Http404:
            raise serializers.ValidationError(
                'Вы пытаетесь удалить несуществующую подписку'
            )
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['put', 'delete'],
        url_path='me/avatar',
        permission_classes=[permissions.IsAuthenticated]
    )
    def avatar(self, request, id=None):
        """Функция для изменения и удаления аватара."""
        user = User.objects.get(username=request.user)
        if request.method == 'PUT':
            serializer = AvatarSerializer(user, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data,
                    status=status.HTTP_200_OK
                )
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
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
        self.get_object = self.get_instance
        return self.retrieve(request, *args, **kwargs)
