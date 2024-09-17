"""Админ-зона для API."""

from django.contrib import admin

from .models import MyUser, Follow


class FollowAdmin(admin.ModelAdmin):
    """Класс для управление админ-зоной."""

    search_fields = ['email', 'username']


admin.site.register(MyUser)
admin.site.register(Follow, FollowAdmin)
