from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from apps.common.models import TimeStampedModel

User = get_user_model()


class League(TimeStampedModel):
    name = models.CharField(max_length=100)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    members = models.ManyToManyField(User, related_name="leagues")
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class Team(TimeStampedModel):
    name = models.CharField(max_length=100)
    short_code = models.CharField(max_length=5)
    logo = models.URLField(blank=True, null=True)


class Status(models.TextChoices):
    SCHEDULED = "scheduled", "Scheduled"
    IN_PLAY = "in_play", "In Play"
    FINISHED = "finished", "Finished"
    POSTPONED = "postponed", "Postponed"
    CANCELED = "canceled", "Canceled"

class Match(TimeStampedModel):


    home_team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name="home_matches"
    )
    away_team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name="away_matches"
    )
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name="matches")
    start_time = models.DateTimeField()
    home_score = models.IntegerField(null=True, blank=True)
    away_score = models.IntegerField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SCHEDULED,
    )


class Prediction(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="predictions")
    match = models.ForeignKey(
        Match, on_delete=models.CASCADE, related_name="predictions"
    )
    home_score = models.IntegerField(validators=[MinValueValidator(0)])
    away_score = models.IntegerField(validators=[MinValueValidator(0)])
    points_earned = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "match")


class Leaderboard(TimeStampedModel):
    league = models.ForeignKey(
        League, on_delete=models.CASCADE, related_name="leaderboard"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)
    position = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("league", "user")
