from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async

from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AnonymousUser


@database_sync_to_async
def get_user(token_key):
    try:
        return Token.objects.get(key=token_key).user
    except:
        return AnonymousUser()


class TokenAuthMiddleware:
    """
    Token authorization middleware for Django Channels 2
    """

    def __init__(self, asgi_app):
        self.asgi_app = asgi_app

    async def __call__(self, scope, receive, send):
        headers = dict(scope['headers'])
        if b'authorization' in headers:
            try:
                token_name, token_key = headers[b'authorization'].decode().split()
                if token_name == 'Token':
                    scope['user'] = await get_user(token_key)
            except:
                scope['user'] = AnonymousUser()

        return await self.asgi_app(scope, receive, send)


TokenAuthMiddlewareStack = lambda inner: TokenAuthMiddleware(AuthMiddlewareStack(inner))
