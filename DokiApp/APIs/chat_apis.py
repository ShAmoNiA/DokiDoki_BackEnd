"""
contains:
    ChatList
    LoadOldChat
"""

from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from rest_framework.permissions import IsAuthenticated

from ..models import User, Chat, Message
from .adapters import adapt_message, adapt_chat


def create_chat_name(user_1_id, user_2_id):
    name = str(user_1_id) + "_" + str(user_2_id)
    if user_1_id > user_2_id:
        name = str(user_2_id) + "_" + str(user_1_id)

    return 'chat_' + name


class ChatList(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        profile = user.profile

        if user.is_doctor:
            chats = Chat.objects.filter(doctor=profile)
        else:
            chats = Chat.objects.filter(patient=profile)

        return Response({'success': True, 'chats': adapt_chat(chats, user)}, status=status.HTTP_200_OK)


class LoadOldChat(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        partner_username = request.GET['partner_username']
        partner = get_object_or_404(User, username=partner_username)
        chat_name = create_chat_name(partner.id, request.user.id)
        chat = get_object_or_404(Chat, name=chat_name)
        messages = Message.objects.filter(chat=chat).order_by('-date')
        oldest_unseen = self.oldest_unseen_message_id(messages, request.user)

        result = adapt_message(messages)
        self.set_messages_as_seen(result, request.user)

        return Response({"success": True, "messages": result, "oldest_unseen_message_id": oldest_unseen},
                        status=status.HTTP_200_OK)

    def oldest_unseen_message_id(self, messages, user):
        for message in messages.order_by('date'):
            if (message.is_sender_doctor != user.is_doctor) and not message.seen:
                return message.id

        return 0

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
