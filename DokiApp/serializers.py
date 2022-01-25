from secrets import token_hex
from re import search as validate_regex

from rest_framework.serializers import ModelSerializer, ValidationError

from .models import *
from .APIs.email_functions import send_verification_email


class StringValidator:
    def is_valid_username(self, text: str):
        username_regex = r'^(?![_.0-9])(?!.*[_.]{2})[a-zA-Z0-9._]+(?<![_.])$'
        return validate_regex(username_regex, text)

    def is_hard_password(self, text: str):
        return len(text) > 7

    def is_valid_phone_number(self, text: str):
        phone_regex = r'^(0|0098|\+98)9\d{9}$'
        return validate_regex(phone_regex, text)


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'is_doctor', 'phone', 'fullname', 'sex', 'profile_picture_url')

    def validate_username(self, username):
        if StringValidator().is_valid_username(username):
            return username
        raise ValidationError('username is invalid')

    def validate_password(self, password):
        if StringValidator().is_hard_password(password):
            return password
        raise ValidationError('Password is too short')

    def validate_phone(self, phone):
        if StringValidator().is_valid_phone_number(phone):
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


class ImageSerializer(ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'


class DoctorProfileSerializer(ModelSerializer):
    class Meta:
        model = DoctorProfile
        fields = ('user', 'degree', 'medical_degree_photo', 'cv', 'office_location')


class PatientProfileSerializer(ModelSerializer):
    class Meta:
        model = PatientProfile
        fields = ('user', 'weight', 'height', 'medical_records')

    def validate_height(self, height):
        if height < 25 or height > 270:
            raise ValidationError("Enter height in centimeters")
        return height

    def validate_weight(self, weight):
        if weight < 20 or weight > 500:
            raise ValidationError("Enter Weight in kilograms")
        return weight


class CommentSerializer(ModelSerializer):
    class Meta:
        model = Comment
        fields = ('writer', 'doctor', 'text', 'date')


class RateSerializer(ModelSerializer):
    class Meta:
        model = Rate
        fields = ('doctor', 'user', 'rate')

    def validate_rate(self, rate):
        rate = int(rate)
        if rate < 1 or rate > 5:
            raise ValidationError("Enter rate between 1 and 5")

        return rate


class ReserveSerializer(ModelSerializer):
    class Meta:
        model = Reserve
        fields = ('doctor', 'creator', 'date', 'time')


class ChatSerializer(ModelSerializer):
    class Meta:
        model = Chat
        fields = ('doctor', 'patient')


class MessageSerializer(ModelSerializer):
    class Meta:
        model = Message
        fields = ('id', 'text', 'seen', 'is_sender_doctor', 'date')
