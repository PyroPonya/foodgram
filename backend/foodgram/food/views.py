from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

from .models import Ingredient, Recipe, Tag
from .serializers import (IngredientSerializer, RecipeReadSerializer,
                          RecipeWriteSerializer, TagSerializer)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = PageNumberPagination
    lookup_field = 'slug'

    def get_queryset(self):
        return Tag.objects.all()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = PageNumberPagination
    lookup_field = 'slug'

    def get_queryset(self):
        return Ingredient.objects.all()


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeWriteSerializer
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        if self.action in ('create', 'partial_update'):
            return RecipeWriteSerializer

    def get_queryset(self):
        return Recipe.objects.all()
