from rest_framework.routers import DefaultRouter

from apps.words.views import WordView

router = DefaultRouter()
router.register(r"words", WordView, basename="words")
