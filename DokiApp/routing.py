from django.urls import path

from DokiApp import consumers


websocket_urlpatterns = [
    path('socket/', consumers.ChatConsumer),
]
