from datetime import datetime


def get_shopping_cart(shopping_cart):
    """Возвращает текстовое представление списка покупок."""
    return '\n'.join([
        'Время и дата составления списка:',
        '{:%H:%M %d.%m.%Y}'.format(datetime.now()),
        'Список продуктов:',
        *[
            '{}. {} - {} ({})'.format(
                index, ingredient.capitalize(), amount, measurement_unit
            )
            for index, (ingredient, (amount, measurement_unit)) in enumerate(
                {
                    recipe['ingredient_name']: (
                        sum(
                            item['amount'] for item in shopping_cart if item[
                                'ingredient_name'
                            ] == recipe['ingredient_name']
                        ), recipe['measurement_unit']
                    ) for recipe in shopping_cart
                }.items(), start=1
            )
        ],
        'Для следующих рецептов:',
        *{recipe['recipe_name'] for recipe in shopping_cart},
    ])
