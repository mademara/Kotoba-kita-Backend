from django.db import models


# Create your models here.
class Word(models.Model):
    id = models.IntegerField(primary_key=True)
    kanji = models.CharField(max_length=200, null=True)
    reading = models.CharField(max_length=200)
    romaji = models.CharField(max_length=200)
    meaning = models.CharField(max_length=200)
    pos = models.CharField(max_length=50)
