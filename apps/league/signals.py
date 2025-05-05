from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.cache import cache
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Match
from .tasks import calculate_prediction_points


@receiver(post_save, sender=Match)
def match_status_update(sender, instance, **kwargs):
    if (
        instance.status == "finished"
        and instance.home_score is not None
        and instance.away_score is not None
    ):
        # Trigger points calculation
        calculate_prediction_points.delay(instance.id)

    # Notify WebSocket clients
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"match_{instance.id}",
        {
            "type": "match_update",
            "data": {
                "status": instance.status,
                "home_score": instance.home_score,
                "away_score": instance.away_score,
            },
        },
    )

    # Clear match cache
    cache.delete(f"match_{instance.id}_data")
