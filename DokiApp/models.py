from secrets import token_hex

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Avg


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

    @property
    def is_patient(self):
        return not self.is_doctor

    def verify_email(self):
        self.verify_email_token = "verified"
        self.save()


class DoctorProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    degree = models.CharField(max_length=128, default="general")
    medical_degree_photo = models.CharField(max_length=128, null=True)
    cv = models.TextField(default="default")
    office_location = models.CharField(max_length=128, null=True)

    @property
    def expertise_tags(self):
        tags = Expertise.objects.filter(doctor=self).values_list('tag_id', flat=True)
        result = ''
        for tag_id in tags:
            result += Tag.objects.get(id=tag_id).title + " "
        return result[:-1]

    @property
    def comments_count(self):
        query = Comment.objects.filter(doctor__id=self.pk)
        return len(query)

    @property
    def rate(self):
        rate = Rate.objects.filter(doctor__id=self.pk).aggregate(Avg('rate'))["rate__avg"]
        return rate

    def set_user(self, user):
        if user.has_profile:
            return "The user already has a profile"
        elif user.is_patient:
            return "The user is a patient"
        else:
            self.user = user
            self.save()
            return "the profile set successfully"

    def __str__(self):
        return str(self.id) + ". " + str(self.user.username)


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

    def __str__(self):
        return str(self.id) + ". " + str(self.user.username)


class Tag(models.Model):
    title = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return str(self.id) + ". " + str(self.title)


class Expertise(models.Model):
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    image_url = models.CharField(max_length=512, null=True, blank=True)


class Comment(models.Model):
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE)
    writer = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)


class Rate(models.Model):
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rate = models.IntegerField(range(1, 5))


class Reserve(models.Model):
    TIME_CHOICES = (('AM', 'Before 12',),
                    ('PM', 'After 12',))
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField()
    time = models.CharField(max_length=2, choices=TIME_CHOICES)


class Chat(models.Model):
    name = models.CharField(default="chat_name", unique=True, max_length=32)

    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE)
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE)

    def __str__(self):
        return self.name + " (" + self.doctor.user.username + " & " + self.patient.user.username + ")"


class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)

    text = models.TextField()
    is_sender_doctor = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.chat.doctor.user.username + " & " + self.chat.patient.user.username
