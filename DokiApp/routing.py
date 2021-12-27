from django.urls import path

from DokiApp import consumers


WEBSOCKET_BASE_URL = 'ws' + '/'


websocket_urlpatterns = [
    path(WEBSOCKET_BASE_URL + 'chat_socket/', consumers.ChatConsumer),
]
