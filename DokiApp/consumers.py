import json

from asgiref.sync import async_to_sync, sync_to_async
from channels.db import database_sync_to_async

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.auth import login, logout

from rest_framework.authtoken.models import Token
from .models import User, DoctorProfile, PatientProfile, Chat, Message


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        try:
            token = self.scope['url_route']['kwargs']['auth_token']
            self.user = await self.get_user_by_token(token)
            await login(self.scope, self.user)

            partner_username = self.scope['url_route']['kwargs']['partner_username']
            self.partner_user = await self.get_user_by_username(partner_username)
        except:
            await self.close(code=403)
            return

        self.group_name = await self.generate_group_name(self.user.username, self.partner_user.username)
        if not await self.chat_exists_by_name(self.group_name):
            await self.close(code=403)
            return
        self.chat = await self.get_chat_by_name(self.group_name)

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        try:
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
        except:
            pass

    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            text_data_json = json.loads(text_data)
            message = text_data_json["message"]

            # TODO: save the message in db

            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'chat_message',
                    'message': message
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @sync_to_async
    def get_user_by_token(self, token):
        return Token.objects.get(key=token).user

    @sync_to_async
    def get_user_by_username(self, username):
        return User.objects.get(username=username)

    @sync_to_async
    def get_chat_by_name(self, name):
        return Chat.objects.get(name=name)

    @database_sync_to_async
    def chat_exists_by_name(self, name):
        return bool(Chat.objects.filter(name=name).count())

    @sync_to_async
    def generate_group_name(self, username_1, username_2):
        user_1_id = User.objects.get(username=username_1).id
        user_2_id = User.objects.get(username=username_2).id

        name = str(user_1_id) + "_" + str(user_2_id)
        if user_1_id > user_2_id:
            name = str(user_2_id) + "_" + str(user_1_id)

        return 'chat_' + name
