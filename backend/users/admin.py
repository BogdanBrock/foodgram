"""Админ-зона для API."""

from django.contrib import admin

from .models import MyUser, Follow


admin.site.register(MyUser)
admin.site.register(Follow)
