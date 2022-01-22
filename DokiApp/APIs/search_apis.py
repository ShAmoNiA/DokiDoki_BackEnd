"""
contains:
    AllTags
    SearchDoctorByName
    SearchDoctorByTag
"""
import math

from django.core.paginator import Paginator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from django.db.models import Q

from ..Helper_functions.adapters import *
from ..serializers import *


def name_query(key):
    query = Q(fullname__icontains=key) | Q(first_name__icontains=key) |\
            Q(last_name__icontains=key) | Q(username__icontains=key)
    return query


class AllTags(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        tags = Tag.objects.all().values_list('title', flat=True)

        result = ""
        for tag in tags:
            result += tag + " "
        return Response({"success": True, "tags": result[:-1]}, status=status.HTTP_200_OK)


class SearchDoctorByName(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        key = request.data["key"]
        search_query = Q(fullname__icontains=key) | Q(first_name__icontains=key) | Q(last_name__icontains=key)
        doctors = User.objects.filter(is_doctor=True).filter(search_query)

        result = adapt_user_queryset_to_dict(doctors)

        return Response({"success": True, "doctors": result}, status=status.HTTP_200_OK)


class SearchDoctorByTag(APIView):
    permission_classes = (AllowAny,)

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
    permission_classes = (AllowAny,)

    def get(self, request, keyword):
        result = User.objects.filter(is_doctor=True).filter(name_query(keyword))
        result = adapt_user_queryset_to_list(result)

        expertises = Expertise.objects.filter(tag__title__icontains=keyword.replace(" ", "_"))
        doctor_profiles = expertises.values_list('doctor_id', flat=True)
        contains_tags = adapt_user_queryset_to_list(
            User.objects.filter(is_doctor=True).filter(doctorprofile__in=doctor_profiles))

        for k in contains_tags:
            if k not in result:
                result.append(k)

        return Response({"success": True, "doctors": result[0:12]}, status=status.HTTP_200_OK)


class DoctorsWithTag(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, keyword):
        expertises = Expertise.objects.filter(tag__title__iexact=keyword.replace(" ", "_"))
        doctor_profiles = expertises.values_list('doctor_id', flat=True)
        result = adapt_user_queryset_to_list(
            User.objects.filter(is_doctor=True).filter(doctorprofile__in=doctor_profiles))

        page = int(request.GET.get('page', '1'))
        paginator = Paginator(result, 12)
        page_max = math.ceil(len(result) / 12)
        if page_max < page or page < 1:
            return Response({"success": False, "message": "Page not found"}, status=status.HTTP_404_NOT_FOUND)
        result = paginator.page(page).object_list

        return Response({"success": True, "doctors": result}, status=status.HTTP_200_OK)


class AdvancedSearch(APIView):

    def get(self, request):
        result = []
        name = request.GET.get('name', '')
        if name != '':
            result = User.objects.filter(is_doctor=True).filter(name_query(name))

            result = adapt_user_queryset_to_list(result)

        tags = request.GET.get('tags', '')
        if tags != '':
            tags = tags.split(',')
            expertises = Expertise.objects.filter(tag__title__in=tags)
            doctor_profiles = expertises.values_list('doctor_id', flat=True)
            contains_tags = adapt_user_queryset_to_list(
                User.objects.filter(is_doctor=True).filter(doctorprofile__in=doctor_profiles))
            if len(result) == 0:
                result = contains_tags
            else:
                result = [item for item in result if item in contains_tags]

        sex = request.GET.get('sex', '')
        if sex != '':
            sex_filter = User.objects.filter(is_doctor=True, sex=sex)
            sex_filter = adapt_user_queryset_to_list(sex_filter)
            if len(result) == 0:
                result = sex_filter
            else:
                result = [item for item in result if item in sex_filter]

        sort = request.GET.get('sort', '')
        if sort != '':
            reverse = request.GET.get('reverse', 'False')
            reverse = True if reverse == 'True' else False
            result.sort(key=lambda k: k[sort], reverse=reverse)

        page = int(request.GET.get('page', '1'))
        paginator = Paginator(result, 12)
        page_max = math.ceil(len(result) / 12)
        if page_max < page or page < 1:
            return Response({"success": False, "message": "Page not found"}, status=status.HTTP_404_NOT_FOUND)
        result = paginator.page(page).object_list

        return Response({"success": True, "doctors": result, "page": page, "max_page": page_max},
                        status=status.HTTP_200_OK)
