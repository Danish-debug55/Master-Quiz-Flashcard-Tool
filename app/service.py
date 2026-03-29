

import json
import re
from pathlib import Path

from app.models import Flashcard, CardProgress
from app.scheduler import create_default_progress, update_card_schedule, is_due


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
FLASHCARD_FILE = DATA_DIR / "flashcards.json"
PROGRESS_DIR = DATA_DIR / "progress"


# ── Validation ────────────────────────────────────────────────

_USER_ID_PATTERN = re.compile(r"^[a-f0-9\-]{36}$")


def validate_user_id(user_id: str) -> str:
    """
    Ensure the user_id looks like a UUID to prevent path-traversal attacks.
    """
    user_id = user_id.strip().lower()

    if not _USER_ID_PATTERN.match(user_id):
        raise ValueError("Invalid user id")

    return user_id


# ── Static flashcard data (read-only) ────────────────────────

def load_flashcards() -> list[Flashcard]:
    if not FLASHCARD_FILE.exists():
        return []

    if FLASHCARD_FILE.stat().st_size == 0:
        return []

    with open(FLASHCARD_FILE, "r", encoding="utf-8") as file:
        raw = json.load(file)

    return [Flashcard(**row) for row in raw]


def get_topics_from_flashcards(flashcards: list[Flashcard]) -> list[str]:
    topics = []

    for card in flashcards:
        if card.topic not in topics:
            topics.append(card.topic)

    topics.sort()
    return topics


# ── Per-user progress ────────────────────────────────────────

def _progress_file(user_id: str) -> Path:
    user_id = validate_user_id(user_id)
    return PROGRESS_DIR / f"{user_id}.json"


def save_progress(user_id: str, progress_map: dict[str, CardProgress]) -> None:
    PROGRESS_DIR.mkdir(parents=True, exist_ok=True)
    payload = {}

    for card_id, progress in progress_map.items():
        payload[card_id] = progress.to_dict()

    with open(_progress_file(user_id), "w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2)


def load_progress(user_id: str) -> dict[str, CardProgress]:
    path = _progress_file(user_id)

    if not path.exists() or path.stat().st_size == 0:
        return {}

    with open(path, "r", encoding="utf-8") as file:
        raw = json.load(file)

    progress_map = {}
    for card_id, value in raw.items():
        progress_map[card_id] = CardProgress(**value)

    return progress_map


# ── Card operations ──────────────────────────────────────────

def get_next_card(user_id: str, topic: str = "All") -> dict:
    flashcards = load_flashcards()
    progress_map = load_progress(user_id)

    filtered_cards = []
    for card in flashcards:
        if topic == "All" or card.topic == topic:
            filtered_cards.append(card)

    due_cards = []

    for card in filtered_cards:
        if card.card_id not in progress_map:
            progress_map[card.card_id] = create_default_progress(card.card_id)

        progress = progress_map[card.card_id]

        if is_due(progress):
            due_cards.append((card, progress))

    due_cards.sort(
        key=lambda item: (
            item[1].due_at,
            -item[0].importance,
            item[1].times_seen,
        )
    )

    save_progress(user_id, progress_map)

    if not due_cards:
        return {"message": "No cards due right now."}

    card, progress = due_cards[0]

    return {
        "card_id": card.card_id,
        "topic": card.topic,
        "subtopic": card.subtopic,
        "card_type": card.card_type,
        "front": card.front,
        "back": card.back,
        "explanation": card.explanation,
        "why_other_options_wrong": card.why_other_options_wrong,
        "example": card.example,
        "progress": progress.to_dict(),
    }


def review_card(user_id: str, card_id: str, rating: str) -> dict:
    progress_map = load_progress(user_id)

    if card_id not in progress_map:
        progress_map[card_id] = create_default_progress(card_id)

    progress = progress_map[card_id]
    update_card_schedule(progress, rating)
    progress_map[card_id] = progress
    save_progress(user_id, progress_map)

    return progress.to_dict()


def get_dashboard(user_id: str) -> dict:
    flashcards = load_flashcards()
    progress_map = load_progress(user_id)

    total_cards = len(flashcards)
    due_cards = 0
    reviewed_cards = 0
    new_cards = 0

    topic_stats = {}
    hard_cards = []

    for card in flashcards:
        if card.card_id not in progress_map:
            progress_map[card.card_id] = create_default_progress(card.card_id)

        progress = progress_map[card.card_id]

        if progress.times_seen == 0:
            new_cards += 1
        else:
            reviewed_cards += 1

        if is_due(progress):
            due_cards += 1

        if card.topic not in topic_stats:
            topic_stats[card.topic] = {
                "topic": card.topic,
                "total": 0,
                "due": 0,
                "reviewed": 0,
                "new": 0,
                "hard": 0,
            }

        topic_stats[card.topic]["total"] += 1

        if progress.times_seen == 0:
            topic_stats[card.topic]["new"] += 1
        else:
            topic_stats[card.topic]["reviewed"] += 1

        if is_due(progress):
            topic_stats[card.topic]["due"] += 1

        if progress.last_rating in ["again", "hard"]:
            topic_stats[card.topic]["hard"] += 1
            hard_cards.append({
                "card_id": card.card_id,
                "topic": card.topic,
                "front": card.front,
                "last_rating": progress.last_rating,
                "times_seen": progress.times_seen,
            })

    save_progress(user_id, progress_map)

    weakest_topics = list(topic_stats.values())
    weakest_topics.sort(key=lambda row: (
        row["hard"], row["due"]), reverse=True)

    hard_cards.sort(
        key=lambda row: (row["last_rating"] == "again", row["times_seen"]),
        reverse=True,
    )

    return {
        "totals": {
            "total_cards": total_cards,
            "due_cards": due_cards,
            "reviewed_cards": reviewed_cards,
            "new_cards": new_cards,
        },
        "topics": list(topic_stats.values()),
        "weakest_topics": weakest_topics[:5],
        "hard_cards": hard_cards[:10],
    }


def search_cards(query: str = "", topic: str = "All") -> list[dict]:
    flashcards = load_flashcards()
    results = []
    query_lower = query.lower().strip()

    for card in flashcards:
        if topic != "All" and card.topic != topic:
            continue

        haystack = f"{card.front} {card.back} {card.explanation} {card.example}".lower()

        if query_lower and query_lower not in haystack:
            continue

        results.append({
            "card_id": card.card_id,
            "topic": card.topic,
            "subtopic": card.subtopic,
            "card_type": card.card_type,
            "front": card.front,
            "back": card.back,
        })

    return results[:100]
