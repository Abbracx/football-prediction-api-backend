from rest_framework import serializers

from apps.league.models import Leaderboard, League, Match, Prediction, Team
from apps.users.serializers import UserSerializer
from apps.users.models import User


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ["id", "name", "short_code", "logo"]


class MatchSerializer(serializers.ModelSerializer):
    home_team = TeamSerializer()
    away_team = TeamSerializer()

    class Meta:
        model = Match
        fields = [
            "id",
            "home_team",
            "away_team",
            "start_time",
            "home_score",
            "away_score",
            "status",
            "league",
        ]


class PredictionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    match = MatchSerializer(read_only=True)

    class Meta:
        model = Prediction
        fields = [
            "id",
            "user",
            "match",
            "home_score",
            "away_score",
            "points_earned",
            "created_at",
        ]


class LeagueSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = League
        fields = ["id", "name", "creator", "is_public", "created_at", "member_count"]

    def get_member_count(self, obj):
        return obj.members.count()


class LeaderboardSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Leaderboard
        fields = ["user", "points", "position", "last_updated"]
