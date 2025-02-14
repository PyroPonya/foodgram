# flake8: noqa
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

User = get_user_model()


class Command(BaseCommand):

    def handle(self, *args, **options):
        username = os.getenv('ADMIN_USERNAME', 'admin')
        email = os.getenv('ADMIN_email', 'admin@email.test')
        password = os.getenv('ADMIN_PASSWORD', 'admin')

        if not User.objects.filter(username=username).exists():
            print('Creating account for %s (%s)' % (username, email))
            admin = User.objects.create_superuser(
                email=email, username=username, password=password)
        else:
            print('Admin account has already been initialized.')
