import datetime
import json

from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ..Helper_functions.email_functions import send_reserve_message
from ..permissions import IsPatient, IsDoctor
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


class ReserveList(APIView):
    permission_classes = (IsAuthenticated, IsDoctor)

    def get(self, request):
        reserves = Reserve.objects.filter(doctor=request.user.profile)

        result = ReserveSerializer(instance=reserves, many=True).data
        return Response({'success': True, 'reserves': json.dumps(result)})
