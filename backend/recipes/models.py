"""Модели для создания БД."""

from random import choices

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

from foodgram.constants import (
    MIN_VALUE_VALIDATOR,
    MAX_VALUE_VALIDATOR,
    CHARACTERS
)


User = get_user_model()


class Ingredient(models.Model):
    """Класс модели Ingredient."""

    name = models.CharField(
        'Название',
        max_length=128
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=64
    )

    class Meta:
        """Класс определяет метаданные для модели."""

        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='name_measurement_unit_unique'
            )
        ]

    def __str__(self):
        """Функция для переопределния имени объекта модели."""
        return f'Ингредиент: {self.name}'


class Tag(models.Model):
    """Класс модели Tag."""

    name = models.CharField(
        'Название',
        max_length=32
    )
    slug = models.SlugField(
        'Слаг',
        max_length=32,
        unique=True,
        null=True,
        blank=True
    )

    class Meta:
        """Класс определяет метаданные для модели."""

        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        """Функция для переопределния имени объекта модели."""
        return f'Тег: {self.name}'


class Recipe(models.Model):
    """Класс модели Recipe."""

    name = models.CharField('Название', max_length=256)
    text = models.TextField('Текст')
    image = models.ImageField(
        'Изображение',
        upload_to='recipes_image'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=[
            MinValueValidator(
                MIN_VALUE_VALIDATOR,
                message='Минимальное значение не должно '
                        f'быть ниже {MIN_VALUE_VALIDATOR}'
            ),
            MaxValueValidator(
                MAX_VALUE_VALIDATOR,
                message='Максимальное значение не должно '
                        f'быть выше {MAX_VALUE_VALIDATOR}'
            )
        ]
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    short_url = models.CharField(max_length=10, unique=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        verbose_name='Ингредиенты'
    )

    def save(self, **kwargs):
        """Функция для сохранения данных."""
        if not self.short_url:
            self.short_url = self.get_short_url()
        super().save(**kwargs)

    def get_short_url(self):
        """Функция для получения короткой ссылки"""
        short_url = ''.join(choices(CHARACTERS, k=10))
        recipe_with_short_url = Recipe.objects.filter(
            short_url=short_url
        ).exists()
        while recipe_with_short_url:
            short_url = short_url
        return short_url

    class Meta:
        """Класс определяет метаданные для модели."""

        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-created_at',)

    def __str__(self):
        """Функция для переопределния имени объекта модели."""
        return f'Рецепт: {self.name}'


class IngredientRecipe(models.Model):
    """Класс модели IngredientRecipe."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_recipe'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE
    )
    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                MIN_VALUE_VALIDATOR,
                message='Минимальное значение не должно '
                        f'быть ниже {MIN_VALUE_VALIDATOR}'
            ),
            MaxValueValidator(
                MAX_VALUE_VALIDATOR,
                message='Максимальное значение не должно '
                        f'быть выше {MAX_VALUE_VALIDATOR}'
            )
        ]
    )

    class Meta:
        """Класс определяет метаданные для модели."""

        verbose_name = 'ингредиент в рецепт'
        verbose_name_plural = 'Ингредиенты добавленные в рецепт'

    def __str__(self):
        """Функция для переопределния имени объекта модели."""
        return f'{self.ingredient} был(а, о) добавлен в {self.recipe}'


class Favorite(models.Model):
    """Класс модели Favorite."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='user_favorite',
        verbose_name='Избранный рецепт'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_recipes',
        verbose_name='Пользователь'
    )

    class Meta:
        """Класс определяет метаданные для модели."""

        verbose_name = 'в избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        """Функция для переопределния имени объекта модели."""
        return f'{self.user} добавил(а) {self.recipe} в избранное'


class ShoppingCart(models.Model):
    """Класс модели ShoppingCart."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='user_cart',
        verbose_name='Рецепт в корзине'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes_in_cart',
        verbose_name='Пользователь'
    )

    class Meta:
        """Класс определяет метаданные для модели."""

        verbose_name = 'в корзину'
        verbose_name_plural = 'Корзина'

    def __str__(self):
        """Функция для переопределния имени объекта модели."""
        return f'{self.user} добавил(а) {self.recipe} в корзину'
