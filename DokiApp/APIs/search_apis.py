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

        result = adapt_profile_list(doctors)

        return Response({"success": True, "doctors": result}, status=status.HTTP_200_OK)


class SearchDoctorByTag(APIView):
    permission_classes = (AllowAny, )

    def post(self, request):
        key = request.data["key"]
        profiles = self.filter_doctors_by_expertise(key)

        return Response({"success": True, "doctors": adapt_doctor_profiles_to_profile_list(profiles)},
                        status=status.HTTP_200_OK)

    def filter_doctors_by_expertise(self, key):
        if key == "":
            return DoctorProfile.objects.all()

        doctor_ids = Expertise.objects.filter(tag__title__in=key.split()).values_list('doctor_id', flat=True)
        return DoctorProfile.objects.filter(id__in=list(doctor_ids))
