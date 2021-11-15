from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny

from django.db.models import Q

from ..models import *
from ..helper_functions import *
from ..serializers import *
from ..permissions import *


class AddTag(APIView):
    permission_classes = (IsAuthenticated, IsDoctor)

    def post(self, request):
        tag_serializer = TagSerializer(data=request.data)
        if tag_serializer.is_valid():
            tag_serializer.save()
            return Response({"success": True, "message": "tag added successfully"}, status=status.HTTP_200_OK)

        return Response({"success": False, "message": "tag not added"}, status=status.HTTP_200_OK)


class SearchForTag(APIView):
    permission_classes = (AllowAny, )

    def post(self, request):
        key = request.data["key"]
        tags = Tag.objects.filter(title__icontains=key).values_list('title', flat=True)

        result = ""
        for tag in tags:
            result += tag + " "
        return Response({"success": True, "tags": result}, status=status.HTTP_200_OK)


class SearchDoctorByName(APIView):
    permission_classes = (AllowAny, )

    def post(self, request):
        key = request.data["key"]
        search_query = Q(fullname__icontains=key) | Q(first_name__icontains=key) | Q(last_name__icontains=key)
        doctors = User.objects.filter(is_doctor=True).filter(search_query)

        doctors_list = entity_adapter(doctors, UserSerializer)
        return Response({"success": True, "doctors": doctors_list}, status=status.HTTP_200_OK)


class SearchDoctorByTag(APIView):
    permission_classes = (AllowAny, )

    def post(self, request):
        key = request.data["key"]
        profiles = DoctorProfile.objects.filter(expertise_tags__icontains=key)
        doctors = profile_to_user_adapter(profiles)
        doctors_list = entity_adapter(doctors, UserSerializer)
        return Response({"success": True, "doctors": doctors_list}, status=status.HTTP_200_OK)
