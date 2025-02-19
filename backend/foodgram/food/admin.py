# flake8: noqa
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.utils.html import mark_safe

from food.models import (
    AmountIngredient,
    Favorite,
    Ingredient,
    Recipe,
    ShoppingCart,
    Subscription,
    Tag
)

admin.site.unregister(Group)
User = get_user_model()


class SubscriptionInline(admin.TabularInline):
    model = Subscription
    fk_name = 'user'
    verbose_name = 'Подписка'
    verbose_name_plural = 'Подписки'


class FavoriteInline(admin.TabularInline):
    model = Favorite
    verbose_name = 'Избранное'
    verbose_name_plural = 'Избранное'


class ShoppingCartInline(admin.TabularInline):
    model = ShoppingCart
    verbose_name = 'Список покупок'
    verbose_name_plural = 'Списки покупок'


@admin.register(User)
class UserAdmin(UserAdmin):
    inlines = (SubscriptionInline, FavoriteInline, ShoppingCartInline)
    list_display = (
        'email', 'username', 'full_name', 'recipes_count',
        'subscribers_count', 'favorites_count', 'avatar_tag'
    )
    search_fields = ('email', 'username', 'full_name')

    @admin.display(description='Полное имя')
    def full_name(self, user):
        return f'{user.first_name} {user.last_name}'

    @admin.display(description='Рецептов')
    def recipes_count(self, user):
        return user.recipes.count()

    @admin.display(description='Подписок')
    def subscribers_count(self, user):
        return user.subscribers.count()

    @admin.display(description='Избранных')
    def favorites_count(self, user):
        return user.favorites.count()

    @mark_safe
    @admin.display(description='Аватар')
    def avatar_tag(self, user):
        if user.avatar:
            return f'<img width="50" height="50" src="{user.avatar.url}" />'
        return 'пусто'


class AmountIngredientInline(admin.TabularInline):
    model = AmountIngredient
    verbose_name = 'Продукт'
    verbose_name_plural = 'Продукты'
    fields = ('ingredient', 'amount')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
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
        return '<br>'.join(tag.name for tag in recipe.tags.all())

    @mark_safe
    @admin.display(description='Изображение')
    def image_tag(self, recipe):
        return f'<img width="50" height="50" src="{recipe.image.url}" />'

    @admin.display(description='Избранных')
    def favorites_count(self, recipe):
        return recipe.favorites.count()

    @mark_safe
    @admin.display(description='Продукты')
    def ingredients_list(self, recipe):
        return '<br>'.join(
            f'{ingredient.ingredient.name} - {ingredient.amount}'
            f' ({ingredient.ingredient.measurement_unit})'
            for ingredient in recipe.amounts.all()
        )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit', 'recipes_count')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)

    @admin.display(description='Рецептов')
    def recipes_count(self, ingredient):
        return ingredient.recipes.count()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'recipes_count')
    search_fields = ('name', 'slug')

    @admin.display(description='Рецептов')
    def recipes_count(self, tag):
        return tag.recipes.count()


@admin.register(AmountIngredient)
class AmountIngredient(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')
    search_fields = ('recipe__name', 'ingredient__name')
    ordering = ('recipe__name', 'ingredient__name')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    search_fields = ('user__username', 'author__username')
    ordering = ('user__username', 'author__username')


class UserRecipeAdminModel(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
    ordering = ('user__username', 'recipe__name')


@admin.register(Favorite)
class FavoriteAdmin(UserRecipeAdminModel):
    pass


@admin.register(ShoppingCart)
class ShoppingCartAdmin(UserRecipeAdminModel):
    pass
