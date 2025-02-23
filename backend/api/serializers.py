from django.contrib.auth import get_user_model
from django.db import transaction
from djoser.serializers import UserSerializer as DjoserUserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from food.constants import MIN_AMOUNT, MIN_COOKING_TIME
from food.models import (
    AmountIngredient,
    Favorite,
    Ingredient,
    Recipe,
    ShoppingCart,
    Subscription,
    Tag
)

User = get_user_model()


class ImageSerializer(serializers.ModelSerializer):
    """Сериализатор изображения."""

    avatar = Base64ImageField(required=True, allow_null=False)

    class Meta:
        """Мета класс."""

        model = User
        fields = ('avatar',)


class UserSerializer(DjoserUserSerializer):
    """Сериализатор пользователя."""

    is_subscribed = serializers.SerializerMethodField(read_only=True)
    avatar = Base64ImageField(read_only=True)

    class Meta(DjoserUserSerializer.Meta):
        """Мета класс."""

        fields = (
            *DjoserUserSerializer.Meta.fields,
            'avatar',
            'is_subscribed'
        )
        extra_kwargs = {'password': {'write_only': True}}

    def get_is_subscribed(self, author):
        """Проверка подписки."""
        request = self.context.get('request')
        return (
            request is not None
            and request.user.is_authenticated
            and Subscription.objects.filter(
                user=request.user,
                author=author
            ).exists()
        )

    def validate(self, data):
        """Validate avatar field."""
        request = self.context.get('request')
        if request and request.method == 'PUT' and 'avatar' not in request.data:
            raise serializers.ValidationError(
                {'avatar': 'Поле avatar обязательно'}
            )
        return data


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор продукта."""

    class Meta:
        """Мета класс."""

        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тега."""

    class Meta:
        """Мета класс."""

        model = Tag
        fields = ('id', 'name', 'slug')


class AmountIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиента."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.values_list('id', flat=True),
        required=True,
        allow_null=False
    )

    class Meta:
        """Мета класс."""

        model = AmountIngredient
        fields = ('id', 'amount')


class ReadAmountIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиента для чтения."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.values_list('id', flat=True),
        required=True,
        allow_null=False
    )
    amount = serializers.IntegerField(
        required=True,
        min_value=MIN_AMOUNT,
        allow_null=False
    )
    name = serializers.CharField(
        source='ingredient.name',
        read_only=True
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )

    class Meta:
        """Мета класс."""

        model = AmountIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецепта."""

    tags = TagSerializer(many=True)
    ingredients = ReadAmountIngredientSerializer(
        many=True,
        source='amounts'
    )
    author = UserSerializer()

    class Meta:
        """Мета класс."""

        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор рецепта."""

    ingredients = AmountIngredientSerializer(
        many=True, required=True, allow_empty=False
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, allow_empty=False
    )
    image = Base64ImageField(required=True, allow_null=False)
    cooking_time = serializers.IntegerField(min_value=MIN_COOKING_TIME)

    class Meta:
        """Мета класс."""

        model = Recipe
        fields = (
            'author',
            'cooking_time',
            'image',
            'ingredients',
            'name',
            'tags',
            'text',
        )
        read_only_fields = ('author',)

    def validate(self, data):
        """Валидация рецепта."""
        for field in ('ingredients', 'tags'):
            if not data.get(field):
                raise serializers.ValidationError(
                    {field: f'{field.capitalize()} обязательны'}
                )
        ingredients = [ingredient['id'] for ingredient in data['ingredients']]
        if len(ingredients) != len(set(ingredients)):
            raise serializers.ValidationError(
                {'ingredients': 'Ингредиенты должны быть уникальны'}
            )
        tags = data['tags']
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                {'tags': 'Тэги должны быть уникальны'}
            )
        return data

    def validate_image(self, image):
        """Валидация поля image."""
        if not image:
            raise serializers.ValidationError(
                {'image': 'Обязательное поле'}
            )
        return image

    def create_amount_ingredients(self, recipe, ingredients):
        """Создание ингредиентов."""
        AmountIngredient.objects.bulk_create(
            AmountIngredient(
                recipe=recipe,
                ingredient_id=ingredient['id'],
                amount=ingredient['amount']
            ) for ingredient in ingredients
        )

    @transaction.atomic
    def create(self, validated_data):
        """Создание рецепта."""
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe = super().create(
            {
                **validated_data,
                'author': self.context['request'].user
            }
        )
        recipe.tags.set(tags_data)
        self.create_amount_ingredients(recipe, ingredients_data)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        """Обновление рецепта."""
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        # спасибо. действительно применял .clear() не к тому полю,
        # запутался в именах указателей.
        instance.ingredients.clear()
        self.create_amount_ingredients(instance, ingredients_data)
        instance.tags.set(tags_data)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """Представление рецепта."""
        return RecipeSerializer(instance, context=self.context).data


class SummaryRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецепта."""

    class Meta:
        """Мета класс."""

        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class SubscribeSerializer(UserSerializer):
    """Сериализатор подписки."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source='recipes.count',
        read_only=True
    )
    is_subscribed = serializers.BooleanField(default=False)

    class Meta(UserSerializer.Meta):
        """Мета класс."""

        fields = (
            *UserSerializer.Meta.fields,
            'recipes',
            'recipes_count'
        )

    def get_recipes(self, user):
        """Получение рецептов."""
        return SummaryRecipeSerializer(
            user.recipes.all()[
                :int(self.context.get(
                    'request'
                ).query_params.get('recipes_limit', 10**10))
            ], many=True
        ).data
