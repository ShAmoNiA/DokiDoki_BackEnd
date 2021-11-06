from secrets import token_hex
from re import search as validateRegex

from rest_framework.serializers import ModelSerializer, ValidationError
from .models import User

from .email_functions import send_verification_email

from .string_validator import *


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'is_doctor', 'phone', 'fullname')

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
        raise ValidationError('Invalid email')

    def validate_phone(self, phone):
        if is_valid_phone_number(phone):
            return phone
        raise ValidationError('Invalid phone number')

    def create(self, validated_data):
        user = super().create(validated_data)
        user.verify_email_token = token_hex(64)
        user.set_password(validated_data['password'])
        user.save()

        send_verification_email(user)
        return user
