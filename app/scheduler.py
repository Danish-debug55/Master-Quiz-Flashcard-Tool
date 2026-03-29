from datetime import datetime, timedelta, timezone
from app.models import CardProgress


VALID_RATINGS = ["again", "hard", "good", "easy"]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def datetime_to_string(value: datetime) -> str:
    return value.isoformat()


def string_to_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value)


def create_default_progress(card_id: str) -> CardProgress:
    return CardProgress(card_id=card_id, due_at=datetime_to_string(utc_now()))


def get_initial_interval_minutes(rating: str) -> int:
    if rating == "again":
        return 1
    if rating == "hard":
        return 15
    if rating == "good":
        return 180
    return 1440


def update_card_schedule(progress: CardProgress, rating: str) -> CardProgress:
    if rating not in VALID_RATINGS:
        raise ValueError("Invalid rating")

    now = utc_now()
    progress.times_seen += 1
    progress.last_rating = rating
    progress.last_reviewed_at = datetime_to_string(now)

    if progress.times_seen <= 2:
        next_interval = get_initial_interval_minutes(rating)
        if rating in ["good", "easy"]:
            progress.streak += 1
        else:
            progress.streak = 0
            if rating == "again":
                progress.lapses += 1
    else:
        current_interval = progress.interval_minutes
        if current_interval <= 0:
            current_interval = 10

        if rating == "again":
            next_interval = 1
            progress.streak = 0
            progress.ease -= 0.2
            progress.lapses += 1
        elif rating == "hard":
            next_interval = int(current_interval * 1.2)
            if next_interval < 10:
                next_interval = 10
            progress.streak = 0
            progress.ease -= 0.05
        elif rating == "good":
            next_interval = int(current_interval * progress.ease)
            if next_interval < 180:
                next_interval = 180
            progress.streak += 1
            progress.ease += 0.03
        else:
            next_interval = int(current_interval * progress.ease * 1.4)
            if next_interval < 1440:
                next_interval = 1440
            progress.streak += 1
            progress.ease += 0.08

    if progress.ease < 1.3:
        progress.ease = 1.3
    if progress.ease > 3.2:
        progress.ease = 3.2

    progress.interval_minutes = next_interval
    progress.due_at = datetime_to_string(now + timedelta(minutes=next_interval))
    return progress


def is_due(progress: CardProgress) -> bool:
    return string_to_datetime(progress.due_at) <= utc_now()
