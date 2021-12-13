from django.shortcuts import render

from ..models import User
from ..serializers import *


class ProfileAdapter:
    def adapt_profile(self, user):
        if user.is_doctor:
            profile = self.adapt_doctor_profile(user)
        else:
            profile = self.adapt_patient_profile(user)
        return profile

    def adapt_doctor_profile(self, user):
        user_serializer = UserSerializer(instance=user)
        profile = user.profile

        data = user_serializer.data
        data.pop('password')

        data["degree"] = profile.degree
        data["medical_degree_photo"] = profile.medical_degree_photo
        data["cv"] = profile.cv
        data["office_location"] = profile.office_location
        data["expertise_tags"] = profile.expertise_tags
        return data

    def adapt_patient_profile(self, user):
        user_serializer = UserSerializer(instance=user)
        profile = user.profile

        data = user_serializer.data
        data.pop('password')

        data["weight"] = profile.weight
        data["height"] = profile.height
        data["medical_records"] = profile.medical_records
        return data


profileAdapter = ProfileAdapter()


def adapt_profile_queryset_to_list(profiles):
    users = []
    for profile in profiles:
        users.append(profile.user)

    return adapt_user_queryset_to_dict(users)


def adapt_user_queryset_to_dict(users):
    result = {}
    for user in users:
        result[user.id] = profileAdapter.adapt_profile(user)
    return result


def adapt_user_queryset_to_list(users):
    result = []
    for user in users:
        data = profileAdapter.adapt_profile(user)
        data['id'] = user.id
        result.append(data)
    return result
