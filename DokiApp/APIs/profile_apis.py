"""
contains:
    ProfilePreview
    MyProfilePreview
    EditProfile
    AddExpertise
"""

import os

from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from rest_framework.permissions import IsAuthenticated, AllowAny
from ..permissions import IsDoctor

from .adapters import ProfileAdapter
from ..serializers import UserSerializer, DoctorProfileSerializer, PatientProfileSerializer
from ..models import User, Image, Tag, Expertise


class ProfilePreview(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        username = request.GET['username']
        user = get_object_or_404(User, username=username)

        profile = self.get_adapted_and_filtered_profile(user)
        return Response({"success": True, "profile": profile}, status=status.HTTP_200_OK)

    def get_adapted_and_filtered_profile(self, user):
        profile = ProfileAdapter().adapt_profile(user)
        return self.filter_private_profile_fields(profile)

    def filter_private_profile_fields(self, profile):
        profile.pop("phone")
        return profile


class MyProfilePreview(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        profile = ProfileAdapter().adapt_profile(user)

        return Response({"success": True, "profile": profile}, status=status.HTTP_200_OK)


class EditProfile(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = request.user
        data = self.pop_dangerous_keys(request)

        self.delete_old_picture(user, data)
        self.save_changes(user, data)

        return Response({"success": True, "message": "Profile changed successfully"}, status=status.HTTP_200_OK)

    def pop_dangerous_keys(self, request):
        dangerous_keys = ['password', 'username', 'email', 'is_doctor', 'user',
                          'reset_password_token', 'verify_email_token']

        try:
            # This will be run for tests:
            request.data._mutable = True
        except:
            pass

        data = request.data
        for key in dangerous_keys:
            if key in data.keys():
                data.pop(key)

        return data

    def delete_old_picture(self, user, data):
        if ('profile_picture_url' in data) and (data['profile_picture_url'] != user.profile_picture_url):
            Image.objects.get(image=user.profile_picture_url).delete()
            os.remove(os.getcwd() + "/static/images/" + user.profile_picture_url)

    def save_changes(self, user, data):
        serializer = self.get_profile_serializer(user)(user.profile, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        serializer = UserSerializer(user, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

    def get_profile_serializer(self, user):
        if user.is_doctor:
            return DoctorProfileSerializer
        return PatientProfileSerializer


class AddExpertise(APIView):
    permission_classes = (IsAuthenticated, IsDoctor)

    def post(self, request):
        image_url = request.data["image_url"]
        tag = request.data["tag"]

        tag = get_object_or_404(Tag, title=tag)
        profile = request.user.profile

        if Expertise.objects.filter(tag=tag, doctor=profile).count():
            return Response({"success": True, "message": "You have recorded the expertise before"},
                            status=status.HTTP_200_OK)

        Expertise.objects.create(tag=tag, image_url=image_url, doctor=profile)
        return Response({"success": True, "message": "Expertise saved successfully"}, status=status.HTTP_200_OK)
