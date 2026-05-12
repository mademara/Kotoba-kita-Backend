from django.conf import settings
from django.db import models


# Create your models here.
class Deck(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="deck_owner",
    )
    title = models.CharField(max_length=30)
    description = models.TextField()
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    words = models.ManyToManyField("words.Word", related_name="deck_words")
