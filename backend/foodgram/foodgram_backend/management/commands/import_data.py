import csv

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from reviews.models import (
    Category, Comment, Genre, Review, Title,
)

User = get_user_model()


class Command(BaseCommand):
    """
    Команда для импорта данных из CSV-файлов.
    python manage.py help import_data.
    """
    help = 'Импортирует данные из CSV-файлов'

    def handle(self, *args, **options):
        for model, filename in [
            (User, 'static/data/users.csv'),
            (Category, 'static/data/category.csv'),
            (Genre, 'static/data/genre.csv'),
            (Title, 'static/data/titles.csv'),
            (Review, 'static/data/review.csv'),
            (Comment, 'static/data/comments.csv'),
        ]:
            with open(filename, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if 'author' in row:
                        row['author'] = User.objects.get(id=row['author'])
                    if 'category' in row:
                        row['category'] = Category.objects.get(
                            id=row['category']
                        )
                    obj, created = model.objects.get_or_create(**row)
                    if created:
                        obj.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'{model.__name__} импортированы успешно'
                    )
                )
