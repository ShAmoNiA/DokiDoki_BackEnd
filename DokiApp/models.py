from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    is_doctor = models.BooleanField(default=False)

    username = models.CharField(unique=True, max_length=64)
    email = models.EmailField(unique=True)
    phone = models.CharField(unique=True, max_length=20, blank=True, null=True)
    fullname = models.CharField(max_length=100, blank=True)

    verify_email_token = models.CharField(max_length=64, default="default")

    @property
    def verified_email(self):
        if self.verify_email_token == "verified":
            return True
        return False

    def verify_email(self):
        self.verify_email_token = "verified"
        self.save()

    @property
    def is_patient(self):
        return not self.is_doctor
