from django.contrib import admin

from .models import Deck

# Register your models here.


@admin.register(Deck)
class DeckAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "is_default", "created_at")
    search_fields = ["title"]
    list_filter = ["owner"]
    prepopulated_fields = {"title": ["title"]}
