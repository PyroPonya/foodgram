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
        'Логин',
        max_length=MAX_USERNAME_LENGTH,
        unique=True,
        validators=[
            validators.RegexValidator(
                r'^[\w.@+-]+$', 'Введите корректное логин'
            ),
        ]
    )
    first_name = models.CharField(
        'Имя',
        max_length=MAX_USERNAME_LENGTH
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=MAX_USERNAME_LENGTH
    )
    email = models.EmailField(
        'Электронная почта',
        unique=True,
        max_length=MAX_EMAIL_LENGTH
    )
    avatar = models.ImageField(
        'Аватар',
        upload_to='users/',
        null=True, default=None
    )
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name',
        'password'
    )
    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('email',)


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='authors',
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription',
            )
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='название',
        max_length=MAX_NAME_LENGTH,
    )
    measurement_unit = models.CharField(
        verbose_name='единица измерения',
        max_length=MAX_NAME_LENGTH,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient',
            )
        ]


class Tag(models.Model):
    name = models.CharField(
        verbose_name='название',
        max_length=MAX_SLUG_LENGTH,
        unique=True,
    )
    slug = models.SlugField(
        verbose_name='slug',
        max_length=MAX_SLUG_LENGTH,
        unique=True,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='автор',
        related_name='recipes',
    )
    name = models.CharField(
        verbose_name='название',
        max_length=MAX_RECIPE_NAME_LENGTH,
    )
    image = models.ImageField(
        verbose_name='картинка',
        upload_to='food/images/',
    )
    text = models.TextField(
        verbose_name='описание',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='AmountIngredient',
        verbose_name='ингредиенты',
        related_name='recipes',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='теги',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='время приготовления',
        validators=[
            validators.MinValueValidator(
                MIN_COOKING_TIME,
                f'Время приготовления должно быть не менее {MIN_COOKING_TIME} минут',
            ),
        ]
    )
    pub_date = models.DateTimeField(
        verbose_name='дата публикации',
        auto_now_add=True,
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class AmountIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='рецепт',
        related_name='amounts',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='ингредиент',
        related_name='amounts',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='количество',
        validators=[
            validators.MinValueValidator(
                MIN_AMOUNT,
                f'Количество ингредиента должно быть не менее {MIN_AMOUNT}',
            ),
        ]
    )

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'

    def __str__(self):
        return f'{self.ingredient} {self.amount}'


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
        return f'{self.recipe} добавлен в избранное {self.user}'


class Favorite(AbstractRecipeUserModel):

    class Meta(AbstractRecipeUserModel.Meta):
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class ShoppingCart(AbstractRecipeUserModel):

    class Meta(AbstractRecipeUserModel.Meta):
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
