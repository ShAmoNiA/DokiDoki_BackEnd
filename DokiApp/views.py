from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from rest_framework.parsers import MultiPartParser
from rest_framework.parsers import FormParser

from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny

from django.db.models import Q

from .models import *
from .helper_functions import *

from .serializers import *

from .APIs.auth_apis import *


@api_view(['POST'])
def send_email_by_front(request):
    subject = request.data["subject"]
    message = request.data["message"]
    to_list = request.data["to_list"]

    to_list = to_list.split(" ")
    send_text_email(subject, message, to_list)

    return Response({"success": True, "message": "email sent"}, status=status.HTTP_200_OK)


class ImageView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        image_serializer = ImageSerializer(data=request.data)
        if image_serializer.is_valid():
            image_serializer.save()
            return Response({"image_url": image_serializer.data["image"]}, status=status.HTTP_200_OK)
        return Response(image_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddTag(APIView):

    def post(self, request):
        tag_serializer = TagSerializer(data=request.data)
        if tag_serializer.is_valid():
            tag_serializer.save()
            return Response({"success": True, "message": "tag added successfully"}, status=status.HTTP_200_OK)

        return Response({"success": False, "message": "tag not added"}, status=status.HTTP_200_OK)


class SearchForTag(APIView):

    def post(self, request):
        key = request.data["key"]
        tags = Tag.objects.filter(title__icontains=key).values_list('title', flat=True)

        result = ""
        for tag in tags:
            result += tag + " "
        return Response({"success": True, "tags": result}, status=status.HTTP_200_OK)


class SearchDoctorByName(APIView):

    def post(self, request):
        key = request.data["key"]
        search_query = Q(fullname__icontains=key) | Q(first_name__icontains=key) | Q(last_name__icontains=key)
        doctors = User.objects.filter(is_doctor=True).filter(search_query)

        doctors_list = entity_adapter(doctors, UserSerializer)
        return Response({"success": True, "doctors": doctors_list}, status=status.HTTP_200_OK)


class SearchDoctorByTag(APIView):

    def post(self, request):
        key = request.data["key"]
        profiles = DoctorProfile.objects.filter(expertise_tags__icontains=key)
        doctors = profile_to_user_adapter(profiles)
        doctors_list = entity_adapter(doctors, UserSerializer)
        return Response({"success": True, "doctors": doctors_list}, status=status.HTTP_200_OK)


class PreviewDoctorProfile(APIView):

    def post(self, request):
        username = request.data["username"]
        user = User.objects.get(username=username)

        profile = doctor_profile_adapter(user)
        return Response({"success": True, "profile": profile}, status=status.HTTP_200_OK)


class PreviewPatientProfile(APIView):

    def post(self, request):
        username = request.data["username"]
        user = User.objects.get(username=username)

        profile = patient_profile_adapter(user)
        return Response({"success": True, "profile": profile}, status=status.HTTP_200_OK)


@api_view(['POST'])
def edit_profile(request):
    if not request.user.is_authenticated:
        return Response({"success": False, "message": "You must login first"}, status=status.HTTP_200_OK)
    user = request.user
    profile = user.get_profile()

    if user.is_doctor:
        serializerClass = DoctorProfileSerializer
    else:
        serializerClass = PatientProfileSerializer

    serializer = serializerClass(profile, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()

    serializer = UserSerializer(request.user, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response({"success": True, "message": "Profile changed successfully"}, status=status.HTTP_200_OK)
