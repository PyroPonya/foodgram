# pep8: noqa
from django_filters.rest_framework import CharFilter, FilterSet

from food.models import Recipe


class RecipeFilter(FilterSet):
    """Фильтр для модели Recipe."""

    author = CharFilter(field_name='author', lookup_expr='exact')
    name = CharFilter(field_name='name', lookup_expr='icontains')
    ingredients = CharFilter(
        field_name='ingredients__name', lookup_expr='icontains')
    tags = CharFilter(field_name='tags__slug', lookup_expr='exact')
    cooking_time = CharFilter(field_name='cooking_time', lookup_expr='exact')

    class Meta:
        model = Recipe
        fields = ('author', 'name', 'ingredients', 'tags', 'cooking_time')
