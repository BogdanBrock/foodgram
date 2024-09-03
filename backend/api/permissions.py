from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if '/users/' in request.path:
            return (
                request.method in permissions.SAFE_METHODS
                or request.is_authenticated
                and obj == request.user
            )
        return (
            request.method in permissions.SAFE_METHODS
            or request.is_authenticated
            and obj.author == request.user
        )
