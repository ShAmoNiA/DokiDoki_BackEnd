import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.auth import login, logout

from rest_framework.authtoken.models import Token


def generate_group_name(username):
    return 'chat_' + username


class ChatConsumer(WebsocketConsumer):

    def connect(self):

        try:
            token = self.scope['url_route']['kwargs']['token']
            self.user = Token.objects.get(key=token).user
            async_to_sync(login)(self.scope, self.user)
        except:
            self.close(code=403)

        self.group_name = generate_group_name(self.user.username)
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

            message = text_data_json["message"]
            receiver = text_data_json['receiver_username']
            receiver_group_name = generate_group_name(receiver)

            # TODO: save the message in db

            print()
            print('FROM: ' + self.group_name)
            print('TO: ' + receiver_group_name)
            print('MESSAGE: ' + message)

            async_to_sync(self.channel_layer.group_send)(
                receiver_group_name,
                {
                    'type': 'chat_message',
                    'message': message
                }
            )

    def chat_message(self, event):
        message = event['message']

        self.send(text_data=json.dumps({
            'message': message
        }))
