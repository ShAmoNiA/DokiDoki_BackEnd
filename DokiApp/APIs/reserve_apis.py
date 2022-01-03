"""
contains:
    ReserveDoctor
    ReserveList
"""


import datetime
import json

from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ..Helper_functions.email_functions import send_reserve_message
from ..Helper_functions.helper_functions import create_chat_name
from ..permissions import IsPatient, IsDoctor
from ..serializers import *


# TODO: move the function to another place
def create_chat_object_in_db(patient, doctor):
    user_1_id = patient.user.id
    user_2_id = doctor.user.id

    name = create_chat_name(user_1_id, user_2_id)
    Chat.objects.create(name=name, patient=patient, doctor=doctor)


class ReserveDoctor(APIView):
    permission_classes = (IsAuthenticated, IsPatient)

    def post(self, request):
        time = request.POST['time']
        date_str = request.POST['date']
        doctor_id = request.POST['doctor_id']

        doctorProfile = get_object_or_404(DoctorProfile, id=doctor_id)
        date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')

        Reserve.objects.create(doctor=doctorProfile, user=request.user, time=time, date=date_obj)
        send_reserve_message(doctorProfile.user.email, doctorProfile.user.username,
                             date_str + " " + time, request.user.fullname)

        create_chat_object_in_db(request.user.profile, doctorProfile)

        return Response({'success': True, 'message': 'Reserved!'})


class ReserveList(APIView):
    permission_classes = (IsAuthenticated, IsDoctor)

    def get(self, request):
        reserves = Reserve.objects.filter(doctor=request.user.profile)

        result = ReserveSerializer(instance=reserves, many=True).data
        return Response({'success': True, 'reserves': json.dumps(result)})
