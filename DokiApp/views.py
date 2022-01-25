from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from rest_framework.parsers import MultiPartParser
from rest_framework.parsers import FormParser

from .APIs.email_functions import send_text_email

from .serializers import ImageSerializer

from .APIs.auth_apis import *
from .APIs.feedback_apis import *
from .APIs.profile_apis import *
from .APIs.reserve_apis import *
from .APIs.search_apis import *
from .APIs.chat_apis import *


class SendEmail(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        subject = request.data["subject"]
        message = request.data["message"]
        to_list = request.data["to_list"]

        to_list = to_list.split(" ")
        send_text_email(subject, message, to_list)

        return Response({"success": True, "message": "email sent"}, status=status.HTTP_200_OK)


class UploadImage(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        image_serializer = ImageSerializer(data=request.data)
        if image_serializer.is_valid():
            image_serializer.save()
            return Response({"image_url": image_serializer.data["image"]}, status=status.HTTP_200_OK)
        return Response(image_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
