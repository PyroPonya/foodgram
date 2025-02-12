# flake8: noqa
import csv

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from food.models import Ingredient, Tag

User = get_user_model()


class Command(BaseCommand):
    """
    Команда для импорта данных из CSV-файлов.
    python manage.py help import_data.
    """
    help = 'Импортирует данные из CSV-файлов'

    def handle(self, *args, **options):
        for model, filename in [
            (Ingredient, 'data/ingredients.csv'),
            (Tag, 'data/tags.csv'),
        ]:
            with open(filename, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    # if 'author' in row:
                    #     row['author'] = User.objects.get(id=row['author'])
                    # if 'category' in row:
                    #     row['category'] = Category.objects.get(
                    #         id=row['category']
                    #     )
                    obj, created = model.objects.get_or_create(**row)
                    if created:
                        obj.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'{model.__name__} импортированы успешно'
                    )
                )
