import base64
import datetime as dt

from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.core.files.base import ContentFile
from djoser.serializers import DjoserUserSerializer
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from food.models import Subscription, Ingredient, Tag, Recipe

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(
                base64.b64decode(imgstr),
                name=f'{dt.datetime.now()}.{ext}'
            )
        return super().to_internal_value(data)


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('avatar',)


class UserSerializer(DjoserUserSerializer):
    is_subscribed = serializers.SerializerMethodField(
        'get_is_subscribed',
        read_only=True
    )
    avatar_raw = Base64ImageField(required=False, allow_null=True)
    avatar = serializers.SerializerMethodField('get_avatar')

    class Meta(DjoserUserSerializer.Meta):
        fields = (
            *DjoserUserSerializer.Meta.fields,
            'avatar',
            'is_subscribed',
        )

    def get_is_subscribed(self, author):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=user,
            author=author
        ).exists()

    def get_avatar(self, obj):
        if obj.avatar_raw:
            return obj.avatar_raw.url
        return None


class SubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')

    def to_representation(self, instance):
        context = {'request': self.context['request']}
        return UserSerializer(instance, context=context).data


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ('id', 'user', 'author')


# class RecipeSerializer(serializers.ModelSerializer):
#     image = Base64ImageField(required=False, allow_null=True)

#     class Meta:
#         model = Recipe
#         fields = ('id', 'name', 'image', 'cooking_time')

#     def to_representation(self, instance):
#         context = {'request': self.context['request']}
#         return RecipeSerializer(instance, context=context).data

#     def create(self, validated_data):
#         author = self.context['request'].user
#         tags = validated_data.pop('tags')
#         ingredients = validated_data.pop('ingredients')
#         recipe = Recipe.objects.create(author=author, **validated_data)
#         recipe.tags.set(tags)
#         recipe.ingredients.set(ingredients)
#         return recipe


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('name', 'slug')


class RecipeSerializerRead(serializers.ModelSerializer):
    image = Base64ImageField(required=False, allow_null=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientSerializer(many=True, read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
            'tags',
            'ingredients'
        )


class RecipeSerializerWrite(serializers.ModelSerializer):
    image = Base64ImageField(required=False, allow_null=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all())
    ingredients = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Ingredient.objects.all())

    class Meta:
        model = Recipe
        fields = ('__all__')
