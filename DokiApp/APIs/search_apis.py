"""
contains:
    AllTags
    SearchDoctorByName
    SearchDoctorByTag
"""

from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny

from django.db.models import Q

from ..models import *
from ..Helper_functions.helper_functions import *
from ..Helper_functions.adapters import *
from ..serializers import *
from ..permissions import *
from itertools import chain


class AllTags(APIView):
    permission_classes = (AllowAny, )

    def get(self, request):
        tags = Tag.objects.all().values_list('title', flat=True)

        result = ""
        for tag in tags:
            result += tag + " "
        return Response({"success": True, "tags": result[:-1]}, status=status.HTTP_200_OK)


class SearchDoctorByName(APIView):
    permission_classes = (AllowAny, )

    def post(self, request):
        key = request.data["key"]
        search_query = Q(fullname__icontains=key) | Q(first_name__icontains=key) | Q(last_name__icontains=key)
        doctors = User.objects.filter(is_doctor=True).filter(search_query)

        result = adapt_user_queryset_to_dict(doctors)

        return Response({"success": True, "doctors": result}, status=status.HTTP_200_OK)


class SearchDoctorByTag(APIView):
    permission_classes = (AllowAny, )

    def post(self, request):
        key = request.data["key"]
        profiles = self.filter_doctors_by_expertise(key)

        return Response({"success": True, "doctors": adapt_profile_queryset_to_list(profiles)},
                        status=status.HTTP_200_OK)

    def filter_doctors_by_expertise(self, key):
        if key == "":
            return DoctorProfile.objects.all()

        doctor_ids = Expertise.objects.filter(tag__title__in=key.split()).values_list('doctor_id', flat=True)
        return DoctorProfile.objects.filter(id__in=list(doctor_ids))


class SearchDoctorByKeyword(APIView):
    permission_classes = (AllowAny, )

    def get(self, request,keyword):
        search_query = Q(fullname__icontains=keyword) | Q(first_name__icontains=keyword) | Q(last_name__icontains=keyword) | Q(username__icontains=keyword)
        result = User.objects.filter(is_doctor=True).filter(search_query)
        result = adapt_user_queryset_to_dict(result)

        expertises = Expertise.objects.filter(tag__title__icontains=keyword.replace(" ","_"))
        doctor_profiles = expertises.values_list('doctor_id',flat=True)
        contains_tags = adapt_user_queryset_to_dict(User.objects.filter(is_doctor=True).filter(doctorprofile__in=doctor_profiles))

        for k, v in contains_tags.items():
            if k not in result:
                result[k] = v

        return Response({"success": True, "doctors": result}, status=status.HTTP_200_OK)


class DoctorsWithTag(APIView):
    permission_classes = (AllowAny, )

    def get(self, request,keyword):
        expertises = Expertise.objects.filter(tag__title__iexact=keyword.replace(" ","_"))
        doctor_profiles = expertises.values_list('doctor_id',flat=True)
        contains_tags = adapt_user_queryset_to_dict(User.objects.filter(is_doctor=True).filter(doctorprofile__in=doctor_profiles))
        return Response({"success": True, "doctors": contains_tags}, status=status.HTTP_200_OK)


class AdvancedSearch(APIView):

    def get(self, request):
        result = []
        name = request.GET.get('name', '')
        if name != '':
            search_query = Q(fullname__icontains=name) | Q(first_name__icontains=name) | Q(last_name__icontains=name) | Q(username__icontains=name)
            result = User.objects.filter(is_doctor=True).filter(search_query)

            result = adapt_user_queryset_to_list(result)

        tags = request.GET.get('tags', '')
        if tags != '':
            tags = tags.split(',')
            expertises = Expertise.objects.filter(tag__title__in=tags)
            doctor_profiles = expertises.values_list('doctor_id', flat=True)
            contains_tags = adapt_user_queryset_to_list(User.objects.filter(is_doctor=True).filter(doctorprofile__in=doctor_profiles))
            if len(result) == 0:
                result = contains_tags
            else:
                result = [item for item in result if item in contains_tags]



        sex = request.GET.get('sex', '')
        if sex != '':
            sex_filter = User.objects.filter(is_doctor=True,sex=sex)
            sex_filter = adapt_user_queryset_to_list(sex_filter)
            if len(result) == 0:
                result = sex_filter
            else:
                result = [item for item in result if item in contains_tags]

        sort = request.GET.get('sort','')
        if sort != '':
            result.sort(key=lambda k : k[sort])

        return Response({"success": True, "doctors": result}, status=status.HTTP_200_OK)

