from fsrs import Card, Rating, Scheduler, State

from .models import Flashcard


def get_or_create_flashcard(user, word_id, now):
    flashcard, _ = Flashcard.objects.get_or_create(
        user=user,
        word_id=word_id,
        defaults={"due": now},
    )
    return flashcard


def get_rating_from_response(is_correct: bool, response_time_seconds: int) -> Rating:
    if not is_correct:
        return Rating.Again
    if response_time_seconds <= 5:
        return Rating.Easy
    elif response_time_seconds <= 10:
        return Rating.Good
    else:
        return Rating.Hard


def build_card_from_flashcard(flashcard: Flashcard):
    card = Card()
    card.step = flashcard.step
    card.stability = flashcard.stability
    card.difficulty = flashcard.difficulty
    card.state = State(flashcard.state)
    if flashcard.last_review:
        card.last_review = flashcard.last_review
    return card


def apply_review(flashcard: Flashcard, rating: Rating):
    card = build_card_from_flashcard(flashcard)
    scheduler = Scheduler()
    card, _ = scheduler.review_card(card, rating)

    flashcard.due = card.due
    flashcard.step = card.step
    flashcard.stability = card.stability
    flashcard.difficulty = card.difficulty
    flashcard.state = card.state
    flashcard.last_review = card.last_review
    flashcard.save()

    return card
