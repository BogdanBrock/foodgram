"""Модели для создания БД."""

from django.db import models
from django.contrib.auth.models import AbstractUser


class MyUser(AbstractUser):
    """Класс модели MyUser."""

    avatar = models.ImageField(
        'Аватар',
        upload_to='avatar_image',
        blank=True
    )


class Follow(models.Model):
    """Класс модели Follow."""

    user = models.ForeignKey(
        MyUser,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Подписки'
    )
    following = models.ForeignKey(
        MyUser,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='Подписчики'
    )

    class Meta:
        """Класс определяет метаданные для
        модели Follow."""

        verbose_name = 'подписку'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        """Функция для переопределния имени объекта модели."""
        return f'{self.user} подписался на {self.following}'
