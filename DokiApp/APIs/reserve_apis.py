import datetime

from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ..Helper_functions.email_functions import send_reserve_message
from ..permissions import IsPatient
from ..serializers import *


class ReserveDoctor(APIView):
    permission_classes = (IsAuthenticated, IsPatient)

    def post(self, request, ):
        time = request.POST['time']
        date_str = request.POST['date']
        doctor_id = request.POST['doctor_id']

        doctor = get_object_or_404(DoctorProfile, id=doctor_id)
        date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')

        Reserve.objects.create(doctor=doctor, user=request.user, time=time, date=date_obj)
        send_reserve_message(doctor.user.email, doctor.user.username, date_str + " " + time, request.user.fullname)

        return Response({'success': True, 'message': 'Reserved!'})


class ReservesList(APIView):

    def get(self):
        return Response({'success': True, 'message': 'Not available for now'})
