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
    def profile(self):
        try:
            if self.is_doctor:
                return DoctorProfile.objects.get(user=self)
            else:
                return PatientProfile.objects.get(user=self)
        except:
            return None

    @property
    def has_profile(self):
        if self.is_doctor:
            result = DoctorProfile.objects.filter(user=self).count()
        else:
            result = PatientProfile.objects.filter(user=self).count()
        return bool(result)

    @property
    def verified_email(self):
        return self.verify_email_token == "verified"

    def verify_email(self):
        self.verify_email_token = "verified"
        self.save()

    @property
    def is_patient(self):
        return not self.is_doctor


class DoctorProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    degree = models.CharField(max_length=128, default="general")
    medical_degree_photo = models.CharField(max_length=128, null=True)
    cv = models.TextField(default="default")
    office_location = models.CharField(max_length=128, null=True)

    expertise_tags = models.CharField(max_length=512, default="")

    def set_user(self, user):
        if user.has_profile:
            return "The user already has a profile"
        elif user.is_patient:
            return "The user is a patient"
        else:
            self.user = user
            self.save()
            return "the profile set successfully"


class PatientProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    weight = models.IntegerField(default=0)
    height = models.IntegerField(default=0)
    medical_records = models.TextField(null=True, default="nothing yet")

    def set_user(self, user):
        if user.has_profile:
            return "The user already has a profile"
        elif user.is_doctor:
            return "The user is a doctor"
        else:
            self.user = user
            self.save()
            return "the profile set successfully"


class Tag(models.Model):
    title = models.CharField(max_length=64, unique=True)
