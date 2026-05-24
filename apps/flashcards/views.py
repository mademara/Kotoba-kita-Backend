import math
import random
from datetime import timedelta

from django.db import transaction
from django.db.models import Avg, Count, Min, Q
from django.db.models.functions import TruncDate
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ..decks.models import Deck
from ..words.models import Word
from .models import Flashcard
from .serializers import (
    HomeStatsSerializer,
    StudyResponseSerializer,
    StudySessionSerializer,
    SubmitAnswerSerializer,
)
from .services import apply_review, get_or_create_flashcard, get_rating_from_response


class GenerateQuestionsView(APIView):
    @extend_schema(
        responses={200: StudySessionSerializer},
        summary="Mulai sesi belajar untuk deck tertentu",
    )
    def get(self, request: Request, deck_id):
        try:
            deck = Deck.objects.prefetch_related("words").get(
                Q(id=deck_id) & (Q(owner=request.user) | Q(is_default=True))
            )
        except Deck.DoesNotExist:
            return Response(
                {"message": "Deck tidak ditemukan atau Anda tidak memiliki akses."},
                status=status.HTTP_404_NOT_FOUND,
            )

        all_words = list(deck.words.all())
        if len(all_words) < 4:
            return Response(
                {"message": "Deck harus berisi minimal 4 kata untuk memulai sesi belajar."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        all_word_ids = [w.id for w in all_words]
        now = timezone.now()


        due_word_ids = set(
            Flashcard.objects.filter(
                user=request.user,
                word_id__in=all_word_ids,
                due__lte=now,
            ).values_list("word_id", flat=True)
        )


        reviewed_word_ids = set(
            Flashcard.objects.filter(
                user=request.user,
                word_id__in=all_word_ids,
            ).values_list("word_id", flat=True)
        )


        new_words = [w for w in all_words if w.id not in reviewed_word_ids]

        has_due = len(due_word_ids) > 0
        has_new = len(new_words) > 0
        is_free_drill = not has_due and not has_new

        if is_free_drill:

            words_to_study = all_words[:20]
            random.shuffle(words_to_study)
        else:

            due_words = [w for w in all_words if w.id in due_word_ids]
            words_to_study = (due_words + new_words)[:20]

        questions = []
        for word in words_to_study:
            distractors = random.sample([w for w in all_words if w.id != word.id], 3)
            choices = distractors + [word]
            random.shuffle(choices)

            questions.append(
                {
                    "id": word.id,
                    "kanji": word.kanji,
                    "reading": word.reading,
                    "romaji": word.romaji,
                    "choices": [
                        {"word_id": c.id, "meaning": c.meaning} for c in choices
                    ],
                }
            )

        return Response(
            {
                "deck_id": deck.id,
                "deck_title": deck.title,
                "total": len(questions),
                "is_free_drill": is_free_drill,
                "words": questions,
            }
        )


class SubmitAnswerView(APIView):
    @extend_schema(
        request=SubmitAnswerSerializer,
        responses={200: StudyResponseSerializer},
        summary="Submit jawaban dan proses FSRS",
    )
    def post(self, request):
        serializer = SubmitAnswerSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        question_word_id = serializer.validated_data["question_word_id"]
        answered_word_id = serializer.validated_data["answered_word_id"]
        response_time_seconds = serializer.validated_data["response_time_seconds"]

        is_correct = question_word_id == answered_word_id
        rating = get_rating_from_response(is_correct, response_time_seconds)
        now = timezone.now()

        flashcard = get_or_create_flashcard(
            user=request.user,
            word_id=question_word_id,
            now=now,
        )

        is_new = flashcard.last_review is None
        is_due = flashcard.due <= now

        is_future_due = not is_new and not is_due

        if is_future_due:
            return Response(
                {
                    "word_id": question_word_id,
                    "next_due": flashcard.due,
                    "is_free_drill": True,
                },
                status=status.HTTP_200_OK,
            )


        try:
            with transaction.atomic():
                card = apply_review(flashcard, rating)
        except Exception as e:
            return Response(
                {
                    "message": "Terjadi kesalahan saat memproses jawaban.",
                    "errmsg": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {"word_id": question_word_id, "next_due": card.due, "is_free_drill": False}
        )


class HomeStatsView(APIView):
    @extend_schema(
        summary="Statistik homepage user",
        responses={200: HomeStatsSerializer},
    )
    def get(self, request: Request):
        user = request.user
        now = timezone.now()

        flashcards = Flashcard.objects.filter(user=user)
        reviewed = flashcards.filter(last_review__isnull=False)
        reviewed_count = reviewed.count()

        if reviewed_count > 0:
            stable_count = reviewed.filter(state=2).count()
            retention_rate = round((stable_count / reviewed_count) * 100, 1)
        else:
            retention_rate = None

        avg_stability = flashcards.filter(stability__isnull=False).aggregate(
            avg=Avg("stability")
        )["avg"]
        stability_days = round(avg_stability, 1) if avg_stability is not None else None

        total_words = Word.objects.count()
        n5_progress = (
            round((reviewed_count / total_words) * 100, 1) if total_words > 0 else 0.0
        )

        end_of_today = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        today_cards = flashcards.filter(due__lte=end_of_today)
        today_count = today_cards.count()

        next_due_today = today_cards.aggregate(next=Min("due"))["next"]
        if next_due_today is not None:
            delta_seconds = (next_due_today - now).total_seconds()
            next_due_minutes = max(0, math.ceil(delta_seconds / 60))
        else:
            next_due_minutes = None

        start_of_tomorrow = end_of_today + timedelta(seconds=1)
        week_ahead = now + timedelta(days=7)
        upcoming_reviews = (
            flashcards.filter(due__gte=start_of_tomorrow, due__lte=week_ahead)
            .annotate(date=TruncDate("due"))
            .values("date")
            .annotate(count=Count("id"))
            .order_by("date")
        )

        data = {
            "retention_rate": retention_rate,
            "stability_days": stability_days,
            "n5_progress": n5_progress,
            "upcoming_reviews": {
                "today": {
                    "next_due_minutes": next_due_minutes,
                    "count": today_count,
                },
                "upcoming": list(upcoming_reviews),
            },
        }

        serializer = HomeStatsSerializer(data)
        return Response(serializer.data)
