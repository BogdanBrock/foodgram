"""Разрешения для API."""

from rest_framework import permissions


class AuthorOrReadOnly(permissions.BasePermission):
    """Разрешение AuthorOrReadOnly."""

    def has_permission(self, request, view):
        """Функция для разрешения на уровне запросов."""
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        """Функция для разрешения на уровне объекта."""
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user
                )
