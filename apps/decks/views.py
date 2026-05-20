from django.db.models import Count, IntegerField, Q, Value
from django.shortcuts import render
from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied

from ..flashcards.models import Flashcard
from .models import Deck
from .serializers import DeckDetailSerializer, DeckListSerializer


@extend_schema_view(
    list=extend_schema(summary="Ambil semua deck milik user dan deck default"),
    retrieve=extend_schema(summary="Ambil detail deck beserta daftar kata"),
    create=extend_schema(summary="Buat deck custom baru"),
    partial_update=extend_schema(summary="Edit judul, deskripsi, atau kata dalam deck"),
    destroy=extend_schema(summary="Hapus deck custom"),
)
# Create your views here.
class DecksViewSet(viewsets.ModelViewSet):
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_queryset(self):
        user = self.request.user
        now = timezone.now()

        queryset = (
            Deck.objects.filter(Q(is_default=True) | Q(owner=user))
            .annotate(word_count=Count("words"))
            .prefetch_related("words")
        )

        due_word_ids = set(
            Flashcard.objects.filter(
                user=user,
                due__lte=now,
            ).values_list("word_id", flat=True)
        )

        for deck in queryset:
            deck_word_ids = {w.id for w in deck.words.all()}
            deck.due_count = len(deck_word_ids & due_word_ids)

        return queryset

    def get_serializer_class(self):

        if self.action == "retrieve":
            return DeckDetailSerializer
        return DeckListSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user, is_default=False)

    def perform_update(self, serializer):
        if self.get_object().is_default:
            raise PermissionDenied("Deck default tidak boleh diubah.")
        if self.get_object().owner != self.request.user:
            raise PermissionDenied("Anda tidak memiliki izin mengubah deck ini.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.is_default:
            raise PermissionDenied("Deck default tidak boleh dihapus.")

        if instance.owner != self.request.user:
            raise PermissionDenied("Anda tidak memiliki izin menghapus deck ini.")

        super().perform_destroy(instance)
