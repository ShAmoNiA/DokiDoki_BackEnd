from channels.generic.websocket import WebsocketConsumer


class ChatConsumer(WebsocketConsumer):

    def connect(self):
        pass
        # self.accept()

    def disconnect(self, code):
        pass

    def receive(self, text_data=None, bytes_data=None):
        pass
        # self.send(text_data=text_data)
