from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model


User = get_user_model()


class Ingredient(models.Model):
    """Класс модели Ingredient."""

    name = models.CharField('Название', max_length=128)
    measurement_unit = models.CharField('Единица измерения', max_length=64)

    class Meta:
        """
        Класс определяет метаданные для
        модели Ingredient.
        """

        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

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
        """
        Класс определяет метаданные для
        модели Tag.
        """

        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        """Функция для переопределния имени объекта модели."""
        return self.name


class Recipe(models.Model):
    """Класс модели Recipe."""

    name = models.CharField('Название', max_length=256)
    text = models.TextField('Текст')
    image = models.ImageField(
        'Изображение',
        upload_to='recipes_image',
        null=True,
        blank=True
    )
    is_favorited = models.BooleanField('В избранном', default=False)
    is_in_shopping_cart = models.BooleanField('В корзине', default=False)
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
        """
        Класс определяет метаданные для
        модели Recipe.
        """

        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        """Функция для переопределния имени объекта модели."""
        return self.name


class TagRecipe(models.Model):
    """Класс модели TagRecipe."""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)


class IngredientRecipe(models.Model):
    """Класс модели IngredientRecipe."""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField()


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
