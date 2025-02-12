from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='название',
        max_length=200,
    )
    measurement_unit = models.CharField(
        verbose_name='единица измерения',
        max_length=200,
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
        max_length=200,
        unique=True,
    )
    slug = models.SlugField(
        verbose_name='slug',
        max_length=200,
        unique=True,
    )


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='автор',
        related_name='recipes',
    )
    name = models.CharField(
        verbose_name='название',
        max_length=200,
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
        # through='IngredientAmount',
        verbose_name='ингредиенты',
        related_name='recipes',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='теги',
        related_name='recipes',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='время приготовления',
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name
