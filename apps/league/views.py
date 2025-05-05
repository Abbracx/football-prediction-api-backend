from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.league.models import Leaderboard, League, Match, Prediction
from apps.league.serializers import (
    LeaderboardSerializer,
    LeagueSerializer,
    MatchSerializer,
    PredictionSerializer,
)


class MatchViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Match.objects.select_related("home_team", "away_team")
    serializer_class = MatchSerializer

    @method_decorator(cache_page(60 * 5))
    @method_decorator(vary_on_cookie)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=True, methods=["get"])
    def predictions(self, request, pk=None):
        match = self.get_object()
        predictions = match.predictions.select_related("user")
        serializer = PredictionSerializer(predictions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def upcoming(self, request):
        queryset = self.get_queryset().filter(status="scheduled").order_by("start_time")
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def live(self, request):
        queryset = self.get_queryset().filter(status="in_play")
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class PredictionViewSet(viewsets.ModelViewSet):
    serializer_class = PredictionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Prediction.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        match = serializer.validated_data["match"]
        if match.status != "scheduled":
            return Response(
                {"error": "Predictions can only be made for scheduled matches"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer.save(user=self.request.user)


class LeagueViewSet(viewsets.ModelViewSet):
    serializer_class = LeagueSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return League.objects.filter(members=self.request.user)

    def perform_create(self, serializer):
        league = serializer.save(creator=self.request.user)
        league.members.add(self.request.user)

    @action(detail=True, methods=["post"])
    def join(self, request, pk=None):
        league = self.get_object()
        if league.is_public or request.user == league.creator:
            league.members.add(request.user)
            return Response({"status": "joined"})
        return Response(
            {"error": "This is a private league"}, status=status.HTTP_403_FORBIDDEN
        )

    @action(detail=True, methods=["get"])
    def leaderboard(self, request, pk=None):
        league = self.get_object()
        leaderboard = Leaderboard.objects.filter(league=league).order_by("-points")
        serializer = LeaderboardSerializer(leaderboard, many=True)
        return Response(serializer.data)


class LeaderboardViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LeaderboardSerializer

    def get_queryset(self):
        return Leaderboard.objects.filter(league__members=self.request.user).order_by(
            "-points"
        )
