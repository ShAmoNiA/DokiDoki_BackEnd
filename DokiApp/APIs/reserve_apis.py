"""
contains:
    ReserveDoctor
    ReserveList
"""

import json
from datetime import datetime

from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from ..permissions import IsPatient, IsDoctor

from .chat_apis import create_chat_name
from .email_functions import send_reserve_message
from ..serializers import ReserveSerializer
from ..models import User, DoctorProfile, Reserve, Chat


class ReserveDoctor(APIView):
    permission_classes = (IsAuthenticated, IsPatient)

    def post(self, request):
        time = request.POST['time']
        date_str = request.POST['date']
        doctor_id = request.POST['doctor_id']

        doctor = get_object_or_404(User, id=doctor_id)
        doctorProfile = get_object_or_404(DoctorProfile, user=doctor)
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')

        Reserve.objects.create(doctor=doctorProfile, creator=request.user, time=time, date=date_obj)
        send_reserve_message(doctorProfile.user.email, doctorProfile.user.username,
                             date_str + " " + time, request.user.fullname)

        self.create_chat_object_in_db(request.user.profile, doctorProfile)

        return Response({'success': True, 'message': 'Reserved!'}, status=status.HTTP_200_OK)

    def create_chat_object_in_db(self, patient, doctor):
        user_1_id = patient.user.id
        user_2_id = doctor.user.id

        name = create_chat_name(user_1_id, user_2_id)
        Chat.objects.create(name=name, patient=patient, doctor=doctor)


class ReserveList(APIView):
    permission_classes = (IsAuthenticated, IsDoctor)

    def get(self, request):
        reserves = Reserve.objects.filter(doctor=request.user.profile)

        result = [ReserveSerializer(instance=reserve).data for reserve in reserves]
        return Response({'success': True, 'reserves': result}, status=status.HTTP_200_OK)
