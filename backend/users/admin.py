"""Админ-зона для API."""

from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Follow


User = get_user_model()


class FollowAdmin(admin.ModelAdmin):
    """Класс для управление админ-зоной."""

    search_fields = ['email', 'username']


admin.site.register(User)
admin.site.register(Follow, FollowAdmin)
