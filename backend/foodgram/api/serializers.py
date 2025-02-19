# flake8: noqa
from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer as DjoserUserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from food.models import (
    MIN_AMOUNT,
    MIN_COOKING_TIME,
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
    avatar = Base64ImageField(required=True, allow_null=False)

    class Meta:
        model = User
        fields = ('avatar',)


class UserSerializer(DjoserUserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    avatar = Base64ImageField(read_only=True)

    class Meta(DjoserUserSerializer.Meta):
        fields = (
            *DjoserUserSerializer.Meta.fields,
            'avatar',
            'is_subscribed'
        )

    def get_is_subscribed(self, author):
        user = self.context.get('request').user
        if user.is_authenticated is False:
            return False
        return Subscription.objects.filter(
            user=user,
            author=author
        ).exists()


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class AmountIngredientSerializer(serializers.ModelSerializer):
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

    class Meta:
        model = AmountIngredient
        fields = ('id', 'amount')

    def to_representation(self, instance):
        return {
            'id': instance.ingredient.id,
            'name': instance.ingredient.name,
            'measurement_unit': instance.ingredient.measurement_unit,
            'amount': instance.amount
        }


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = AmountIngredientSerializer(
        many=True,
        source='amounts'
    )
    author = UserSerializer()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_is_favorited(self, recipe):
        request = self.context.get('request')
        if request.user.is_authenticated is False:
            return False
        return Favorite.objects.filter(
            user=request.user,
            recipe=recipe
        ).exists()

    def get_is_in_shopping_cart(self, recipe):
        request = self.context.get('request')
        if request.user.is_authenticated is False:
            return False
        return ShoppingCart.objects.filter(
            user=request.user,
            recipe=recipe
        ).exists()


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    ingredients = AmountIngredientSerializer(
        many=True, required=True, allow_empty=False
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, allow_empty=False
    )
    image = Base64ImageField(required=True, allow_null=False)
    cooking_time = serializers.IntegerField(min_value=MIN_COOKING_TIME)

    class Meta:
        model = Recipe
        fields = (
            'author',
            'cooking_time',
            'image',
            'ingredients',
            'name',
            'tags',
            'text'
        )
        read_only_fields = ('author',)

    def validate(self, data):
        for field in ('ingredients', 'tags', 'image'):
            if not data.get(field):
                raise serializers.ValidationError(
                    {field: f'{field.capitalize()} обязательны'}
                )
        print(data['ingredients'])
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

    def create_amount_ingredients(self, recipe, ingredients):
        AmountIngredient.objects.bulk_create(
            AmountIngredient(
                recipe=recipe,
                ingredient_id=ingredient['id'],
                amount=ingredient['amount']
            ) for ingredient in ingredients
        )

    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe = super().create(validated_data)
        recipe.tags.set(tags_data)
        self.create_amount_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        instance.amounts.all().delete()
        self.create_amount_ingredients(instance, ingredients_data)
        instance.tags.set(tags_data)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeSerializer(instance, context=self.context).data


class SummaryRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class SubscribeSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source='recipes.count',
        read_only=True
    )
    is_subscribed = serializers.BooleanField(default=False)

    class Meta(UserSerializer.Meta):
        fields = (
            *UserSerializer.Meta.fields,
            'recipes',
            'recipes_count'
        )

    def get_recipes(self, user):
        return SummaryRecipeSerializer(
            user.recipes.all()[
                :int(self.context.get(
                    'request'
                ).query_params.get('recipes_limit', 10**10))
            ], many=True
        ).data
