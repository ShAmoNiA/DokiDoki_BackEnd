"""
contains:
    WriteComment
    GetComments
    RateDoctor
"""

from django.db.models import Avg
from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from ..Helper_functions.adapters import adapt_comment
from ..serializers import *


class WriteComment(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        text = request.POST['text']
        doctor_id = request.POST['doctor_id']

        if text.isspace():
            return Response({'success': False, 'message': 'Comment is empty'})

        doctor = get_object_or_404(DoctorProfile, id=doctor_id)
        Comment.objects.create(writer=request.user, text=text, doctor=doctor)
        return Response({'success': True, 'message': 'Comment submitted'})


class GetComments(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, doctor_id):
        comments = Comment.objects.filter(doctor__user__id=doctor_id)
        return Response({'success': True, 'comments': adapt_comment(comments)})


class RateDoctor(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, doctor_id):
        rate = Rate.objects.filter(doctor__id=doctor_id).aggregate(Avg('rate'))["rate__avg"]
        return Response({'success': True, 'rate': rate})

    def post(self, request, doctor_id):
        rate = request.POST['rate']
        doctor = get_object_or_404(DoctorProfile, id=doctor_id)

        rateSerializer = RateSerializer(data={"doctor": doctor, "user": request.user, "rate": rate})
        if rateSerializer.is_valid():
            rateSerializer.save()
            return Response({'success': True, 'message': 'Rate submitted!'})

        return Response({'success': False, 'message': rateSerializer.errors})
