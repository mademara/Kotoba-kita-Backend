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


class TodayReviewSerializer(serializers.Serializer):
    next_due_minutes = serializers.IntegerField(
        allow_null=True,
        help_text="Menit hingga kartu berikutnya due hari ini. Null jika tidak ada kartu due hari ini.",
    )
    count = serializers.IntegerField(help_text="Jumlah kartu yang due hari ini.")


class UpcomingReviewSerializer(serializers.Serializer):
    date = serializers.DateField(help_text="Tanggal sesi review.")
    count = serializers.IntegerField(
        help_text="Jumlah kartu yang due pada tanggal tersebut."
    )


class UpcomingReviewsSerializer(serializers.Serializer):
    today = TodayReviewSerializer(help_text="Ringkasan kartu yang due hari ini.")
    upcoming = UpcomingReviewSerializer(
        many=True,
        help_text="Kartu yang due dalam 7 hari ke depan, dikelompokkan per tanggal.",
    )


class HomeStatsSerializer(serializers.Serializer):
    retention_rate = serializers.FloatField(
        allow_null=True,
        help_text="Persentase kartu yang sudah masuk state Review. Null jika belum ada kartu yang direview.",
    )
    stability_days = serializers.FloatField(
        allow_null=True,
        help_text="Rata-rata stability dalam hari. Null jika belum ada kartu dengan nilai stability.",
    )
    n5_progress = serializers.FloatField(
        help_text="Persentase kata N5 yang sudah pernah direview dari total kata di database.",
    )
    upcoming_reviews = UpcomingReviewsSerializer(
        help_text="Jadwal review mendatang.",
    )
