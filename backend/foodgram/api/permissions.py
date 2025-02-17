# flake8: noqa
from rest_framework.permissions import BasePermission, SAFE_METHODS

# backend / foodgram / food / permissions.py: 1: 1: I001 isort found an import in the wrong position
# backend / foodgram / food / permissions.py: 2: 1: I005 isort found an unexpected missing import


class IsAdminModeratorAuthorOrReadOnly(BasePermission):
    """AdminModeratorAuthorPermission."""

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or obj.author == request.user
            or request.user.is_admin
            or request.user.is_moderator)


class IsAdmin(BasePermission):
    """AdminPermission."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsAdminOrReadOnly(BasePermission):
    """AdminOrReadOnlyPermission."""

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or (request.user.is_authenticated and request.user.is_admin)
        )


class IsAuthorOrReadOnly(BasePermission):
    """AuthorPermission."""

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or obj.author == request.user
