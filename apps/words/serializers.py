from rest_framework import serializers

from .models import Word


class WordSerializer(serializers.ModelSerializer):
    decks = serializers.SerializerMethodField()

    def get_decks(self, obj):
        return list(obj.deck_words.values("id", "title"))

    class Meta:
        model = Word
        fields = ["id", "kanji", "reading", "romaji", "meaning", "pos", "decks"]
