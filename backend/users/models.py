from django.db import models
from django.contrib.auth.models import AbstractUser


class MyUser(AbstractUser):
    avatar = models.ImageField(
        'Аватар',
        upload_to='avatar_image',
        blank=True
    )


class Follow(models.Model):
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
        verbose_name = 'подписку'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user} подписался на {self.following}'
