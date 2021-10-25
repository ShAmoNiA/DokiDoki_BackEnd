from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import UserSerializer


class SignUp(APIView):

    def post(self, request):
        user_serializer = UserSerializer(data=request.data)
        if user_serializer.is_valid():
            user_serializer.save()
            return Response({'success': True, 'message': 'User saved successfully'})

        return Response({'success': False, 'message': user_serializer.errors})
