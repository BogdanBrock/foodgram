"""Сериализация данных для API."""

import base64

from django.contrib.auth import authenticate, get_user_model
from django.core.files.base import ContentFile
from django.http import Http404
from django.shortcuts import get_list_or_404, get_object_or_404
from djoser.serializers import TokenCreateSerializer, UserCreateSerializer
from rest_framework import serializers

from recipes.models import (
    Favorite, Ingredient, IngredientRecipe,
    Recipe, ShoppingCart, Tag, TagRecipe
)
from users.models import Follow


User = get_user_model()


class Base64ImageField(serializers.ImageField):
    """Сериализатор Base64ImageField."""

    def to_internal_value(self, data):
        """Функция для форматирования данных изображения."""
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор TagSerializer."""

    class Meta:
        """Класс определяет метаданныедля сериализатора."""

        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор IngredientSerializer."""

    class Meta:
        """Класс определяет метаданные для сериализатора."""

        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор IngredientInRecipeSerializer."""

    id = serializers.IntegerField()

    class Meta:
        """Класс определяет метаданные для сериализатора."""

        model = IngredientRecipe
        fields = ('id', 'amount')

    def to_representation(self, instance):
        """Функция для отображения дополнительных данных."""
        representation = super().to_representation(instance)
        ingredient = instance.ingredient
        representation.update(
            {
                'name': ingredient.name,
                'measurement_unit': ingredient.measurement_unit
            }
        )
        return representation


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор AvatarSerializer."""

    avatar = Base64ImageField(allow_null=True)

    class Meta:
        """Класс определяет метаданные для сериализатора."""

        model = User
        fields = ('avatar',)

    def validate_avatar(self, value):
        """Функция для валидации аватара."""
        try:
            value
        except KeyError:
            raise serializers.ValidationError(
                'Отсутствует изображение, которое должно быть в запросе'
            )
        return value


