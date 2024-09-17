"""Модели для создания БД."""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator


User = get_user_model()


class Ingredient(models.Model):
    """Класс модели Ingredient."""

    name = models.CharField('Название', max_length=128, unique=True)
    measurement_unit = models.CharField('Единица измерения', max_length=64)

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
        return self.name


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
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'slug'],
                name='unique_name_slug'
            )
        ]

    def __str__(self):
        """Функция для переопределния имени объекта модели."""
        return self.name


class Recipe(models.Model):
    """Класс модели Recipe."""

    name = models.CharField('Название', max_length=256)
    text = models.TextField('Текст')
    image = models.ImageField(
        'Изображение',
        upload_to='recipes_image'
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    cooking_time = models.IntegerField(
        'Время приготовления',
        validators=[MinValueValidator(1)]
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    tags = models.ManyToManyField(
        Tag,
        through='TagRecipe',
        verbose_name='Теги'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        verbose_name='Ингредиенты'
    )

    class Meta:
        """Класс определяет метаданные для модели."""

        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        """Функция для переопределния имени объекта модели."""
        return self.name


class TagRecipe(models.Model):
    """Класс модели TagRecipe."""

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        """Класс определяет метаданные для модели TagRecipe."""

        verbose_name = 'тег для рецепта'
        verbose_name_plural = 'Теги добавленные к рецепту'

    def __str__(self):
        """Функция для переопределния имени объекта модели."""
        return f'{self.tag} был добавлен к {self.recipe}'


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
        validators=[MinValueValidator(1)]
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
