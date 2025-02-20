# flake8: noqa
import csv

from django.core.management.base import BaseCommand

from food.models import Ingredient, Tag


class Command(BaseCommand):
    """
    Команда для импорта данных из CSV-файлов.
    python manage.py help import_data.
    """
    help = 'Импортирует данные из CSV-файлов'

    def handle(self, *args, **options):
        for model, filename, fields in [
            (
                Ingredient,
                'data/ingredients.csv',
                ['name', 'measurement_unit']
            ),
            (
                Tag,
                'data/tags.csv',
                ['name', 'slug']
            ),
        ]:
            with open(filename, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    data = {field: row[field] for field in fields}
                    obj, created = model.objects.get_or_create(**data)
                    if created:
                        obj.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'{model.__name__} импортированы успешно'
                    )
                )
