"""
contains:
    AllTags
    SearchDoctorByName
    SearchDoctorByTag
    SearchDoctorByKeyword
    SearchDoctorsWithTag
    AdvancedSearch
"""


from django.core.paginator import Paginator
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


PAGINATE_BY = 12


def name_query(key):
    query = Q(fullname__icontains=key) | Q(first_name__icontains=key) |\
            Q(last_name__icontains=key) | Q(username__icontains=key)
    return query


def search_doctor_by_expertises(key, want_users=False):
    if key == "":
        return DoctorProfile.objects.all()

    doctor_ids = Expertise.objects.filter(tag__title__in=key.split()).values_list('doctor_id', flat=True)
    profiles = DoctorProfile.objects.filter(id__in=list(doctor_ids))

    if want_users:
        user_ids = profiles.values_list('user_id', flat=True)
        return User.objects.filter(id__in=list(user_ids))

    return profiles


class AllTags(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        tags = Tag.objects.all().values_list('title', flat=True)
        result = " ".join(tags)

        return Response({"success": True, "tags": result}, status=status.HTTP_200_OK)


class SearchDoctorByName(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        key = request.data["key"]

        doctors = User.objects.filter(is_doctor=True).filter(name_query(key))
        result = adapt_user_queryset_to_dict(doctors)

        return Response({"success": True, "doctors": result}, status=status.HTTP_200_OK)


class SearchDoctorByTag(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        key = request.data["key"]
        profiles = search_doctor_by_expertises(key)

        return Response({"success": True, "doctors": adapt_profile_queryset_to_list(profiles)},
                        status=status.HTTP_200_OK)


class SearchDoctorByKeyword(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, keyword):
        name_result = User.objects.filter(is_doctor=True).filter(name_query(keyword))
        tag_result = search_doctor_by_expertises(keyword, want_users=True)

        result = list(chain(name_result, tag_result))
        result = adapt_user_queryset_to_list(result)
        result = first_twelve_items_if_exists(result)

        return Response({"success": True, "doctors": result}, status=status.HTTP_200_OK)


class SearchDoctorsWithTag(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, keyword):
        result = search_doctor_by_expertises(keyword, want_users=True)
        result = adapt_user_queryset_to_list(result)

        page = int(request.GET.get('page', 1))
        paginator = Paginator(result, PAGINATE_BY)
        if paginator.num_pages < page or page < 1:
            return Response({"success": False, "message": "Page not found"}, status=status.HTTP_404_NOT_FOUND)
        result = paginator.page(page).object_list

        return Response({"success": True, "doctors": result}, status=status.HTTP_200_OK)


class AdvancedSearch(APIView):

    def get(self, request):
        tags = request.GET.get('tags', '')
        name = request.GET.get('name', '')
        sex = request.GET.get('sex', '')
        page = int(request.GET.get('page', 1))
        sort = request.GET.get('sort', '')
        reverse = request.GET.get('reverse', False)

        result = search_doctor_by_expertises(tags.split(','), want_users=True)
        result = result.filter(name_query(name))
        result = result.filter(sex=sex)
        result = adapt_user_queryset_to_list(result)
        if sort != '':
            result.sort(key=lambda k: k[sort], reverse=reverse)

        paginator = Paginator(result, PAGINATE_BY)
        if paginator.num_pages < page or page < 1:
            return Response({"success": False, "message": "Page not found"}, status=status.HTTP_404_NOT_FOUND)
        result = paginator.page(page).object_list

        return Response({"success": True, "doctors": result, "page": page, "max_page": paginator.num_pages},
                        status=status.HTTP_200_OK)
