from rest_framework import serializers

from ..words.models import Word


class SubmitAnswerSerializer(serializers.Serializer):
    question_word_id = serializers.IntegerField()
    answered_word_id = serializers.IntegerField()
    response_time_seconds = serializers.IntegerField(min_value=0, max_value=20)

    def validate(self, data):
        word_ids = {data["question_word_id"], data["answered_word_id"]}
        existing = Word.objects.filter(id__in=word_ids).count()
        if existing != len(word_ids):
            raise serializers.ValidationError("Salah satu word ID tidak valid.")
        return data


class StudyChoicesSerializer(serializers.Serializer):
    word_id = serializers.IntegerField()
    meaning = serializers.CharField(max_length=200)


class WordlistStudySessionsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    kanji = serializers.CharField(max_length=200, allow_null=True)
    reading = serializers.CharField(max_length=200)
    romaji = serializers.CharField(max_length=200)
    choices = StudyChoicesSerializer(many=True)


class StudySessionSerializer(serializers.Serializer):
    deck_id = serializers.IntegerField()
    deck_title = serializers.CharField()
    total = serializers.IntegerField()
    words = WordlistStudySessionsSerializer(many=True)


class StudyResponseSerializer(serializers.Serializer):
    word_id = serializers.IntegerField()
    next_due = serializers.DateTimeField()
    is_free_drill = serializers.BooleanField()
