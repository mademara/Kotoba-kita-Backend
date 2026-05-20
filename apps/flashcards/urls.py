from django.urls import path

from .views import GenerateQuestionsView, HomeStatsView, SubmitAnswerView

urlpatterns = [
    path(
        "study/<int:deck_id>/start/",
        GenerateQuestionsView.as_view(),
        name="study-start",
    ),
    path("study/submit/", SubmitAnswerView.as_view(), name="study-submit"),
    path("home/stats/", HomeStatsView.as_view(), name="home-stats"),
]
