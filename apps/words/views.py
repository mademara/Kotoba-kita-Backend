from django.shortcuts import render
from rest_framework import filters, viewsets
from rest_framework.pagination import PageNumberPagination

from .models import Word
from .serializers import WordSerializer


# Create your views here.
class WordPagination(PageNumberPagination):
    page_size = 20


class WordView(viewsets.ReadOnlyModelViewSet):
    queryset = Word.objects.all().order_by("id")
    serializer_class = WordSerializer
    pagination_class = WordPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ["meaning"]
