from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny

from .models import User
from .helper_functions import result_page

from .APIs.auth_apis import *


@api_view(['POST'])
def send_email_by_front(request):
    subject = request.data["subject"]
    message = request.data["message"]
    to_list = request.data["to_list"]

    to_list = to_list.split(" ")
    send_text_email(subject, message, to_list)

    return Response({"success": True, "message": "email sent"}, status=status.HTTP_200_OK)


@api_view(['POST'])
def edit_profile(request):
    if not request.user.is_authenticated:
        return Response({"success": False, "message": "You must login first"})
    user = request.user
    if 'sex' in request.data:
        user.sex = request.data["sex"]
    if 'new_password' in request.data:
        user.set_password(request.data["new_password"])
    if 'fullname' in request.data:
        user.fullname = request.data["fullname"]
    serializer = UserSerializer(request.user, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response({"success": True, "message": "Profile changed"}, status=status.HTTP_200_OK)
