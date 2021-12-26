import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class ChatConsumer(WebsocketConsumer):

    def connect(self):
        token = self.scope['url_route']['kwargs']['sender_token']
        user = Token.objects.get(key=token).user
        self.username = user.username
        self.group_name = 'chat_' + self.username

        async_to_sync(
            self.channel_layer.group_add(self.group_name, self.channel_name)
        )

        self.accept()

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name, self.channel_name
        )

    def receive(self, text_data=None, bytes_data=None):
        if text_data:
            text_data_json = json.loads(text_data)
            receiver = text_data_json['receiver_username']
            receiver_group_name = 'chat_' + receiver

            # TODO: save in db

            async_to_sync(self.channel_layer.group_send)(
                receiver_group_name,
                {
                    'type': 'chat_message',
                    'message': text_data
                }
            )

    def chat_message(self, event):
        message = event['message']
        self.send(text_data=message)
