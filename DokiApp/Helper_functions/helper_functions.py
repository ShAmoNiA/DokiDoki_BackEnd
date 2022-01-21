from django.shortcuts import render

from ..models import User
from ..serializers import *


def result_page(request, result):
    return render(request, 'result.html', context={'result': result})


def get_profile_serializer(user):
    if user.is_doctor:
        return DoctorProfileSerializer
    return PatientProfileSerializer


def first_n_items_if_exists(the_list, n):
    if len(the_list) < n:
        return the_list
    return the_list[:n]


def create_chat_name(user_1_id, user_2_id):
    name = str(user_1_id) + "_" + str(user_2_id)
    if user_1_id > user_2_id:
        name = str(user_2_id) + "_" + str(user_1_id)

    return 'chat_' + name


def oldest_unseen_message_id(messages, user):
    for message in messages.order_by('date'):
        if (message.is_sender_doctor != user.is_doctor) and not message.seen:
            return message.id

    return 0
