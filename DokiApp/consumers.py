import json

from asgiref.sync import async_to_sync, sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.auth import login, logout

from rest_framework.authtoken.models import Token
from .models import User


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        try:
            token = self.scope['url_route']['kwargs']['auth_token']
            self.user = await self.get_user_by_token(token)
            await login(self.scope, self.user)
        except:
            await self.close(code=403)

        partner_username = self.scope['url_route']['kwargs']['partner_username']
        self.group_name = await self.generate_group_name(self.user.username, partner_username)

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

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
    def generate_group_name(self, username_1, username_2):
        user_1_id = User.objects.get(username=username_1).id
        user_2_id = User.objects.get(username=username_2).id

        name = str(user_1_id) + "_" + str(user_2_id)
        if user_1_id > user_2_id:
            name = str(user_2_id) + "_" + str(user_1_id)

        return 'chat_' + name
