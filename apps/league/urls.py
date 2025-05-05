from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.league.views import MatchViewSet, PredictionViewSet, LeagueViewSet, LeaderboardViewSet

app_name = "league" 

router = DefaultRouter()
router.register(r"matches", MatchViewSet, basename="match")
router.register(r"predictions", PredictionViewSet, basename="prediction")
router.register(r"leagues", LeagueViewSet, basename="league")

urlpatterns = [
    path("", include(router.urls)),
]