from django.core.management.base import BaseCommand, CommandError

from DokiApp.models import User


PASSWORD = '12345678'


def set_password(password):
    for user in User.objects.all():
        user.set_password(password)
        user.save()


class Command(BaseCommand):
    def handle(self, *args, **options):
        set_password(PASSWORD)
        print(f"user passwords set as: {PASSWORD}")
