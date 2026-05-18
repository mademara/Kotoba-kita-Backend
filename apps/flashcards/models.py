from django.conf import settings
from django.db import models


# Create your models here.
class Flashcard(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    word = models.ForeignKey("words.Word", on_delete=models.CASCADE)
    due = models.DateTimeField()
    step = models.IntegerField(default=0, null=True, blank=True)
    stability = models.FloatField(null=True)
    difficulty = models.FloatField(null=True)
    state = models.IntegerField(default=1)
    last_review = models.DateTimeField(null=True)

    class Meta:
        unique_together = (("user", "word"),)
