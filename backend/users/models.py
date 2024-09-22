"""Модели для создания БД."""

from django.db import models
from django.contrib.auth.models import AbstractUser

from foodgram.constants import CREATE_USER_MAX_LENGTH


class CreateUser(AbstractUser):
    """Класс модели User."""

    first_name = models.CharField(
        'Имя',
        max_length=CREATE_USER_MAX_LENGTH
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=CREATE_USER_MAX_LENGTH
    )
    email = models.EmailField('Почта', unique=True)
    avatar = models.ImageField(
        'Аватар',
        upload_to='avatar_image',
        blank=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']

    class Meta:
        """Класс определяет метаданные для модели User."""

        verbose_name = 'пользователя'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        """Функция для переопределния имени объекта модели."""
        return f'Пользователь: {self.username}'


class Follow(models.Model):
    """Класс модели Follow."""

    user = models.ForeignKey(
        CreateUser,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Подписки'
    )
    following = models.ForeignKey(
        CreateUser,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='Подписчики'
    )

    class Meta:
        """Класс определяет метаданные для модели Follow."""

        verbose_name = 'подписку'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='user_following_unique_relationships'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('following')),
                name='user_following_prevent_self_follow'
            )
        ]

    def __str__(self):
        """Функция для переопределния имени объекта модели."""
        return f'{self.user} подписался на {self.following}'
