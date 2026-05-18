import random

from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ..decks.models import Deck
from .models import Flashcard
from .serializers import (
    StudyResponseSerializer,
    StudySessionSerializer,
    SubmitAnswerSerializer,
)
from .services import apply_review, get_or_create_flashcard, get_rating_from_response


# Create your views here.
class GenerateQuestionsView(APIView):
    @extend_schema(
        responses={200: StudySessionSerializer},
        summary="Mulai sesi belajar untuk deck tertentu",
    )
    def get(self, request: Request, deck_id):
        try:
            deck = Deck.objects.prefetch_related("words").get(
                Q(id=deck_id)
                & (Q(owner=request.user) | Q(is_default=True) | Q(owner__isnull=True))
            )

        except Deck.DoesNotExist:
            return Response(
                {"message": "Deck tidak ditemukan atau Anda tidak memiliki akses."},
                status=status.HTTP_404_NOT_FOUND,
            )

        all_words = list(deck.words.all())
        if len(all_words) < 4:
            return Response(
                {
                    "message": "Deck harus berisi minimal 4 kata untuk memulai sesi belajar."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        all_word_ids = [w.id for w in all_words]
        due_flashcards = Flashcard.objects.filter(
            user=request.user, word_id__in=all_word_ids, due__lte=timezone.now()
        )

        questions = []
        if not due_flashcards.exists():
            words_to_study = all_words[:20]
        else:
            due_word_ids = set(due_flashcards.values_list("word_id", flat=True))
            words_to_study = [w for w in all_words if w.id in due_word_ids][:20]

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
        if not due_flashcards.exists():
            random.shuffle(questions)
        return Response(
            {
                "deck_id": deck.id,
                "deck_title": deck.title,
                "total": len(questions),
                "is_free_drill": not due_flashcards.exists(),
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

        is_new_card = flashcard.last_review is None
        if not is_new_card and flashcard.due > now:
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
