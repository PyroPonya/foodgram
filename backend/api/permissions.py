from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Проверка на автора рецепта."""

    def has_object_permission(self, request, view, recipe):
        """Проверка на автора рецепта."""
        return (
            request.method in permissions.SAFE_METHODS
            or recipe.author == request.user
        )
