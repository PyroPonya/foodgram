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
        for model, filename in [
            (
                Ingredient,
                'data/ingredients.csv',
            ),
            (
                Tag,
                'data/tags.csv',
            ),
        ]:
            with open(filename, 'r', encoding='utf-8', newline='') as csvfile:
                reader = csv.reader(csvfile)
                data = []
                for row in reader:
                    if model == Ingredient:
                        data.append(
                            model(
                                name=row[0],
                                measurement_unit=row[1],
                            )
                        )
                    else:
                        data.append(
                            model(
                                name=row[0],
                                slug=row[1],
                            )
                        )
                model.objects.bulk_create(data, ignore_conflicts=True)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'{model.__name__} импортированы успешно'
                    )
                )
