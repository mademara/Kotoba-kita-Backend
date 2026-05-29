from django.db import models
from django.db.models import Q
from rest_framework import serializers

from .models import Word


class WordSerializer(serializers.ModelSerializer):
    decks = serializers.SerializerMethodField()

    def get_decks(self, obj):
        request = self.context.get("request")

        queryset = obj.deck_words.all()

        if request and request.user and request.user.is_authenticated:
            queryset = queryset.filter(Q(owner=request.user) | Q(is_default=True))
        else:
            queryset = queryset.filter(is_default=True)

        return list(
            queryset.values(id=models.F("id"), title=models.F("title")).distinct()
        )

    class Meta:
        model = Word
        fields = ["id", "kanji", "reading", "romaji", "meaning", "pos", "decks"]
