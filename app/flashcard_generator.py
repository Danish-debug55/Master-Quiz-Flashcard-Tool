from app.models import QuizQuestion, Flashcard


def get_correct_answer_text(question: QuizQuestion) -> str:
    if question.correct_answer_text:
        return question.correct_answer_text.strip()

    if question.correct_option in question.options:
        return question.options[question.correct_option].strip()

    return ""


def format_front_text(question: QuizQuestion) -> str:
    """
    Keep the original question intact.
    We do not inject extra awkward prompts into imported Airtable questions.
    """
    return question.question_text.strip()


def create_recall_card(question: QuizQuestion) -> Flashcard:
    correct_answer_text = get_correct_answer_text(question)

    return Flashcard(
        card_id=f"{question.question_id}_recall",
        source_question_id=question.question_id,
        topic=question.topic,
        subtopic=question.subtopic,
        card_type="recall",
        front=format_front_text(question),
        back=correct_answer_text,
        explanation=question.explanation,
        why_other_options_wrong=question.why_other_options_wrong,
        example=question.example,
        importance=2 if question.compulsory == "Yes" else 1,
        source=question.source,
    )


def create_reverse_card(question: QuizQuestion) -> Flashcard:
    correct_answer_text = get_correct_answer_text(question)

    return Flashcard(
        card_id=f"{question.question_id}_reverse",
        source_question_id=question.question_id,
        topic=question.topic,
        subtopic=question.subtopic,
        card_type="reverse",
        front=f"Which concept or term matches this description?\n\n{correct_answer_text}",
        back=question.question_text.strip(),
        explanation=question.explanation,
        why_other_options_wrong=question.why_other_options_wrong,
        example=question.example,
        importance=1,
        source=question.source,
    )


def create_misconception_card(question: QuizQuestion) -> Flashcard:
    correct_answer_text = get_correct_answer_text(question)

    return Flashcard(
        card_id=f"{question.question_id}_misconception",
        source_question_id=question.question_id,
        topic=question.topic,
        subtopic=question.subtopic,
        card_type="misconception",
        front=f"State the key idea being tested.\n\n{question.question_text.strip()}",
        back=correct_answer_text,
        explanation=question.explanation,
        why_other_options_wrong=question.why_other_options_wrong,
        example=question.example,
        importance=1,
        source=question.source,
    )


def should_create_extra_cards(question: QuizQuestion) -> bool:
    """
    For imported Airtable quiz content, extra reverse/misconception cards often
    become unnatural and confusing, especially for MCQ-style questions.
    So we keep Airtable imports as recall cards only.
    """
    if question.source_type == "airtable":
        return False

    if question.question_format in ["mcq", "multi_select", "true_false"]:
        return False

    answer_text = get_correct_answer_text(question)
    if not answer_text:
        return False

    if len(answer_text) > 140:
        return False

    return True


def create_flashcards_from_question(question: QuizQuestion) -> list[Flashcard]:
    cards = [create_recall_card(question)]

    if should_create_extra_cards(question):
        cards.append(create_reverse_card(question))
        cards.append(create_misconception_card(question))

    return cards


def build_flashcards(questions: list[QuizQuestion]) -> list[Flashcard]:
    flashcards = []

    for question in questions:
        cards = create_flashcards_from_question(question)
        flashcards.extend(cards)

    return flashcards
