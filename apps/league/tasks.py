from celery import shared_task
from django.core.cache import cache

from .models import Leaderboard, Match, Prediction


@shared_task
def calculate_prediction_points(match_id):
    from django.db import transaction

    match = Match.objects.select_related("league").get(pk=match_id)
    if (
        match.status != "finished"
        or match.home_score is None
        or match.away_score is None
    ):
        return

    predictions = Prediction.objects.select_related("user").filter(match=match)

    with transaction.atomic():
        for prediction in predictions:
            points = 0

            # Exact score prediction
            if (
                prediction.home_score == match.home_score
                and prediction.away_score == match.away_score
            ):
                points = 10

            # Correct outcome (win/lose/draw)
            elif (
                (
                    prediction.home_score > prediction.away_score
                    and match.home_score > match.away_score
                )
                or (
                    prediction.home_score < prediction.away_score
                    and match.home_score < match.away_score
                )
                or (
                    prediction.home_score == prediction.away_score
                    and match.home_score == match.away_score
                )
            ):
                points = 5

            # One correct score
            elif (
                prediction.home_score == match.home_score
                or prediction.away_score == match.away_score
            ):
                points = 2

            prediction.points_earned = points
            prediction.save()

            # Update user points and leaderboards
            user = prediction.user
            user.points += points
            user.save()

            # Update all leaderboards the user is part of
            Leaderboard.objects.filter(user=user, league__matches=match).update(
                points=models.F("points") + points
            )

    # Update leaderboard positions
    for league in match.league.all():
        update_leaderboard_positions.delay(league.id)

    # Clear relevant caches
    cache.delete(f"match_{match_id}_data")
    cache.delete_pattern(f"leaderboard_*")


@shared_task
def update_leaderboard_positions(league_id):
    from django.db import connection

    with connection.cursor() as cursor:
        cursor.execute(
            """
            UPDATE prediction_leaderboard
            SET position = subquery.rank
            FROM (
                SELECT 
                    id,
                    RANK() OVER (ORDER BY points DESC) as rank
                FROM prediction_leaderboard
                WHERE league_id = %s
            ) AS subquery
            WHERE prediction_leaderboard.id = subquery.id
        """,
            [league_id],
        )
