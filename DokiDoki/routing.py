from channels.routing import ProtocolTypeRouter, URLRouter
from .auth_token import TokenAuthMiddlewareStack

from DokiApp import routing as DokiApp_routing

application = ProtocolTypeRouter({
    'websocket': TokenAuthMiddlewareStack(
        URLRouter(
            DokiApp_routing.websocket_urlpatterns
        )
    )
})
