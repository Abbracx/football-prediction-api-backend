import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import cache
from django.core.exceptions import ValidationError

from apps.league.models import Match, Prediction
from apps.league.serializers import MatchSerializer

class MatchUpdatesConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.match_group_name = None
        self.match_id = None

    async def connect(self):
        self.match_id = self.scope["url_route"]["kwargs"]["match_id"]
        self.match_group_name = f"match_{self.match_id}"

        # Join match group
        await self.channel_layer.group_add(self.match_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, code):
        # Leave match group
        await self.channel_layer.group_discard(self.match_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json["type"]

        if message_type == "prediction":
            await self.handle_prediction(text_data_json)
        elif message_type == "get_updates":
            await self.send_match_updates()

    async def handle_prediction(self, data):
        user = self.scope["user"]
        if user.is_anonymous:
            return

        # Validate and save prediction
        success = await self.save_prediction(
            user, self.match_id, data["home_score"], data["away_score"]
        )

        if success:
            # Broadcast new prediction to group
            await self.channel_layer.group_send(
                self.match_group_name,
                {
                    "type": "prediction_update",
                    "user_id": user.id,
                    "username": user.username,
                    "home_score": data["home_score"],
                    "away_score": data["away_score"],
                },
            )

    @database_sync_to_async
    def save_prediction(self, user, match_id, home_score, away_score):

        try:
            match = Match.objects.get(pk=match_id)
            if match.status != "scheduled":
                return False

            prediction, created = Prediction.objects.update_or_create(
                user=user,
                match=match,
                defaults={"home_score": home_score, "away_score": away_score},
            )
            return True
        except (Match.DoesNotExist, ValidationError):
            return False

    async def send_match_updates(self):
        match_data = await self.get_match_data(self.match_id)
        await self.send(
            text_data=json.dumps({"type": "match_update", "data": match_data})
        )

    @database_sync_to_async
    def get_match_data(self, match_id):

        # Check if match data is cached
        # If not, fetch from database and cache it
        cache_key = f"match_{match_id}_data"
        match_data = cache.get(cache_key)

        if not match_data:
            match = (
                Match.objects.select_related("home_team", "away_team")
                .prefetch_related("predictions")
                .get(pk=match_id)
            )
            match_data = MatchSerializer(match).data
            cache.set(cache_key, match_data, timeout=60 * 5)  # Cache for 5 minutes

        return match_data

    # Receive message from match group
    async def prediction_update(self, event):
        await self.send(text_data=json.dumps(event))

    async def match_update(self, event):
        await self.send(text_data=json.dumps(event))
