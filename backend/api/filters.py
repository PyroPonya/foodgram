from django_filters.rest_framework import FilterSet, filters
from food.models import Ingredient, Recipe, Tag


class IngredientFilter(FilterSet):
    """Фильтр продуктов."""

    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        """Метаданные фильтра."""

        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    """Фильтр рецептов."""

    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug'
    )
    is_favorited = filters.BooleanFilter(method='filter_favorites')
    is_in_shopping_cart = filters.BooleanFilter(method='filter_shoppingcarts')

    class Meta:
        """Метаданные фильтра."""

        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def filter_favorites(self, recipes, name, value):
        """Фильтр избранных рецептов."""
        if self.request.user.is_authenticated and value:
            return recipes.filter(favorites__user=self.request.user)
        return recipes

    def filter_shoppingcarts(self, recipes, name, value):
        """Фильтр списка покупок."""
        if self.request.user.is_authenticated and value:
            return recipes.filter(shoppingcarts__user=self.request.user)
        return recipes
