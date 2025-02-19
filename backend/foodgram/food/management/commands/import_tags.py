# flake8: noqa
from django.core.management.base import BaseCommand

from food.models import Tag
from .import_data import import_data_from_json


class Command(BaseCommand):
    def handle(self, *args, **options):
        import_data_from_json('data/tags.json', Tag)
        self.stdout.write(self.style.SUCCESS('Импорт тэгов завершён.'))
