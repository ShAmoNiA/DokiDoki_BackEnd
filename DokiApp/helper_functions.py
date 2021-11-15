from django.shortcuts import render

from .models import User
from .serializers import *


def result_page(request, result):
    return render(request, 'result.html', context={'result': result})


def entity_adapter(query_set, serializer_class):
    result = dict({})
    for item in query_set:
        user_serializer = serializer_class(instance=item)
        data = user_serializer.data
        result[item.id] = data
    return result


def profile_to_user_adapter(query_set):
    IDs = []
    users = User.objects.all()
    for user in users:
        if user.profile in query_set:
            IDs.append(user.id)
    return User.objects.filter(id__in=IDs)


def doctor_profile_adapter(user):
    user_serializer = UserSerializer(instance=user)
    profile = user.profile

    data = user_serializer.data

    data["degree"] = profile.degree
    data["medical_degree_photo"] = profile.medical_degree_photo
    data["cv"] = profile.cv
    data["office_location"] = profile.office_location
    data["expertise_tags"] = profile.expertise_tags
    return data


def patient_profile_adapter(user):
    user_serializer = UserSerializer(instance=user)
    profile = user.profile

    data = user_serializer.data

    data["weight"] = profile.weight
    data["height"] = profile.height
    data["medical_records"] = profile.medical_records
    return data


def pop_dangerous_keys(request):
    dangerous_keys = ['password', 'username', 'email', 'is_doctor', 'user',
                      'reset_password_token', 'verify_email_token']

    request.data._mutable = True
    data = request.data
    for key in dangerous_keys:
        if key in data.keys():
            data.pop(key)

    return data


def get_profile_serializer(user):
    if user.is_doctor:
        return DoctorProfileSerializer
    return PatientProfileSerializer
