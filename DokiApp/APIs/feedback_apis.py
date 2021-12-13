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
            if text.isspace():
                return Response({'success': False, 'message': 'Comment is empty'})
            doctor_id = request.POST['doctor_id']
            try:
                doctor = DoctorProfile.objects.get(id=doctor_id)
            except:
                return Response({'success': False, 'message': 'Doctor not found'})
            comment = Comment(writer=request.user,text=text,doctor=doctor)
            comment.save()
            return Response({'success': True, 'message': 'Comment submitted'})
        else:
            return Response({'success': False, 'message': 'Please login first'})


class GetComments(APIView):
    def get(self,request,doctor_id):
        comments = []
        query = Comment.objects.filter(doctor__id=doctor_id)
        for cm in query:
            data = CommentSerializer(instance=cm).data
            data["writer_name"] = User.objects.get(id=data['writer']).username
            comments.append(data)

        return Response({'success': True, 'comments': comments})
