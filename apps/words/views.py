from django.shortcuts import render
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, viewsets
from rest_framework.pagination import PageNumberPagination

from .models import Word
from .serializers import WordSerializer


# Create your views here.
class WordPagination(PageNumberPagination):
    page_size = 20


@extend_schema_view(
    list=extend_schema(summary="Ambil semua list kata yang tersedia"),
    retrieve=extend_schema(summary="Ambil detail kata (tunggal)"),
)
class WordView(viewsets.ReadOnlyModelViewSet):
    queryset = Word.objects.all().prefetch_related("deck_words").order_by("id")
    serializer_class = WordSerializer
    pagination_class = WordPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ["meaning"]
