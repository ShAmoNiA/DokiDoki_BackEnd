from django.shortcuts import render

from ..models import User
from ..serializers import *


def result_page(request, result):
    return render(request, 'result.html', context={'result': result})


def get_profile_serializer(user):
    if user.is_doctor:
        return DoctorProfileSerializer
    return PatientProfileSerializer


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


def first_n_items_if_exists(the_list, n):
    if len(the_list) < n:
        return the_list
    return the_list[:n]
