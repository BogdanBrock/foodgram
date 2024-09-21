"""Сериализация данных для API."""

import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework import serializers

from recipes.models import (
    Favorite, Ingredient, IngredientRecipe,
    Recipe, ShoppingCart, Tag
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


class CreateUserSerializer(serializers.ModelSerializer):
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
        request = self.context['request']
        return (request
                and request.user.is_authenticated
                and Follow.objects.filter(
                    user=request.user, following=obj
                ).exists())


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    """Сериализатор RecipeMinifiedSerializer."""

    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        """Класс определяет метаданные для сериализатора."""

        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserWithRecipesSerializer(CreateUserSerializer):
    """Сериализатор UserWithRecipesSerializer."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        """Класс определяет метаданные для сериализатора."""

        model = User
        fields = CreateUserSerializer.Meta.fields + (
            'recipes',
            'recipes_count'
        )

    def get_recipes(self, obj):
        """Функция для получения рецептов для пользователя."""
        request = self.context['request']
        recipes_limit = request.query_params.get('recipes_limit')
        recipes = Recipe.objects.all().order_by(
            '-created_at'
        ).filter(author=obj)
        if recipes_limit:
            try:
                recipes = recipes[:int(recipes_limit)]
            except ValueError:
                pass
        serializer = RecipeMinifiedSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        """Функция для получения количества рецептов."""
        return obj.recipes.count()

    def get_is_subscribed(self, obj):
        """Функция для получения данных о подписке на пользователя."""
        request = self.context['request']
        return (request
                and request.user.is_authenticated
                and Follow.objects.filter(
                    user=request.user, following=obj
                ).exists())


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

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        """Класс определяет метаданные для сериализатора."""

        model = IngredientRecipe
        fields = ('id', 'amount')

    def to_internal_value(self, data):
        """Функция для форматирования данных."""
        internal_value = super().to_internal_value(data)
        internal_value['id'] = data.pop('id')
        return internal_value


class IngredientInRecipeGetSerializer(serializers.ModelSerializer):
    """Сериализатор IngredientInRecipeGetSerializer."""

    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        """Класс определяет метаданные для сериализатора."""

        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор AvatarSerializer."""

    avatar = Base64ImageField(allow_null=True)

    class Meta:
        """Класс определяет метаданные для сериализатора."""

        model = User
        fields = ('avatar',)


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
    author = CreateUserSerializer(read_only=True)
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        """Класс определяет метаданные для сериализатора."""

        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'name', 'image', 'text', 'cooking_time'
        )

    def to_representation(self, instance):
        """Функция для преобразования данных поля tags."""
        request = self.context['request']
        serializer = RecipeGetSerializer(
            instance,
            context={'request': request}
        )
        return serializer.data

    def create_or_update(self, instance, ingredients):
        """Функция для основных функций update и create."""
        ingredient_objects = []
        for obj in ingredients:
            ingredient_recipe = IngredientRecipe(
                ingredient_id=obj['id'],
                recipe=instance,
                amount=obj['amount']
            )
            ingredient_objects.append(ingredient_recipe)
        IngredientRecipe.objects.bulk_create(ingredient_objects)

    def create(self, validated_data):
        """Функция для создания данных."""
        ingredients = validated_data.pop('ingredient_recipe')
        tags = validated_data.pop('tags')
        validated_data['author'] = self.context['request'].user
        instance = Recipe.objects.create(**validated_data)
        self.create_or_update(instance, ingredients)
        for tag in tags:
            instance.tags.add(tag)
        return instance

    def update(self, instance, validated_data):
        """Функция для изменения данных."""
        instance.name = validated_data.get('name')
        instance.text = validated_data.get('text')
        instance.image = validated_data.get('image')
        instance.cooking_time = validated_data.get('cooking_time')
        if 'ingredient_recipe' in validated_data:
            ingredients = validated_data.pop('ingredient_recipe')
            instance.ingredients.clear()
            self.create_or_update(instance, ingredients)
        if 'tags' in validated_data:
            tags = validated_data.pop('tags')
            tags_objects = []
            for tag in tags:
                tags_objects.append(tag)
            instance.tags.set(tags_objects)
        return super().update(instance, validated_data)

    def validate(self, data):
        """Функция для валидации данных."""
        if 'ingredient_recipe' not in data:
            raise serializers.ValidationError(
                'Отсутствует поле с ингредиентами'
            )
        if 'tags' not in data:
            raise serializers.ValidationError(
                'Отсутствует поле с тегами'
            )
        if 'image' not in data:
            raise serializers.ValidationError(
                'Отсутствует поле с изображением'
            )
        if not data['ingredient_recipe']:
            raise serializers.ValidationError(
                'Значение в поле с ингредиентами не должно быть пустым'
            )
        if not data['tags']:
            raise serializers.ValidationError(
                'Значение в поле с тегами не должно быть пустым'
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
        return data


class RecipeGetSerializer(serializers.ModelSerializer):
    """Сериализатор RecipeGetSerializer."""

    tags = TagSerializer(many=True)
    ingredients = IngredientInRecipeGetSerializer(
        many=True,
        source='ingredient_recipe'
    )
    author = CreateUserSerializer(read_only=True)
    image = Base64ImageField(required=False, allow_null=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        """Класс определяет метаданные для сериализатора."""

        model = Recipe
        fields = RecipeSerializer.Meta.fields + (
            'is_favorited',
            'is_in_shopping_cart'
        )

    def get_is_favorited(self, obj):
        """Функция для получения данных о рецептах в избранном."""
        request = self.context['request']
        return (request
                and request.user.is_authenticated
                and Favorite.objects.filter(
                    user=request.user, recipe=obj
                ).exists())

    def get_is_in_shopping_cart(self, obj):
        """Функция для получения данных о рецептах в корзине."""
        request = self.context['request']
        return (request
                and request.user.is_authenticated
                and ShoppingCart.objects.filter(
                    user=request.user, recipe=obj
                ).exists())


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор FavoriteSerializer."""

    class Meta:
        """Класс определяет метаданные для сериализатора."""

        model = Favorite
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        """Функция для преобразования данных."""
        serializer = RecipeMinifiedSerializer(instance.recipe)
        return serializer.data

    def validate(self, data):
        """Функция для валидации данных."""
        if Favorite.objects.filter(
            user=data['user'],
            recipe=data['recipe']
        ).exists():
            raise serializers.ValidationError(
                'Нельзя добавить в избранное один и тот же рецепт'
            )
        return data


class ShoppingCartSerializer(FavoriteSerializer):
    """Сериализатор ShoppingCartSerializer."""

    class Meta(FavoriteSerializer.Meta):
        """Класс определяет метаданные для сериализатора."""

        model = ShoppingCart

    def validate(self, data):
        """Функция для валидации данных."""
        if ShoppingCart.objects.filter(
            user=data['user'],
            recipe=data['recipe']
        ).exists():
            raise serializers.ValidationError(
                'Нельзя добавить в список покупок один и тот же рецепт'
            )
        return data


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор FollowSerializer."""

    class Meta:
        """Класс определяет метаданные для сериализатора."""

        model = Follow
        fields = ('user', 'following')

    def to_representation(self, instance):
        """Функция для преобразования данных."""
        request = self.context['request']
        serializer = UserWithRecipesSerializer(
            instance.following,
            context={'request': request}
        )
        return serializer.data

    def validate(self, data):
        """Функция для валидации данных."""
        if data['user'] == data['following']:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя'
            )
        follow = Follow.objects.filter(
            user=data['user'],
            following=data['following']
        ).exists()
        if follow:
            raise serializers.ValidationError(
                'Нельзя подписаться еще раз на пользователя'
            )
        return data
