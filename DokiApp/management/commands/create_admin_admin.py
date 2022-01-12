from django.core.management.base import BaseCommand, CommandError

from DokiApp.models import User

USERNAME = 'admin'
PASSWORD = 'admin'


def create_superuser(username, password):
    superuser = User.objects.create(
        username=username,
        email=f'{username}@gmail.com',
        is_staff=True,
        is_superuser=True,
        is_active=True,
    )

    superuser.set_password(password)
    superuser.save()


class Command(BaseCommand):
    def handle(self, *args, **options):
        create_superuser(USERNAME, PASSWORD)
        print(f"superuser created ---> (username, password) = ({USERNAME}, {PASSWORD})")
