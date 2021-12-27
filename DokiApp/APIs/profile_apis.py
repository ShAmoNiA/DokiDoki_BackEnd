"""
contains:
    ProfilePreview
    MyProfilePreview
    EditProfile
    AddExpertise
"""

import os

from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny

from django.shortcuts import get_object_or_404

from ..models import *
from ..Helper_functions.helper_functions import *
from ..Helper_functions.adapters import *
from ..serializers import *
from ..permissions import *


class ProfilePreview(APIView):
    permission_classes = (AllowAny, )

    def get(self, request):
        username = request.GET['username']
        user = get_object_or_404(User, username=username)

        profile = self.get_adapted_and_filtered_profile(user)
        return Response({"success": True, "profile": profile}, status=status.HTTP_200_OK)

    def get_adapted_and_filtered_profile(self, user):
        profile = ProfileAdapter().adapt_profile(user)
        return self.filter_profile(profile)

    def filter_profile(self, profile):
        profile.pop("phone")
        return profile


class MyProfilePreview(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        user = request.user
        profile = ProfileAdapter().adapt_profile(user)

        return Response({"success": True, "profile": profile}, status=status.HTTP_200_OK)


class EditProfile(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        user = request.user
        profile = user.profile

        data = pop_dangerous_keys(request)
        serializerClass = get_profile_serializer(user)

        self.delete_old_picture(user, data)

        serializer = serializerClass(profile, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        serializer = UserSerializer(user, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": True, "message": "Profile changed successfully"}, status=status.HTTP_200_OK)

    def delete_old_picture(self, user, data):
        if ('profile_picture_url' in data) and (data['profile_picture_url'] != user.profile_picture_url):
            Image.objects.get(image=user.profile_picture_url).delete()
            os.remove(os.getcwd() + "/static/images/" + user.profile_picture_url)


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
