from secrets import token_hex
from re import search as validateRegex

from rest_framework.serializers import ModelSerializer, ValidationError
from .models import *

from .email_functions import send_verification_email

from .string_validator import *


class ImageSerializer(ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'is_doctor', 'phone', 'fullname', 'sex')

    def validate_username(self, username):
        if is_valid_username(username):
            return username
        raise ValidationError('username is invalid')

    def validate_password(self, password):
        if is_hard_password(password):
            return password
        raise ValidationError('Password is too short')

    def validate_email(self, email):
        if is_valid_email(email):
            return email
        # raise ValidationError('Invalid email')

    def validate_phone(self, phone):
        if is_valid_phone_number(phone):
            return phone
        raise ValidationError('Invalid phone number')

    def set_profile(self, user):
        is_doctor = user.is_doctor
        if is_doctor:
            DoctorProfile.objects.create(user=user)
        else:
            PatientProfile.objects.create(user=user)

    def create(self, validated_data):
        user = super().create(validated_data)
        user.verify_email_token = token_hex(64)
        user.set_password(validated_data['password'])
        self.set_profile(user)
        user.save()

        send_verification_email(user)
        return user


class DoctorProfileSerializer(ModelSerializer):
    class Meta:
        model = DoctorProfile
        fields = ('user', 'degree', 'medical_degree_photo', 'cv', 'office_location', 'expertise_tags')


class PatientProfileSerializer(ModelSerializer):
    class Meta:
        model = PatientProfile
        fields = ('user', 'weight', 'height', 'medical_records')

    def validate_height(self, height):
        if height < 25 or height > 270:
            raise ValidationError("Enter height in centimeters")
        else:
            return height

    def validate_weight(self, weight):
        if weight < 20 or weight > 500:
            raise ValidationError("Enter Weight in kilogram")
        else:
            return weight


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = ('title',)

    def validate_title(self, title):
        if " " in title or title == "":
            raise ValidationError('Invalid title')
        return title
