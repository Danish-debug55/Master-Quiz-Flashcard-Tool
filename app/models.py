from dataclasses import dataclass, asdict, field
from typing import Dict, Any


@dataclass
class QuizQuestion:
    question_id: str
    quiz_id: str
    topic: str
    subtopic: str
    question_text: str
    options: Dict[str, str]
    correct_option: str
    correct_answer_text: str = ""
    explanation: str = ""
    why_other_options_wrong: Dict[str, str] = field(default_factory=dict)
    example: str = ""
    source: str = ""
    trainee_answer: str = ""
    self_assessed: str = ""
    coach_mark: Any = ""
    compulsory: str = ""
    question_format: str = "general"
    source_type: str = "sample"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Flashcard:
    card_id: str
    source_question_id: str
    topic: str
    subtopic: str
    card_type: str
    front: str
    back: str
    explanation: str = ""
    why_other_options_wrong: Dict[str, str] = field(default_factory=dict)
    example: str = ""
    importance: int = 1
    source: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class CardProgress:
    card_id: str
    times_seen: int = 0
    streak: int = 0
    ease: float = 2.3
    interval_minutes: int = 0
    due_at: str = ""
    last_rating: str = ""
    last_reviewed_at: str = ""
    lapses: int = 0

    def to_dict(self) -> dict:
        return asdict(self)
