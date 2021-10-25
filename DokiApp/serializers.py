from secrets import token_hex
from re import search as validateRegex

from rest_framework.serializers import ModelSerializer, ValidationError
from .models import User


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'is_doctor', 'phone', 'fullname')

    def validate_password(self, password):
        if len(password) < 5:
            raise ValidationError('Password is too short')
        return password

    def validate_email(self, email):
        EMAIL_REGEX = r'^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'
        if validateRegex(EMAIL_REGEX, email):
            return email
        raise ValidationError('Invalid email')

    def validate_phone(self, phone):
        PHONE_REGEX = r'^(0|0098|\+98)9\d{9}$'
        if validateRegex(PHONE_REGEX, phone):
            return phone
        raise ValidationError('Invalid phone number')

    def create(self, validated_data):
        user = super().create(validated_data)
        user.verify_email_token = token_hex(64)
        user.set_password(validated_data['password'])
        user.save()

        # self.send_verification_email(user)
        return user

    # def send_verification_email(self, user):
    #     email = user.email
    #     send_email(email)
