from rest_framework import serializers

from .models import Word


class WordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Word
        fields = ["id", "kanji", "reading", "romaji", "meaning", "pos"]
