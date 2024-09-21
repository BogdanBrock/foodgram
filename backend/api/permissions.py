"""Разрешения для API."""

from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Разрешение AuthorOrReadOnly."""

    def has_object_permission(self, request, view, obj):
        """Функция для разрешения на уровне объекта."""
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user
                )
