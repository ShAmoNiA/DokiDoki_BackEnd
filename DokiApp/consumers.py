import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


def generate_group_name(username):
    return 'chat_' + username


class ChatConsumer(WebsocketConsumer):

    def connect(self):
        self.user = self.scope['user']
        if self.user.is_authenticated:
            self.group_name = generate_group_name(user.username)
            async_to_sync(
                self.channel_layer.group_add(self.group_name, self.channel_name)
            )
            self.accept()
        else:
            self.close(code=403)

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name, self.channel_name
        )

    def receive(self, text_data=None, bytes_data=None):
        if text_data:
            text_data_json = json.loads(text_data)
            receiver = text_data_json['receiver_username']
            receiver_group_name = generate_group_name(receiver)

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
