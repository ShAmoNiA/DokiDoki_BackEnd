from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from rest_framework.parsers import MultiPartParser
from rest_framework.parsers import FormParser

from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny

from django.core.paginator import Paginator
from django.db.models import Q

from .models import *
from .Helper_functions.helper_functions import *
from .serializers import *

from .APIs.auth_apis import *
from .APIs.feedback_apis import *
from .APIs.profile_apis import *
from .APIs.reserve_apis import *
from .APIs.search_apis import *


@api_view(['POST'])
def send_email_by_front(request):
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


class LoadOldChat(APIView):
    permission_classes = (IsAuthenticated,)
    PAGINATE_BY = 15

    def get(self, request):
        partner_username = request.GET['partner_username']
        partner = get_object_or_404(User, username=partner_username)
        chat_name = create_chat_name(partner.id, request.user.id)
        chat = Chat.objects.get(name=chat_name)
        messages = Message.objects.filter(chat=chat).order_by('-date')

        result = adapt_message(messages)

        page = int(request.GET.get('page', 1))
        paginator = Paginator(result, self.PAGINATE_BY)
        if paginator.num_pages < page or page < 1:
            return Response({"success": False, "message": "Page not found"}, status=status.HTTP_404_NOT_FOUND)
        result = paginator.page(page).object_list

        self.set_messages_as_seen(result)

        return Response({"success": True, "messages": result, "page": page, "max_page": paginator.num_pages}
                        , status=status.HTTP_200_OK)

    def set_messages_as_seen(self, result):
        for message in Message.objects.filter(id__in=self.message_ids(result)):
            if not message.seen:
                message.set_as_seen()

    def message_ids(self, message_list):
        result = []
        for obj in message_list:
            ID = obj['id']
            result.append(ID)
        return result
