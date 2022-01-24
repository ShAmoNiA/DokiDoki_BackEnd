"""
contains:
    SignUp
    CheckUsername
    LogIn
    LogOut
    VerifyEmail
    forgot_password
    ResetPassword
"""

from secrets import token_hex
from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

from ..models import User
from ..serializers import UserSerializer
from ..Helper_functions.email_functions import send_reset_pass_email, send_text_email


class SignUp(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        user_serializer = UserSerializer(data=request.data)
        if user_serializer.is_valid():
            user_serializer.save()
            return Response({'success': True, 'message': 'User saved successfully'})

        return Response({'success': False, 'message': user_serializer.errors})


class CheckUsername(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, username):
        user = User.objects.filter(username__iexact=username)
        return Response({"exists": user.exists()})


class LogIn(ObtainAuthToken):
    permission_classes = (AllowAny,)

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
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        request.user.auth_token.delete()
        return Response({"success": True, "message": "logged out successfully."})


class VerifyEmail(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        result = "Your email verified successfully"
        token = request.data["token"]
        email = request.data["email"]
        user = User.objects.get(email=email)
        if user.verified_email:
            result = "ERROR: your email verified before"
        elif user.verify_email_token == token:
            user.verify_email()
        else:
            result = "ERROR: privateTokenError"

        return self.result_page(request, result)

    def result_page(self, request, result):
        return render(request, 'result.html', context={'result': result})


@api_view(['GET'])
def forgot_password(request):
    email = request.GET['email']

    user = User.objects.filter(email=email)
    if user.count() == 0:
        return Response(data={"success": False, "message": "user not found"})
    user = user[0]

    if not user.verified_email:
        return Response(data={"success": False, "message": "email not verified"})

    reset_password_token = token_hex(64)
    user.reset_password_token = reset_password_token
    user.save()
    send_reset_pass_email(email, user.fullname, reset_password_token)

    return Response(data={"success": True, "message": "email sent"})


class ResetPassword(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        token = request.data['token']
        email = request.data['email']
        password_1 = request.data['password_1']
        password_2 = request.data['password_2']

        user = User.objects.filter(email=email)
        if user.count() == 0:
            return self.result_page(request, "user not found")
        elif password_1 != password_2:
            return self.result_page(request, "passwords are different")

        user = user[0]
        if not user.verified_email:
            return self.result_page(request, "Your email is not verified")
        elif user.reset_password_token == "expired":
            return self.result_page(request, "Your token is expired")
        elif user.reset_password_token != token:
            return self.result_page(request, "Your token is wrong")

        user.set_password(password_1)
        user.reset_password_token = "expired"
        user.save()
        return self.result_page(request, "Password changed successfully. you can sign in.")

    def result_page(self, request, result):
        return render(request, 'result.html', context={'result': result})
