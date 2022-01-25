"""
contains:
    WriteComment
    GetComments
    RateDoctor
"""

from django.db.models import Avg
from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from .adapters import adapt_comment
from ..serializers import RateSerializer
from ..models import User, DoctorProfile, Rate, Comment


class WriteComment(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        text = request.POST.get('text', None)
        doctor_id = int(request.POST.get('doctor_id', -1))

        empty_comment = bool(text == '' or text == ' ' or text is None)
        if empty_comment:
            return Response({'success': False, 'message': 'Comment is empty'}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(User, id=doctor_id)
        if user.is_patient:
            return Response({'success': False, 'message': 'Doctor not found'}, status=status.HTTP_404_NOT_FOUND)

        doctorProfile = user.profile
        Comment.objects.create(writer=request.user, text=text, doctor=doctorProfile)
        return Response({'success': True, 'message': 'Comment submitted'}, status=status.HTTP_200_OK)


class GetComments(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, doctor_id):
        comments = Comment.objects.filter(doctor__user__id=doctor_id)
        return Response({'success': True, 'comments': adapt_comment(comments)}, status=status.HTTP_200_OK)


class RateDoctor(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, doctor_id):
        doctorProfile = get_object_or_404(User, is_doctor=True, id=doctor_id).profile
        rate = Rate.objects.filter(doctor=doctorProfile).aggregate(Avg('rate'))["rate__avg"]
        return Response({'success': True, 'rate': rate}, status=status.HTTP_200_OK)

    def post(self, request, doctor_id):
        rate = int(float(request.POST['rate']))
        doctor = get_object_or_404(User, is_doctor=True, id=doctor_id)
        doctorProfile = get_object_or_404(DoctorProfile, user=doctor)

        rateSerializer = RateSerializer(data={"doctor": doctorProfile.id, "user": request.user.id, "rate": rate})
        if rateSerializer.is_valid():
            rateSerializer.save()
            return Response({'success': True, 'message': 'Rate submitted!'}, status=status.HTTP_200_OK)

        return Response({'success': False, 'message': rateSerializer.errors}, status=status.HTTP_400_BAD_REQUEST)
