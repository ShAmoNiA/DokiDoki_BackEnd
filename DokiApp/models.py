from secrets import token_hex

from django.db import models
from django.contrib.auth.models import AbstractUser


class Image(models.Model):
    image = models.ImageField(default="default.png", null=True, blank=True)


class User(AbstractUser):
    SEX_CHOICES = (('F', 'Female',),
                   ('M', 'Male',),
                   ('U', 'Unsure',),
                   ('P', 'Prefer not to say'))

    profile_picture_url = models.CharField(max_length=512, null=True, blank=True)

    username = models.CharField(unique=True, max_length=64)
    email = models.EmailField(unique=True)
    phone = models.CharField(unique=True, max_length=20, blank=True, null=True)
    fullname = models.CharField(max_length=100, blank=True)
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    sex = models.CharField(max_length=1, choices=SEX_CHOICES, default='P')

    reset_password_token = models.CharField(max_length=64, default="expired")
    verify_email_token = models.CharField(max_length=64, default="default")

    is_doctor = models.BooleanField(default=False)

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
    degree = models.CharField(max_length=128, default="general")
    medical_degree_photo = models.CharField(max_length=128, null=True)
    # CV = ?
    office_location = models.CharField(max_length=128, null=True)


class PatientProfile(models.Model):
    weight = models.IntegerField(default=0)
    height = models.IntegerField(default=0)
    medical_records = models.TextField(null=True)
