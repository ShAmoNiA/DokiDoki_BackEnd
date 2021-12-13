import os

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from ..serializers import *

class WriteComment(APIView):
    permission_classes = (IsAuthenticated, )
    def post(self, request):
        if request.user.is_authenticated:
            text = request.POST['text']
            doctor_id = request.POST['doctor_id']
            doctor = DoctorProfile.objects.get(id=doctor_id)
            comment = Comment(writer=request.user,text=text,doctor=doctor)
            comment.save()
            return Response({'success': True, 'message': 'Comment submitted'})
        else:
            return Response({'success': False, 'message': 'Please login first'})

