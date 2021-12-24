from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..Helper_functions.email_functions import send_reserve_message
from ..serializers import *
import datetime


class ReserveDoctor(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request,):
        if not request.user.is_authenticated:
            return Response({'success': False, 'message': 'Please login first'})
        time = request.POST['time']
        date_str = request.POST['date']
        doctor_id = request.POST['doctor_id']
        doctors = DoctorProfile.objects.filter(id=doctor_id)
        date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        if len(doctors) == 0:
            return Response({'success': False, 'message': 'Doctor not found'})
        doctor = doctors.first()
        reserve = Reserve(doctor=doctor, user=request.user, time=time, date=date_obj)
        reserve.save()
        send_reserve_message(doctor.user.email, doctor.user.username, date_str + " " + time, request.user.fullname)
        return Response({'success': True, 'message': 'Reserved!'})

class ReservesList(APIView):
    def get(self):
        return Response({'success' : True, 'message' : 'Not available for now'})