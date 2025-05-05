from django.urls import re_path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from apps.league import consumers

websocket_urlpatterns = [
    re_path(r'ws/match/(?P<match_id>\d+)/$', consumers.MatchUpdatesConsumer.as_asgi()),
]