class CustomUserSerializer(serializers.ModelSerializer):
    """Сериализатор CustomUserSerializer."""

    avatar = Base64ImageField(required=False, allow_null=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        """Класс определяет метаданные для сериализатора."""

        model = User
        fields = ('id', 'username', 'first_name',
                  'last_name', 'email', 'is_subscribed', 'avatar'
                  )

    def get_is_subscribed(self, obj):
        """Функция для получения данных о подписке на пользователя."""
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        try:
            get_object_or_404(Follow, user=user, following=obj)
        except Http404:
            return False
        return True


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    """Сериализатор RecipeMinifiedSerializer."""

    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        """Класс определяет метаданные для сериализатора."""

        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserWithRecipesSerializer(serializers.ModelSerializer):
    """Сериализатор UserWithRecipesSerializer."""

    avatar = Base64ImageField(required=False, allow_null=True)
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        """Класс определяет метаданные для сериализатора."""

        model = User
        fields = ('id', 'username', 'first_name',
                  'last_name', 'email', 'is_subscribed',
                  'recipes', 'recipes_count', 'avatar'
                  )

    def get_recipes(self, obj):
        """Функция для получения рецептов для пользователя."""
        request = self.context['request']
        recipes_limit = request.query_params.get('recipes_limit')
        recipes = Recipe.objects.all().order_by(
            '-created_at'
        ).filter(author=obj)
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        serializer = RecipeMinifiedSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        """Функция для получения количества рецептов."""
        return obj.recipes.count()

    def get_is_subscribed(self, obj):
        """Функция для получения данных о подписке на пользователя."""
        user = self.context['request'].user
        try:
            get_object_or_404(Follow, user=user, following=obj)
        except Http404:
            return False
        return True


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор RecipeSerializer."""

    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    ingredients = IngredientInRecipeSerializer(
        many=True,
        source='ingredient_recipe'
    )
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField(required=False, allow_null=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        """Класс определяет метаданные для сериализатора."""

        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def get_is_favorited(self, obj):
        """Функция для получения данных о рецептах в избранном."""
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        try:
            get_object_or_404(Favorite, recipe=obj, user=user)
        except Http404:
            return False
        return True

    def get_is_in_shopping_cart(self, obj):
        """Функция для получения данных о рецептах в корзине."""
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        try:
            get_object_or_404(ShoppingCart, recipe=obj, user=user)
        except Http404:
            return False
        return True

    def to_representation(self, instance):
        """Функция для преобразования данных поля tags."""
        representation = super().to_representation(instance)
        tags = Tag.objects.filter(id__in=instance.tags.all())
        serializer = TagSerializer(tags, many=True)
        representation['tags'] = serializer.data
        return representation

    def create(self, validated_data):
        """Функция для создания данных."""
        ingredients = validated_data.pop('ingredient_recipe')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for instance in ingredients:
            ingredient = get_object_or_404(Ingredient, id=instance['id'])
            IngredientRecipe.objects.create(
                ingredient=ingredient,
                recipe=recipe,
                amount=instance['amount']
            )
        for tag in tags:
            TagRecipe.objects.create(
                tag=tag,
                recipe=recipe
            )
        return recipe

    def update(self, instance, validated_data):
        """Функция для изменения данных."""
        instance.name = validated_data.get('name')
        instance.text = validated_data.get('text')
        instance.image = validated_data.get('image')
        instance.cooking_time = validated_data.get('cooking_time')
        if 'ingredient_recipe' in validated_data:
            ingredients = validated_data['ingredient_recipe']
            ingredient_objects = []
            for obj in ingredients:
                try:
                    ingredient = get_object_or_404(Ingredient, id=obj['id'])
                    IngredientRecipe.objects.filter(
                        ingredient=ingredient
                    ).delete()
                    IngredientRecipe.objects.create(
                        ingredient=ingredient,
                        recipe=instance,
                        amount=obj['amount']
                    )
                    ingredient_objects.append(ingredient)
                except Http404:
                    ingredient_recipe = get_object_or_404(
                        IngredientRecipe,
                        id=obj['id']
                    )
                    ingredient_objects.append(ingredient_recipe.ingredient)
            instance.ingredients.set(ingredient_objects)
        if 'tags' in validated_data:
            tags = validated_data['tags']
            tags_objects = []
            for tag in tags:
                tags_objects.append(tag)
            instance.tags.set(tags_objects)
        instance.save()
        return instance

    def validate(self, data):
        """Функция для валидации данных."""
        try:
            data['ingredient_recipe']
            data['tags']
            data['image']
        except KeyError:
            raise serializers.ValidationError(
                'Отсутствует поле для ввода данных'
            )
        if not data['ingredient_recipe'] or not data['tags']:
            raise serializers.ValidationError(
                'Поле не должно быть пустым'
            )
        ingredients = data['ingredient_recipe']
        ingredients = [ingredient['id'] for ingredient in ingredients]
        if len(ingredients) != len(set(ingredients)):
            raise serializers.ValidationError(
                'Такой ингредиент уже присутствует'
            )
        tags = data['tags']
        tags = [tag.id for tag in tags]
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                'Такой тег уже присутствует'
            )
        try:
            get_list_or_404(Ingredient, id__in=ingredients)
        except Http404:
            raise serializers.ValidationError(
                'Отсутсвует данный ингредиент'
            )
        return data


class CustomTokenCreateSerializer(TokenCreateSerializer):
    """Сериализатор CustomTokenCreateSerializer."""

    def __init__(self, *args, **kwargs):
        """Конструктор класса."""
        super().__init__(*args, **kwargs)
        self.user = None
        self.fields['email'] = serializers.CharField(required=False)

    def validate(self, attrs):
        """Функция для валидации данных."""
        password = attrs.get("password")
        params = {'email': attrs.get('email')}
        self.user = authenticate(
            request=self.context.get("request"), **params, password=password
        )
        if not self.user:
            self.user = User.objects.filter(**params).first()
            if self.user and not self.user.check_password(password):
                self.fail("invalid_credentials")
        if self.user and self.user.is_active:
            return attrs
        self.fail("invalid_credentials")


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор CustomUserCreateSerializer."""

    class Meta:
        """Класс определяет метаданные для сериализатора."""

        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            'username',
            'email',
            'password',
        )

    def validate(self, data):
        """Функция для валидации данных."""
        try:
            data['email']
            data['first_name']
            data['last_name']
        except KeyError:
            raise serializers.ValidationError(
                'Поле не должно быть пустым'
            )
        if User.objects.filter(email=data['email']):
            raise serializers.ValidationError(
                'Такая почта уже существует'
            )
        return data
