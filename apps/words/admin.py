from django.contrib import admin

from .models import Word

# Register your models here.


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ("id", "kanji", "romaji", "reading", "meaning", "pos")
    search_fields = ["romaji", "meaning"]
    list_filter = ["pos"]
    prepopulated_fields = {"meaning": ["meaning"], "romaji": ["romaji"]}
