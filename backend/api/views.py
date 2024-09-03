from django.contrib.auth import get_user_model
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import viewsets, status, mixins
from rest_framework.reverse import reverse
from rest_framework.decorators import api_view, action
from rest_framework.response import Response

from recipes.models import Recipe, Tag, Ingredient, Favorite, ShoppingCart
from users.models import Follow
from api.serializers import (
    RecipeSerializer,
    RecipeListSerializer,
    TagSerializer,
    IngredientSerializer,
    CustomUserSerializer,
    RecipeMinifiedSerializer,
    AvatarSerializer,
    UserWithRecipesSerializer
)
from api.permissions import IsOwnerOrReadOnly


User = get_user_model()


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOwnerOrReadOnly]
    filter_backend = [DjangoFilterBackend]
    filterset_fields = ['is_in_shopping_cart']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return RecipeListSerializer
        return RecipeSerializer

    def get_object(self):
        return get_object_or_404(Recipe, pk=self.kwargs['pk'])

    def get_queryset(self):
        try:
            User.objects.filter(
                followers__user=self.request.user
            ).update(is_subscribed=True)
            User.objects.exclude(
                followers__user=self.request.user
            ).update(is_subscribed=False)

            Recipe.objects.filter(
                user_favorite__user=self.request.user
            ).update(is_favorited=True)
            Recipe.objects.exclude(
                user_favorite__user=self.request.user
            ).update(is_favorited=False)

            Recipe.objects.filter(
                user_cart__user=self.request.user
            ).update(is_in_shopping_cart=True)
            Recipe.objects.exclude(
                user_cart__user=self.request.user
            ).update(is_in_shopping_cart=False)
        except TypeError:
            pass
        queryset = Recipe.objects.all()
        tags = self.request.GET.getlist('tags')
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart'
        )
        is_favorited = self.request.query_params.get(
            'is_favorited'
        )
        author = self.request.query_params.get('author')
        if tags is not None:
            queryset = queryset.prefetch_related('tags').filter(
                tags__slug__in=tags
            ).distinct()
        if author is not None:
            queryset = queryset.filter(author=author)
        if is_favorited is not None:
            queryset = queryset.filter(is_favorited=is_favorited)
        if is_in_shopping_cart is not None:
            return Recipe.objects.filter(
                is_in_shopping_cart=is_in_shopping_cart
            )
        return queryset

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        if request.method == 'POST':
            data = {
                'pk': pk,
                'name': recipe.name,
                'cooking_time': recipe.cooking_time
            }
            if recipe.image:
                data.update({'image': recipe.image})
            serializer = RecipeMinifiedSerializer(
                data=data
            )
            if serializer.is_valid():
                recipe.is_in_shopping_cart = True
                recipe.save()
                ShoppingCart.objects.create(user=request.user, recipe=recipe)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        recipe.is_in_shopping_cart = False
        recipe.save()
        recipe_in_cart = get_object_or_404(
            ShoppingCart,
            user=request.user,
            recipe=recipe
        )
        recipe_in_cart.delete()
        if not recipe.is_in_shopping_cart:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request):
        recipe_list = Recipe.objects.filter(is_in_shopping_cart=True)
        serializer = RecipeMinifiedSerializer(recipe_list, many=True)
        return Response(serializer.data, content_type='text/plain')

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        if request.method == 'POST':
            data = {
                'pk': pk,
                'name': recipe.name,
                'cooking_time': recipe.cooking_time
            }
            if recipe.image:
                data.update({'image': recipe.image})
            serializer = RecipeMinifiedSerializer(
                data=data
            )
            if serializer.is_valid():
                recipe.is_favorited = True
                recipe.save()
                Favorite.objects.create(user=request.user, recipe=recipe)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.method == 'DELETE':
            recipe.is_favorited = False
            recipe.save()
            favorite = get_object_or_404(
                Favorite,
                user=request.user,
                recipe=recipe
            )
            favorite.delete()
            if not recipe.is_favorited:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk=None):
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
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = [DjangoFilterBackend]


class CustomUserViewSet(UserViewSet):
    permission_classes = [IsOwnerOrReadOnly]
    serializer_class = CustomUserSerializer

    @action(
        detail=False,
        methods=['get'],
        serializer_class=UserWithRecipesSerializer
    )
    def subscriptions(self, request):
        subscriptions = request.user.subscriptions.all()
        users = [user.following for user in subscriptions]
        queryset = User.objects.filter(username__in=users)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=['delete', 'post'],
        url_path='subscribe',
        serializer_class=UserWithRecipesSerializer
    )
    def subscribe_and_unsubscribe(self, request, id=None):
        instance = get_object_or_404(User, id=id)
        if request.method == 'POST':
            instance.is_subscribed = True
            data = {
                'id': id,
                'first_name': instance.first_name,
                'last_name': instance.last_name,
                'username': instance.username,
                'email': instance.email,
                'is_subscribed': instance.is_subscribed
            }
            if instance.avatar:
                data.update({'avatar': instance.avatar})
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            instance.save()
            Follow.objects.create(user=request.user, following=instance)
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
                headers=headers
            )
        instance.is_subscribed = False
        instance.save()
        follow = get_object_or_404(
            Follow,
            user=request.user,
            following=instance
        )
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['put', 'delete'], url_path='me/avatar')
    def avatar(self, request, id=None):
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
