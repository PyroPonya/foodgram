# flake8: noqa
from django.contrib.auth import get_user_model
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import (
    filters,
    permissions,
    status,
    viewsets
)
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    IsAuthenticated
)
from rest_framework.response import Response
from rest_framework.views import APIView

from api.filters import RecipeFilter
from api.pagination import (
    CustomPageNumberPagination,
    CustomUserlistPageNumberPagination
)
from api.serializers import (
    UserSerializer,
    SubscribeSerializer,
    ImageSerializer,
    TagSerializer,
    IngredientSerializer,
    RecipeSerializerWrite,
    RecipeSerializerRead
)
from api.permissions import (
    IsAdmin,
    IsAuthorOrReadOnly,
    IsAdminOrReadOnly,
    IsAdminModeratorAuthorOrReadOnly
)
from food.models import Subscription, Ingredient, Recipe, Tag


User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    """Пользователи."""

    def get_permissions(self):
        """Права доступа."""
        if self.action == 'me':
            return [IsAuthenticated()]
        return super().get_permissions()

    @action(
        ['PUT', 'DELETE'],
        detail=False,
        url_path='me/avatar',
        permission_classes=[IsAuthenticated]
    )
    def avatar(self, request):
        """Аватар."""
        if request.method == 'PUT':
            if 'avatar' not in request.data:
                raise serializers.ValidationError(
                    {'errors': 'Avatar обязательное поле'}
                )
            serializer = ImageSerializer(
                instance=request.user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                {'avatar': request.build_absolute_uri(
                    serializer.data['avatar'])}
            )
        request.user.avatar.delete(save=True)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        ['POST', 'DELETE'],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id):
        """Подписка/отписка."""
        user = request.user
        author = get_object_or_404(User, pk=id)
        serializer = SubscribeSerializer(
            author, context={'request': request}
        )
        if request.method == 'DELETE' or user.id == author.id:
            get_object_or_404(
                Subscription,
                user=user,
                author=author
            ).delete()
            return Response(
                serializer.data,
                status=status.HTTP_204_NO_CONTENT
            )
        if not Subscription.objects.get_or_create(
            user=user,
            author=author
        )[1]:
            raise serializers.ValidationError(
                {'errors': 'Вы уже подписаны на этого автора'}
            )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        ['GET'],
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        """Подписки."""
        return self.get_paginated_response(
            SubscribeSerializer(
                self.paginate_queryset(
                    User.objects.filter(authors__user=request.user)
                ),
                many=True,
                context={'request': request}
            ).data
        )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Теги."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Ингредиенты."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Рецепты."""

    queryset = Recipe.objects.all()
    pagination_class = CustomPageNumberPagination
    permission_classes = (IsAdminOrReadOnly, IsAuthorOrReadOnly)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = RecipeFilter
    ordering_fields = ('id', 'name', 'cooking_time', 'tags__name')
    ordering = ('tags__name', 'cooking_time')

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeSerializerWrite
        return RecipeSerializerRead
