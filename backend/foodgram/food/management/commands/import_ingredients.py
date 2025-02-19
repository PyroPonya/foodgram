# flake8: noqa
from django.core.management.base import BaseCommand

from food.models import Ingredient
from .import_data import import_data_from_json


class Command(BaseCommand):
    def handle(self, *args, **options):
        import_data_from_json('data/ingredients.json', Ingredient)
        self.stdout.write(self.style.SUCCESS('Импорт продуктов завершён.'))
