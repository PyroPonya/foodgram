# flake8: noqa
from django.contrib.auth import get_user_model
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
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
    SubscribeSerializer,
    ImageSerializer,
    TagSerializer,
    IngredientSerializer,
    RecipeSerializerWrite,
    RecipeSerializerRead,
    ShoppingListSerializer
)
from api.permissions import (
    IsAdmin,
    IsAuthorOrReadOnly,
    IsAdminOrReadOnly,
    IsAdminModeratorAuthorOrReadOnly
)
from food.models import (
    Subscription,
    Ingredient,
    Recipe,
    Tag,
    ShoppingList,
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
        url_path='(?P<id>[0-9]+)/subscribe/',
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

    @action(
        ['GET'],
        detail=True,
        url_path='(?P<id>[0-9]+)',
        permission_classes=[IsAdminOrReadOnly]
    )
    def tag(self, request, id):
        """Тег."""
        tag = get_object_or_404(Tag, id=id)
        serializer = TagSerializer(tag)
        return Response(serializer.data)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Ингредиенты."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None

    @action(
        ['GET'],
        detail=True,
        url_path='(?P<id>[0-9]+)',
        permission_classes=[IsAuthenticatedOrReadOnly]
    )
    def ingredient(self, request, id):
        """Ингредиент."""
        ingredient = get_object_or_404(Ingredient, id=id)
        serializer = IngredientSerializer(ingredient)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RecipeViewSet(viewsets.ModelViewSet):
    """Список рецептов. Страница доступна всем пользователям."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializerRead
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = RecipeFilter
    search_fields = ['^name']

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        is_favorited = self.request.query_params.get('is_favorited')
        if is_favorited is not None:
            queryset = queryset.filter(favorites__user=user)

        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart')
        if is_in_shopping_cart is not None:
            queryset = queryset.filter(shopping_cart__user=user)

        author_id = self.request.query_params.get('author')
        if author_id is not None:
            queryset = queryset.filter(author_id=author_id)

        tags = self.request.query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()

        return queryset

    @action(
        methods=['post'],
        detail=False,
        url_path='',
        permission_classes=[IsAuthenticated],
    )
    def create_recipe(self, request):
        """Создание рецепта. Доступно только авторизованному пользователю."""
        serializer = RecipeSerializerWrite(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        methods=['get'],
        detail=True,
        url_path='(?P<id>[0-9]+)',
        permission_classes=[IsAuthenticatedOrReadOnly]
    )
    def retrieve_recipe(self, request, id):
        """Получение рецепта по ID."""
        recipe = get_object_or_404(Recipe, id=id)
        serializer = RecipeSerializerRead(recipe, context={'request': request})
        return Response(serializer.data)

    @action(
        methods=['patch'],
        detail=True,
        url_path='(?P<id>[0-9]+)',
        permission_classes=[IsAuthorOrReadOnly]
    )
    def update_recipe(self, request, id):
        """Обновление рецепта. Доступно только автору данного рецепта."""
        recipe = get_object_or_404(Recipe, id=id, author=request.user)
        serializer = RecipeSerializerWrite(
            recipe, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['delete'],
        detail=True,
        url_path='(?P<id>[0-9]+)',
        permission_classes=[IsAuthorOrReadOnly]
    )
    def delete_recipe(self, request, id):
        """Удаление рецепта. Доступно только автору данного рецепта."""
        recipe = get_object_or_404(Recipe, id=id, author=request.user)
        recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['get'],
        detail=True,
        url_path='(?P<id>[0-9]+)/get-link',
        permission_classes=[IsAuthenticatedOrReadOnly]
    )
    def get_short_link(self, request, id):
        """Получить короткую ссылку на рецепт."""
        recipe = get_object_or_404(Recipe, id=id)
        return Response(
            {'short_link': request.build_absolute_uri(f'/api/recipes/{id}/')},
            status=status.HTTP_200_OK
        )

    @action(
        methods=['post'],
        detail=True,
        url_path='(?P<id>[0-9]+)/favorite',
        permission_classes=[IsAuthenticated]
    )
    def add_to_favorites(self, request, id):
        """Добавить рецепт в избранное."""
        recipe = get_object_or_404(Recipe, id=id)
        if recipe.favorites.filter(user=request.user).exists():
            return Response(
                {'errors': 'Рецепт уже добавлен в избранное'},
                status=status.HTTP_400_BAD_REQUEST
            )
        recipe.favorites.get_or_create(user=request.user)
        serializer = RecipeSerializerRead(recipe, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        methods=['delete'],
        detail=True,
        url_path='(?P<id>[0-9]+)/favorite',
        permission_classes=[IsAuthenticated]
    )
    def remove_from_favorites(self, request, id):
        """Удалить рецепт из избранного. Доступно только авторизованным пользователям."""
        recipe = get_object_or_404(Recipe, id=id)
        favorite = recipe.favorites.filter(user=request.user)
        if not favorite.exists():
            return Response(
                {'errors': 'Рецепт не найден в избранном'},
                status=status.HTTP_400_BAD_REQUEST
            )
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['get'],
        detail=False,
        url_path='download_shopping_cart',
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        """Скачать список покупок. Доступно только авторизованным пользователям."""
        # Fetching shopping list for the authenticated user
        shopping_list = ShoppingList.objects.filter(user=request.user)

        # Example: Creating a text file with shopping list items
        content = "\n".join(
            [f"{item.recipe.name}: {item.amount}" for item in shopping_list])
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="shopping_list.txt"'
        return response

    @action(
        methods=['post'],
        detail=True,
        url_path='(?P<id>[0-9]+)/shopping_cart',
        permission_classes=[IsAuthenticated]
    )
    def add_to_shopping_cart(self, request, id):
        """Добавить рецепт в список покупок. Доступно только авторизованным пользователям."""
        recipe = get_object_or_404(Recipe, id=id)
        shopping_item, created = ShoppingList.objects.get_or_create(
            user=request.user, recipe=recipe)

        if not created:
            return Response(
                {'errors': 'Рецепт уже есть в списке покупок'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = RecipeSerializerRead(recipe, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        methods=['delete'],
        detail=True,
        url_path='(?P<id>[0-9]+)/shopping_cart',
        permission_classes=[IsAuthenticated]
    )
    def remove_from_shopping_cart(self, request, id):
        """Удалить рецепт из списка покупок. Доступно только авторизованным пользователям."""
        recipe = get_object_or_404(Recipe, id=id)
        shopping_item = ShoppingList.objects.filter(
            user=request.user, recipe=recipe)

        if not shopping_item.exists():
            return Response(
                {'errors': 'Рецепта нет в списке покупок'},
                status=status.HTTP_400_BAD_REQUEST
            )

        shopping_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
