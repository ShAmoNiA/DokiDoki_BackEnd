from django.db.models import Avg
from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from ..Helper_functions.adapters import adapt_comment
from ..serializers import *


class WriteComment(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        text = request.POST['text']
        doctor_id = request.POST['doctor_id']

        if text.isspace():
            return Response({'success': False, 'message': 'Comment is empty'})

        doctor = get_object_or_404(DoctorProfile, id=doctor_id)
        Comment.objects.create(writer=request.user, text=text, doctor=doctor)
        return Response({'success': True, 'message': 'Comment submitted'})


class GetComments(APIView):

    def get(self, request, doctor_id):
        comments = Comment.objects.filter(doctor__id=doctor_id)
        return Response({'success': True, 'comments': adapt_comment(comments)})


class RateDoctor(APIView):

    def get(self, request, doctor_id):
        rate = Rate.objects.filter(doctor__id=doctor_id).aggregate(Avg('rate'))["rate__avg"]
        return Response({'success': True, 'rate': rate})

    def post(self, request, doctor_id):
        if request.user.is_authenticated:
            rate = request.POST['rate']
            doctor = get_object_or_404(DoctorProfile, id=doctor_id)

            new_rate = RateSerializer(data={"doctor": doctor_id, "user": request.user.id, "rate": rate})
            if not new_rate.is_valid():
                return Response({'success': False, 'message': new_rate.errors})

            rate_object = Rate.objects.filter(doctor=doctor, user=request.user)
            if len(rate_object) != 0:
                rate_object.update(rate=rate)
                return Response({'success': True, 'message': 'New rate replaced!'})

            new_rate.save()
            return Response({'success': True, 'message': 'Rate submitted!'})
        else:
            return Response({'success': False, 'message': 'Please login first'})
