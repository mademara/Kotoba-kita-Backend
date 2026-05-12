from rest_framework import serializers

from ..words.models import Word
from ..words.serializers import WordSerializer
from .models import Deck


class DeckListSerializer(serializers.ModelSerializer):
    word_count = serializers.IntegerField(read_only=True)
    due_count = serializers.IntegerField(read_only=True)
    is_default = serializers.BooleanField(read_only=True)
    word_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Word.objects.all(),
        source="words",
        write_only=True,
        required=False,
    )

    class Meta:
        model = Deck
        fields = [
            "id",
            "title",
            "description",
            "is_default",
            "created_at",
            "word_count",
            "due_count",
            "word_ids",
        ]

    def validate_word_ids(self, value):
        if len(value) < 10:
            raise serializers.ValidationError("Deck harus berisi minimal 10 kata.")
        ids = [word.id for word in value]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError("Terdapat kata duplikat dalam daftar.")

        return value

    def create(self, validated_data):
        words = validated_data.pop("words", [])
        deck = Deck.objects.create(**validated_data)
        if words:
            deck.words.set(words)
        return deck

    def update(self, instance, validated_data):
        words = validated_data.pop("words", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if words is not None:
            instance.words.set(words)
        return instance


class DeckDetailSerializer(serializers.ModelSerializer):
    words = WordSerializer(many=True, read_only=True)
    word_count = serializers.IntegerField(read_only=True)
    due_count = serializers.IntegerField(read_only=True)
    is_default = serializers.BooleanField(read_only=True)

    class Meta:
        model = Deck
        fields = [
            "id",
            "title",
            "description",
            "is_default",
            "created_at",
            "word_count",
            "due_count",
            "words",
        ]
