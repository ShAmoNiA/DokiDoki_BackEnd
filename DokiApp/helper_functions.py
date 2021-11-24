from django.shortcuts import render

from .models import User
from .serializers import *


def result_page(request, result):
    return render(request, 'result.html', context={'result': result})


def adapt_doctor_profiles_to_profile_list(profiles):
    doctors = []
    for profile in profiles:
        doctors.append(profile.user)

    result = {}
    for doctor in doctors:
        result[doctor.id] = doctor_profile_adapter(doctor)
    return result


def adapt_profile_list(users):
    result = {}
    for user in users:
        result[user.id] = adapt_profile(user)
    return result


def adapt_profile(user):
    if user.is_doctor:
        profile = doctor_profile_adapter(user)
    else:
        profile = patient_profile_adapter(user)
    return profile


def doctor_profile_adapter(user):
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


def patient_profile_adapter(user):
    user_serializer = UserSerializer(instance=user)
    profile = user.profile

    data = user_serializer.data
    data.pop('password')

    data["weight"] = profile.weight
    data["height"] = profile.height
    data["medical_records"] = profile.medical_records
    return data


def pop_dangerous_keys(request):
    dangerous_keys = ['password', 'username', 'email', 'is_doctor', 'user',
                      'reset_password_token', 'verify_email_token']

    try:
        # This will be run for tests:
        request.data._mutable = True
    except: pass

    data = request.data
    for key in dangerous_keys:
        if key in data.keys():
            data.pop(key)

    return data


def get_profile_serializer(user):
    if user.is_doctor:
        return DoctorProfileSerializer
    return PatientProfileSerializer
