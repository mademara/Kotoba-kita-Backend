from django.contrib import admin

from .models import User


# Register your models here.
@admin.register(User)
class WordAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "username",
        "email",
        "date_joined",
        "last_login",
        "is_superuser",
        "is_staff",
        "is_active",
    )
    search_fields = ["username", "email"]
    list_filter = [
        "is_staff",
        "is_superuser",
    ]
    prepopulated_fields = {"username": ["username"], "email": ["email"]}
