from rest_framework.routers import DefaultRouter

from .views import DecksViewSet

deck_router = DefaultRouter()
deck_router.register(r"decks", DecksViewSet, basename="decks")
