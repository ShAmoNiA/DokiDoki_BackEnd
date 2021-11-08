from secrets import token_hex

from django.db import models
from django.contrib.auth.models import AbstractUser


class Image(models.Model):
    pass


class User(AbstractUser):
    is_doctor = models.BooleanField(default=False)

    username = models.CharField(unique=True, max_length=64)
    email = models.EmailField(unique=True)
    phone = models.CharField(unique=True, max_length=20, blank=True, null=True)
    fullname = models.CharField(max_length=100, blank=True)

    reset_password_token = models.CharField(max_length=64, default="expired")
    verify_email_token = models.CharField(max_length=64, default="default")
    sex = models.CharField(max_length=1, choices=(('F', 'Female',), ('M', 'Male',), ('U', 'Unsure',),
                                                  ('P', 'Prefer not to say')), default='P')

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


class DoctorProfile(models.Model):
    pass


class PatientProfile(models.Model):
    pass
