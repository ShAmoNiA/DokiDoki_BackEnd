from django.core.management.base import BaseCommand, CommandError

from DokiApp.models import User


def set_emails_verified():
    for user in User.objects.all():
        user.verify_email()


class Command(BaseCommand):
    def handle(self, *args, **options):
        set_emails_verified()
        print("user emails set as verified")
