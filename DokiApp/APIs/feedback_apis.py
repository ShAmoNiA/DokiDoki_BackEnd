import os

from django.db.models import Avg
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from ..serializers import *


class WriteComment(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if request.user.is_authenticated:
            text = request.POST['text']
            if text.isspace():
                return Response({'success': False, 'message': 'Comment is empty'})
            doctor_id = request.POST['doctor_id']
            try:
                doctor = DoctorProfile.objects.get(id=doctor_id)
            except:
                return Response({'success': False, 'message': 'Doctor not found'})
            comment = Comment(writer=request.user, text=text, doctor=doctor)
            comment.save()
            return Response({'success': True, 'message': 'Comment submitted'})
        else:
            return Response({'success': False, 'message': 'Please login first'})


class GetComments(APIView):
    def get(self, request, doctor_id):
        comments = []
        query = Comment.objects.filter(doctor__id=doctor_id)
        for cm in query:
            data = CommentSerializer(instance=cm).data
            data["writer_name"] = User.objects.get(id=data['writer']).username
            comments.append(data)

        return Response({'success': True, 'comments': comments})


class RateDoctor(APIView):
    def get(self, request, doctor_id):
        rate = Rate.objects.filter(doctor__id=doctor_id).aggregate(Avg('rate'))["rate__avg"]
        return Response({'success': True, 'rate': rate})

    def post(self, request,doctor_id):
        if request.user.is_authenticated:
            rate = request.POST['rate']
            doctors = DoctorProfile.objects.filter(id=doctor_id)
            if len(doctors) == 0:
                return Response({'success': False, 'message': 'Doctor not found'})
            new_rate = RateSerializer(data={"doctor":doctor_id , "user":request.user.id,"rate":rate})
            if not new_rate.is_valid():
                return Response({'success': False, 'message': new_rate.errors})

            rates = Rate.objects.filter(doctor=doctors.first(), user=request.user)
            if len(rates) != 0:
                rates.update(rate=rate)
                return Response({'success': True, 'message': 'New rate replaced!'})

            new_rate.save()
            return Response({'success': True, 'message': 'Rate submitted!'})
        else:
            return Response({'success': False, 'message': 'Please login first'})
