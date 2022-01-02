from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

from DokiApp import routing as DokiApp_routing

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            DokiApp_routing.websocket_urlpatterns
        )
    )
})
