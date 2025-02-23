from django.contrib.auth import get_user_model
from django.db.models import F, Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status, viewsets, serializers
from rest_framework.decorators import action
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    ImageSerializer,
    IngredientSerializer,
    RecipeCreateUpdateSerializer,
    RecipeSerializer,
    SubscribeSerializer,
    SummaryRecipeSerializer,
    TagSerializer,
)
from .utils import get_shopping_cart

from food.models import (
    Ingredient,
    Recipe,
    Subscription,
    Tag,
)


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
            serializer = ImageSerializer(
                request.user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                {
                    'avatar': request.build_absolute_uri(
                        serializer.data['avatar']
                    )
                }
            )
        request.user.avatar.delete(save=True)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        ['POST', 'DELETE'],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id):
        """Подписка."""
        user = request.user
        author = get_object_or_404(User, pk=id)
        if user == author:
            return Response(
                {'errors': 'Нельзя подписаться на самого себя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = SubscribeSerializer(
            author,
            context={'request': request}
        )
        if request.method == 'DELETE':
            if not Subscription.objects.filter(
                user=user,
                author=author
            ).exists():
                return Response(
                    {'errors': 'Вы не подписаны на этого автора'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            deleted_count, _ = get_object_or_404(
                Subscription,
                user=user,
                author=author
            ).delete()
            if deleted_count == 0:
                return Response(
                    {'errors': 'Вы не подписаны на этого автора'},
                    status=status.HTTP_400_BAD_REQUEST
                )
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
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @action(
        ['GET'],
        detail=False,
        url_path='subscriptions',
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
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    """Рецепты."""

    queryset = Recipe.objects.all()
    http_method_names = ('get', 'post', 'patch', 'delete')
    permission_classes = (
        IsAuthorOrReadOnly,
        IsAuthenticatedOrReadOnly
    )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        """Вобор сериализатора."""
        if self.action in ('create', 'partial_update'):
            return RecipeCreateUpdateSerializer
        return RecipeSerializer

    @action(
        ['GET'],
        detail=True,
        url_path='get-link',
        permission_classes=(AllowAny,)
    )
    def short_link(self, request, pk=None):
        """Короткий url."""
        get_object_or_404(Recipe, pk=pk)
        return Response(
            {
                'short-link': request.build_absolute_uri(
                    reverse('food:short-link', args=(pk,))
                )
            }
        )

    def perform_create(self, serializer):
        """Создание рецепта."""
        serializer.save(author=self.request.user)

    @action(
        ['GET'],
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        """Скачать список покупок."""
        if not request.user.shoppingcarts.exists():
            return serializers.ValidationError(
                {'errors': 'Ваша корзина пуста'}
            )
        return FileResponse(
            get_shopping_cart(
                request.user.shoppingcarts.values(
                    recipe_name=F('recipe__name'),
                    ingredient_name=F('recipe__ingredients__name'),
                    measurement_unit=F(
                        'recipe__ingredients__measurement_unit'
                    ),
                ).annotate(
                    amount=Sum('recipe__amounts__amount')
                ).order_by('ingredient_name')
            ), as_attachment=True, filename='shopping_cart.txt',
            content_type='text/plain'
        )

    @staticmethod
    def add_or_remove_from_collection(request, pk, collection_name):
        """Добавление/удаление рецепта в коллекцию."""
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        collection = getattr(user, collection_name)
        if request.method == 'DELETE':
            get_object_or_404(collection, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        if collection.get_or_create(recipe=recipe)[1]:
            return Response(
                SummaryRecipeSerializer(recipe).data,
                status=status.HTTP_201_CREATED
            )
        raise serializers.ValidationError(
            {'errors': 'Вы уже добавили этот рецепт в коллекцию'}
        )

    @action(
        ['POST', 'DELETE'],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        """Добавление/удаление рецепта в корзину."""
        return self.add_or_remove_from_collection(
            request,
            pk,
            'shoppingcarts'
        )

    @action(
        ['POST', 'DELETE'],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        """Добавление/удаление рецепта в избранное."""
        return self.add_or_remove_from_collection(
            request,
            pk,
            'favorites'
        )
