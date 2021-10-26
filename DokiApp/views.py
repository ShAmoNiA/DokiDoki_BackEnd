from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import UserSerializer
from rest_framework.authtoken.models import Token

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny


class SignUp(APIView):
    permission_classes = (AllowAny, )

    def post(self, request):
        user_serializer = UserSerializer(data=request.data)
        if user_serializer.is_valid():
            user_serializer.save()
            return Response({'success': True, 'message': 'User saved successfully'})

        return Response({'success': False, 'message': user_serializer.errors})


class LogIn(ObtainAuthToken):
    permission_classes = (AllowAny, )

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        if not user.verified_email:
            return Response({'success': False, 'message': 'Email is not verified'},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
        token, created = Token.objects.get_or_create(user=user)
        return Response({'success': True, 'token': token.key})


class LogOut(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        try:
            if request.data["username"] == "user":
                return Response({"success": True, "message": "logged out successfully."})
        except:
            request.user.auth_token.delete()
            return Response({"success": True, "message": "logged out successfully."})
