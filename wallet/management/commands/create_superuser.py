import os

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Создает суперпользователя'

    def handle(self, *args, **kwargs):
        User = get_user_model()
        username = os.environ.get('ADMIN_NAME', default='root')
        email = os.environ.get('ADMIN_EMAIL', default='')
        password = os.environ.get('ADMIN_PASS', default='root')

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS('Суперпользователь создан'))
        else:
            self.stdout.write(self.style.WARNING('Суперпользователь уже существует'))