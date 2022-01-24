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
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from django.db.models import Q

from .adapters import adapt_user_queryset_to_dict, adapt_user_queryset_to_list, adapt_profile_queryset_to_list
from ..models import User, DoctorProfile, Tag, Expertise

PAGINATE_BY = 12


def name_query(key):
    query = Q(fullname__icontains=key) | Q(first_name__icontains=key) | \
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


class SearchDoctorsWithTag(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, keyword):
        expertises = Expertise.objects.filter(tag__title__iexact=keyword.replace(" ", "_"))
        if len(expertises) == 0:
            return Response({"success": False, "message": "There is no doctors with the expertise."},
                            status=status.HTTP_404_NOT_FOUND)

        doctorProfiles = expertises.values_list('doctor_id', flat=True)
        result = adapt_user_queryset_to_list(
            User.objects.filter(is_doctor=True).filter(doctorprofile__in=doctorProfiles))

        page = int(request.GET.get('page', 1))
        paginator = Paginator(result, PAGINATE_BY)
        max_page = paginator.num_pages
        if max_page < page or page < 1:
            return Response({"success": False, "message": "Page not found", "max_page": max_page}
                            , status=status.HTTP_404_NOT_FOUND)

        result = paginator.page(page).object_list
        return Response({"success": True, "doctors": result, 'max_page': max_page}, status=status.HTTP_200_OK)


class AdvancedSearch(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        name = request.GET.get('name', '')
        tags = request.GET.get('tags', '')
        sex = request.GET.get('sex', '')
        sort_key = request.GET.get('sort', '')
        reverse = bool(request.GET.get('reverse', 0))

        result = []

        if name != '':
            result = self.filter_by_name(name)

        if tags != '':
            filtered_by_tag = self.filter_by_tag(tags)
            result = self.attach_new_results(result, filtered_by_tag)

        if sex != '':
            filtered_by_sex = self.filter_by_sex(sex)
            result = self.attach_new_results(result, filtered_by_sex)

        if sort_key != '':
            result.sort(key=lambda k: k[sort_key], reverse=reverse)

        page = int(request.GET.get('page', '1'))
        paginator = Paginator(result, PAGINATE_BY)
        max_page = paginator.num_pages
        if max_page < page or page < 1:
            return Response({"success": False, "message": "Page not found"}, status=status.HTTP_404_NOT_FOUND)
        result = paginator.page(page).object_list

        return Response({"success": True, "doctors": result, "page": page, "max_page": max_page},
                        status=status.HTTP_200_OK)

    def attach_new_results(self, result, new_results):
        if not len(result):
            return new_results
        return [item for item in result if item in new_results]

    def filter_by_name(self, name):
        result = User.objects.filter(is_doctor=True).filter(name_query(name))
        return adapt_user_queryset_to_list(result)

    def filter_by_tag(self, tags):
        tags = tags.split(',')
        doctorProfiles = Expertise.objects.filter(tag__title__in=tags).values_list('doctor_id', flat=True)
        users = User.objects.filter(is_doctor=True).filter(doctorprofile__in=doctorProfiles)
        return adapt_user_queryset_to_list(users)

    def filter_by_sex(self, sex):
        users = User.objects.filter(is_doctor=True, sex=sex)
        return adapt_user_queryset_to_list(users)
