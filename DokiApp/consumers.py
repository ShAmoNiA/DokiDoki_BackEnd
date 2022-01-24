import json

from asgiref.sync import async_to_sync, sync_to_async
from channels.db import database_sync_to_async

from channels.generic.websocket import AsyncWebsocketConsumer

from rest_framework.authtoken.models import Token
from .models import User, DoctorProfile, PatientProfile, Chat, Message

from DokiDoki.settings import CHANNEL_LAYERS
from .APIs.chat_apis import create_chat_name
from .APIs.email_functions import send_text_email


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        try:
            token = self.scope['url_route']['kwargs']['auth_token']
            self.user = await self.get_user_by_token(token)

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

        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'partner_status',
                'partner_is_online': await self.is_partner_online(),
            }
        )

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'partner_status',
                'partner_is_online': False,
            }
        )

    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            text_data_json = json.loads(text_data)
            message = text_data_json["message"]

            seen = await self.is_partner_online()

            if not seen:
                try:
                    await self.email_to_offline_user()
                except:
                    pass

            message = await self.save_message_in_database(message, seen)

            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'chat_message',
                    'message': message.text,
                    'seen': message.seen,
                    'date': str(message.date),
                    'is_sender_doctor': message.is_sender_doctor
                }
            )

    async def chat_message(self, event):
        await self.send_chat(event)

    async def partner_status(self, event):
        await self.send_chat(event)

    async def send_chat(self, event):
        await self.send(text_data=json.dumps(event))

    async def is_partner_online(self):
        channel_layer = CHANNEL_LAYERS["default"]["BACKEND"]

        if channel_layer == "channels_redis.core.RedisChannelLayer":
            is_online = self.channel_layer.receive_count == 2
        elif channel_layer == "channels.layers.InMemoryChannelLayer":
            is_online = len(self.channel_layer.groups.get(self.group_name, {}).items()) == 2
        else:
            is_online = False

        return is_online

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
    # TODO: @sync_to_async
    def chat_exists_by_name(self, name):
        return bool(Chat.objects.filter(name=name).count())

    @database_sync_to_async
    # TODO: @sync_to_async
    def save_message_in_database(self, text, seen):
        return Message.objects.create(chat=self.chat, text=text, seen=seen, is_sender_doctor=self.user.is_doctor)

    @sync_to_async
    def generate_group_name(self, username_1, username_2):
        user_1_id = User.objects.get(username=username_1).id
        user_2_id = User.objects.get(username=username_2).id

        return create_chat_name(user_1_id, user_2_id)

    @sync_to_async
    def email_to_offline_user(self):
        send_text_email('New message in DokiDokiChat',
                        'the user: ' + self.user.username + ", has answered to your chat",
                        [self.partner_user.email])
