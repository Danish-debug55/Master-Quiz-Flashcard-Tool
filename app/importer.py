import re
from html import unescape
from typing import Any


def strip_html(html_text: Any) -> str:
    """
    Remove HTML tags and tidy up whitespace.
    """
    if html_text is None:
        return ""

    text = str(html_text)
    text = unescape(text)

    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</p>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("\xa0", " ")
    text = re.sub(r"\n+", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)

    return text.strip()


def extract_answer_and_explanation(question_answer_html: Any) -> tuple[str, str, str]:
    """
    Extract:
    - correct option letter
    - correct answer text
    - explanation text

    from the Airtable 'Question Answer' field.
    """
    clean_text = strip_html(question_answer_html)

    correct_option = ""
    correct_answer_text = ""
    explanation_text = ""

    lines = []
    for line in clean_text.split("\n"):
        stripped_line = line.strip()
        if stripped_line:
            lines.append(stripped_line)

    answer_index = None
    explanation_index = None

    for index, line in enumerate(lines):
        lower_line = line.lower()
        if lower_line.startswith("answer"):
            answer_index = index
        elif lower_line.startswith("explanation"):
            explanation_index = index

    if answer_index is not None:
        start_index = answer_index + 1

        if explanation_index is not None:
            answer_lines = lines[start_index:explanation_index]
        else:
            answer_lines = lines[start_index:]

        correct_answer_text = " ".join(answer_lines).strip()

    if explanation_index is not None:
        explanation_lines = lines[explanation_index + 1:]
        explanation_text = " ".join(explanation_lines).strip()

    option_match = re.match(r"^([A-D])\)\s*(.*)$", correct_answer_text)
    if option_match:
        correct_option = option_match.group(1)
        correct_answer_text = option_match.group(2).strip()

    return correct_option, correct_answer_text, explanation_text


def build_options_from_answer_text(correct_option: str, correct_answer_text: str) -> dict[str, str]:
    """
    Since your Airtable export does not currently include all four options separately,
    we store only the known correct option text.

    Later, if your team provides full MCQ options, this can be upgraded.
    """
    options = {
        "A": "",
        "B": "",
        "C": "",
        "D": ""
    }

    if correct_option in options:
        options[correct_option] = correct_answer_text

    return options


def derive_topic(fields: dict[str, Any]) -> str:
    """
    Use Topic if it is meaningful. Otherwise fall back to Week.
    """
    topic = str(fields.get("Topic", "")).strip()
    week = str(fields.get("Week", "")).strip()

    if topic and topic != "-":
        return topic

    if week:
        return week

    return "General"


def derive_subtopic(fields: dict[str, Any]) -> str:
    """
    Try to derive a useful subtopic from Question Id or leave blank.
    """
    question_id = str(fields.get("Question Id", "")).strip()

    if not question_id:
        return ""

    parts = question_id.split("-Q")
    if len(parts) >= 1:
        return parts[0]

    return ""


def convert_airtable_record_to_quiz_question(record: dict[str, Any]) -> dict[str, Any]:
    """
    Convert one real Airtable mastery quiz record into the quiz-question format
    used by the flashcard app.
    """
    fields = record.get("fields", {})

    question_id = str(fields.get("Question Id", record.get("id", ""))).strip()
    quiz_id = str(fields.get("Week", "")).strip()

    question_text = strip_html(fields.get("Question", ""))
    topic = derive_topic(fields)
    subtopic = derive_subtopic(fields)

    correct_option, correct_answer_text, explanation_text = extract_answer_and_explanation(
        fields.get("Question Answer", "")
    )

    options = build_options_from_answer_text(
        correct_option, correct_answer_text)

    trainee_answer = strip_html(fields.get("Trainee Answer", ""))
    self_assessed = str(fields.get("Self-Assessed", "")).strip()
    coach_mark = fields.get("Coach Mark", "")
    compulsory = str(fields.get("Compulsory", "")).strip()

    converted_record = {
        "question_id": question_id,
        "quiz_id": quiz_id,
        "topic": topic,
        "subtopic": subtopic,
        "question_text": question_text,
        "options": options,
        "correct_option": correct_option,
        "correct_answer_text": correct_answer_text,
        "explanation": explanation_text,
        "why_other_options_wrong": {
            "A": "",
            "B": "",
            "C": "",
            "D": ""
        },
        "example": "",
        "trainee_answer": trainee_answer,
        "self_assessed": self_assessed,
        "coach_mark": coach_mark,
        "compulsory": compulsory,
        "source_type": "airtable",
        "question_format": "mcq",
    }

    return converted_record


def is_php_record(converted: dict[str, Any]) -> bool:
    """
    Return True if this record belongs to a PHP quiz.
    Checks topic, quiz_id, and question_id for the word 'php' (case-insensitive).
    """
    fields_to_check = [
        converted.get("topic", ""),
        converted.get("quiz_id", ""),
        converted.get("question_id", ""),
        converted.get("subtopic", ""),
    ]

    for field in fields_to_check:
        if "php" in str(field).lower():
            return True

    return False


def convert_airtable_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Convert all Airtable records into quiz questions.
    Skips records with missing data and any records belonging to PHP quizzes.
    """
    converted_questions = []
    php_skipped = 0

    for record in records:
        converted = convert_airtable_record_to_quiz_question(record)

        if not converted["question_text"]:
            print("Skipping record with empty question text:", record.get("id"))
            continue

        if not converted["correct_answer_text"]:
            print("Skipping record with empty correct answer text:", record.get("id"))
            continue

        if is_php_record(converted):
            php_skipped += 1
            continue

        converted_questions.append(converted)

    print(f"Skipped {php_skipped} PHP quiz records.")
    print("Converted questions:", len(converted_questions))
    return converted_questions
