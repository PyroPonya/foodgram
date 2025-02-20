from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.db.models import Count
from django.utils.html import mark_safe

from food.models import (
    AmountIngredient,
    Favorite,
    Ingredient,
    Recipe,
    ShoppingCart,
    Subscription,
    Tag,
)

admin.site.unregister(Group)
User = get_user_model()


class SubscriptionInline(admin.TabularInline):
    """Вывод подписок в админке."""

    model = Subscription
    fk_name = 'user'
    verbose_name = 'Подписка'
    verbose_name_plural = 'Подписки'


class FavoriteInline(admin.TabularInline):
    """Вывод избранных в админке."""

    model = Favorite
    verbose_name = 'Избранное'
    verbose_name_plural = 'Избранное'


class ShoppingCartInline(admin.TabularInline):
    """Вывод списка покупок в админке."""

    model = ShoppingCart
    verbose_name = 'Список покупок'
    verbose_name_plural = 'Списки покупок'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Вывод пользователей в админке."""

    model = User
    inlines = (SubscriptionInline, FavoriteInline, ShoppingCartInline)
    list_display = (
        'email', 'username', 'full_name', 'recipes_count',
        'subscribers_count', 'favorites_count', 'avatar_tag'
    )
    search_fields = ('email', 'username', 'full_name')

    @admin.display(description='Полное имя')
    def full_name(self, user):
        """Вывод полного имени."""
        return f'{user.first_name} {user.last_name}'

    def get_queryset(self, request):
        """Возвращает queryset с дополнительными полями."""
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            recipes_count=Count('recipes'),
            subscribers_count=Count('subscribers'),
            favorites_count=Count('favorites'),
        )
        return queryset

    @admin.display(description='Избранных')
    def favorites_count(self, obj):
        """Возвращает количество избранных."""
        return obj.favorites_count

    @admin.display(description='Подписчиков')
    def subscribers_count(self, obj):
        """Возвращает количество подписчиков."""
        return obj.subscribers_count

    @admin.display(description='Количество рецептов')
    def recipes_count(self, obj):
        """Возвращает количество рецептов, в которых участвует пользователь."""
        return obj.recipes_count

    @mark_safe
    @admin.display(description='Аватар')
    def avatar_tag(self, user):
        """Вывод аватара."""
        if user.avatar:
            return f'<img width="50" height="50" src="{user.avatar.url}" />'
        return '-пусто-'


class AmountIngredientInline(admin.TabularInline):
    """Вывод продуктов в админке."""

    model = AmountIngredient
    verbose_name = 'Продукт'
    verbose_name_plural = 'Продукты'
    fields = ('ingredient', 'amount')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Вывод рецептов в админке."""

    inlines = (AmountIngredientInline,)

    list_display = (
        'id', 'name', 'cooking_time', 'author', 'favorites_count',
        'tags_list', 'ingredients_list', 'image_tag'
    )
    search_fields = ('name', 'author__username', 'tags__name')
    list_filter = ('author__username', 'tags__name')

    @mark_safe
    @admin.display(description='Теги')
    def tags_list(self, recipe):
        """Вывод тегов."""
        return '<br>'.join(tag.name for tag in recipe.tags.all())

    @mark_safe
    @admin.display(description='Изображение')
    def image_tag(self, recipe):
        """Вывод изображения."""
        return f'<img width="50" height="50" src="{recipe.image.url}" />'

    @admin.display(description='Избранных')
    def favorites_count(self, recipe):
        """Вывод количества избранных."""
        return recipe.favorites.count()

    @mark_safe
    @admin.display(description='Продукты')
    def ingredients_list(self, recipe):
        """Вывод продуктов."""
        return '<br>'.join(
            f'{ingredient.ingredient.name} - {ingredient.amount}'
            f' ({ingredient.ingredient.measurement_unit})'
            for ingredient in recipe.amounts.all()
        )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Вывод продуктов в админке."""

    model = Ingredient
    list_display = ('name', 'measurement_unit', 'recipes_count')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)

    def get_queryset(self, request):
        """Возвращает queryset с дополнительными полями."""
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            recipes_count=Count('recipes'),
        )
        return queryset

    @admin.display(description='Количество рецептов')
    def recipes_count(self, obj):
        """Возвращает количество рецептов, в которых участвует продукт."""
        return obj.recipes_count


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Вывод тегов в админке."""

    list_display = ('name', 'slug', 'recipes_count')
    search_fields = ('name', 'slug')

    def get_queryset(self, request):
        """Возвращает queryset с дополнительными полями."""
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            recipes_count=Count('recipes'),
        )
        return queryset

    @admin.display(description='Количество рецептов')
    def recipes_count(self, obj):
        """Возвращает количество рецептов, в которых участвует тег."""
        return obj.recipes_count


@admin.register(AmountIngredient)
class AmountIngredientAdmin(admin.ModelAdmin):
    """Вывод продуктов в админке."""

    list_display = ('recipe', 'ingredient', 'amount')
    search_fields = ('recipe__name', 'ingredient__name')
    ordering = ('recipe__name', 'ingredient__name')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Вывод подписок в админке."""

    list_display = ('user', 'author')
    search_fields = ('user__username', 'author__username')
    ordering = ('user__username', 'author__username')


class UserRecipeAdminModel(admin.ModelAdmin):
    """Вывод избранных и корзины в админке."""

    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
    ordering = ('user__username', 'recipe__name')


@admin.register(Favorite)
class FavoriteAdmin(UserRecipeAdminModel):
    """Вывод избранных в админке."""

    pass


@admin.register(ShoppingCart)
class ShoppingCartAdmin(UserRecipeAdminModel):
    """Вывод корзины в админке."""

    pass
