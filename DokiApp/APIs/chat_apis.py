from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from rest_framework.permissions import IsAuthenticated

from django.shortcuts import get_object_or_404
from ..models import User, Chat, Message

from ..Helper_functions.helper_functions import create_chat_name, oldest_unseen_message_id
from ..Helper_functions.adapters import adapt_message, adapt_chat


class ChatList(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        profile = user.profile

        if user.is_doctor:
            chats = Chat.objects.filter(doctor=profile)
        else:
            chats = Chat.objects.filter(patient=profile)

        return Response({'success': True, 'chats': adapt_chat(chats, user)})


class LoadOldChat(APIView):
    permission_classes = (IsAuthenticated,)
    PAGINATE_BY = 15

    def get(self, request):
        partner_username = request.GET['partner_username']
        partner = get_object_or_404(User, username=partner_username)
        chat_name = create_chat_name(partner.id, request.user.id)
        chat = get_object_or_404(Chat, name=chat_name)
        messages = Message.objects.filter(chat=chat).order_by('-date')
        oldest_unseen = oldest_unseen_message_id(messages, request.user)

        result = adapt_message(messages)

        page = int(request.GET.get('page', False))
        num_pages = 'not defined'
        if page:
            paginator = Paginator(result, self.PAGINATE_BY)
            if paginator.num_pages < page or page < 1:
                return Response({"success": False, "message": "Page not found"}, status=status.HTTP_404_NOT_FOUND)
            result = paginator.page(page).object_list
            num_pages = paginator.num_pages

        self.set_messages_as_seen(result, request.user)

        return Response({"success": True, "page": page if page else 'not defined', "max_page": num_pages,
                         "oldest_unseen_message_id": oldest_unseen,
                         "messages": result}, status=status.HTTP_200_OK)

    def set_messages_as_seen(self, result, user):
        for message in Message.objects.filter(id__in=self.message_ids(result)):
            if (not message.seen) and (message.is_sender_doctor != user.is_doctor):
                message.set_as_seen()

    def message_ids(self, message_list):
        result = []
        for obj in message_list:
            ID = obj['id']
            result.append(ID)
        return result