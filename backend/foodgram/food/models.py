# flake8: noqa
from django.contrib.auth.models import AbstractUser
from django.core import validators
from django.db import models


MAX_EMAIL_LENGTH = 254
MAX_NAME_LENGTH = 128
MAX_RECIPE_NAME_LENGTH = 256
MAX_SLUG_LENGTH = 32
MAX_USERNAME_LENGTH = 150
MIN_AMOUNT = 1
MIN_COOKING_TIME = 1


class User(AbstractUser):
    username = models.CharField(
        'Логин', max_length=MAX_USERNAME_LENGTH, unique=True,
        validators=[
            validators.RegexValidator(
                r'^[\w.@+-]+$', 'Введите корректное логин'
            ),
        ]
    )
    first_name = models.CharField(
        'Имя', max_length=MAX_USERNAME_LENGTH
    )
    last_name = models.CharField(
        'Фамилия', max_length=MAX_USERNAME_LENGTH
    )
    email = models.EmailField(
        'Электронная почта', unique=True, max_length=MAX_EMAIL_LENGTH
    )
    avatar = models.ImageField(
        'Аватар', upload_to='users/', null=True, default=None
    )
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'password']
    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('email',)


class Ingredient(models.Model):
    name = models.CharField('Название', max_length=MAX_NAME_LENGTH)
    measurement_unit = models.CharField(
        'Единица измерения', max_length=MAX_NAME_LENGTH
    )

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'], name='unique_ingredient'
            )
        ]
        ordering = ('name',)

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Tag(models.Model):
    name = models.CharField(
        'Имя тэга', max_length=MAX_NAME_LENGTH, unique=True
    )
    slug = models.SlugField(
        'Слаг', unique=True, max_length=MAX_SLUG_LENGTH
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField('Название', max_length=MAX_RECIPE_NAME_LENGTH)
    text = models.TextField('Описание')
    cooking_time = models.IntegerField(
        'Время приготовления',
        validators=[validators.MinValueValidator(MIN_COOKING_TIME)]
    )
    ingredients = models.ManyToManyField(
        Ingredient, through='AmountIngredient', related_name='recipes',
        verbose_name='Продукты'
    )
    tags = models.ManyToManyField(
        Tag, related_name='recipes', verbose_name='Тэги'
    )
    image = models.ImageField('Изображение', upload_to='recipes/images/')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes',
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField('Время публикации', auto_now_add=True)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class AmountIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='amounts',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name='amounts',
        verbose_name='Продукт'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество', validators=[validators.MinValueValidator(MIN_AMOUNT)]
    )

    class Meta:
        verbose_name = 'Количество продукта'
        verbose_name_plural = 'Количество продуктов'

    def __str__(self):
        return f'{self.ingredient} - {self.amount}'


class Subscription(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Пользователь',
        related_name='subscribers'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Автор',
        related_name='authors'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique_subscription'
            )
        ]

    def __str__(self):
        return f'{self.user} - {self.author}'


class AbstractRecipeUserModel(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='%(class)ss',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='%(class)ss',
        verbose_name='Рецепт'
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='%(class)s_unique_user_recipe'
            )
        ]

    def __str__(self):
        return f'{self.user} - {self.recipe}'


class Favorite(AbstractRecipeUserModel):

    class Meta(AbstractRecipeUserModel.Meta):
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class ShoppingCart(AbstractRecipeUserModel):

    class Meta(AbstractRecipeUserModel.Meta):
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
