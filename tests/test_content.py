"""Validate that practice content is answerable and all links stay intact."""

import re
from collections import Counter

import pytest

from data.content import (
    get_question,
    load_grammar,
    load_reading,
    load_vocabulary,
    load_writing,
)


READING_SETS = load_reading()
ALL_QUESTIONS = [
    *(q for reading_set in READING_SETS for q in reading_set["questions"]),
    *load_grammar(),
]


def test_every_reading_part_has_two_complete_sets():
    assert Counter(s["part"] for s in READING_SETS) == Counter({part: 2 for part in range(1, 7)})
    for reading_set in READING_SETS:
        expected = 6 if reading_set["part"] in (5, 6) else 5
        assert len(reading_set["questions"]) == expected
        assert reading_set["title"] and reading_set["instructions"] and reading_set["passage"]
        assert all(q["skill"] == "Reading" for q in reading_set["questions"])
        assert all(q["topic"] == f"Part {reading_set['part']}" for q in reading_set["questions"])


def test_all_content_ids_are_unique_across_banks():
    records = [*READING_SETS, *ALL_QUESTIONS, *load_vocabulary(), *load_writing()]
    identifiers = [record["id"] for record in records]
    assert len(identifiers) == len(set(identifiers))


@pytest.mark.parametrize("question", ALL_QUESTIONS, ids=lambda q: q["id"])
def test_answers_and_retrieval_are_consistent(question):
    assert question["prompt"].strip()
    assert question["topic"].strip()
    assert question["explanation"].strip()
    assert get_question(question["id"]) == question
    options = question["options"]
    assert len(options) == len(set(options)), "Duplicate options make a question ambiguous"
    if options:
        assert question["answer"] in options
        assert options.count(question["answer"]) == 1
    else:
        assert re.fullmatch(r"[A-Za-z]+", question["answer"]), "An open cloze needs exactly one word"
        accepted = question.get("accepted_answers", [question["answer"]])
        assert question["answer"] in accepted
        assert all(re.fullmatch(r"[A-Za-z]+", answer) for answer in accepted)


@pytest.mark.parametrize("reading_set", READING_SETS, ids=lambda s: s["id"])
def test_reading_formats_and_references(reading_set):
    part = reading_set["part"]
    passage = reading_set["passage"]
    questions = reading_set["questions"]
    if part == 1:
        assert re.findall(r"(?m)^([1-5])\. ", passage) == list("12345")
        assert all(len(q["options"]) == 3 for q in questions)
        for number, question in enumerate(questions, start=1):
            assert str(number) in question["prompt"]
    elif part in (2, 4):
        # All eight labelled alternatives exist in the passage, and every
        # chosen answer refers to one of them. Matching uses five unique texts.
        labels = re.findall(r"(?m)^([A-H])\. ", passage)
        assert labels == list("ABCDEFGH")
        assert all(q["options"] == list("ABCDEFGH") for q in questions)
        assert len({q["answer"] for q in questions}) == 5
        assert set(q["answer"] for q in questions) <= set(labels)
        assert len(set(labels) - {q["answer"] for q in questions}) == 3
    elif part == 3:
        assert len(passage.split()) >= 250, "Part 3 needs a sustained reading text"
        assert all(len(q["options"]) == 4 for q in questions)
    elif part == 5:
        assert all(len(q["options"]) == 4 for q in questions)
    elif part == 6:
        assert all(q["options"] == [] for q in questions)

    if part in (4, 5, 6):
        assert re.findall(r"\[(\d+)\]", passage) == [str(n) for n in range(1, len(questions) + 1)]
        for number, question in enumerate(questions, start=1):
            assert f"[{number}]" in question["prompt"]


def test_part_six_accepts_valid_alternative_words():
    # Relative pronouns and negative comparisons have multiple valid forms;
    # these should not be incorrectly marked wrong by practice pages.
    relative = get_question("reading-p6-book-club-q3")
    assert {"which", "that"} <= set(relative["accepted_answers"])
    comparison = get_question("reading-p6-hostel-q6")
    assert {"as", "so"} <= set(comparison["accepted_answers"])
    hostel = next(s for s in READING_SETS if s["id"] == "reading-p6-hostel")
    assert "not [6] expensive as" in hostel["passage"]


def test_grammar_has_a_varied_question_bank():
    grammar = load_grammar()
    assert len(grammar) >= 36
    topics = Counter(q["topic"] for q in grammar)
    assert len(topics) >= 10
    assert min(topics.values()) >= 3
    assert all(q["skill"] == "Grammar" and len(q["options"]) == 4 for q in grammar)


def test_vocabulary_cards_are_complete_and_varied():
    cards = load_vocabulary()
    assert len(cards) >= 40
    assert len({card["word"].casefold() for card in cards}) == len(cards)
    assert len({card["topic"] for card in cards}) >= 6
    for card in cards:
        assert all(isinstance(card[field], str) and card[field].strip() for field in ("id", "word", "meaning", "example", "topic"))
        assert len(card["example"].split()) >= 5
    # These are German glosses, not accidentally duplicated English headwords.
    assert next(c for c in cards if c["word"] == "luggage")["meaning"] == "Gepäck"


def test_writing_tasks_cover_all_exam_choices_and_feedback_clues():
    tasks = load_writing()
    assert Counter(task["kind"] for task in tasks) == Counter({"Email": 2, "Article": 2, "Story": 2})
    for task in tasks:
        assert "100 words" in task["prompt"]
        assert task["title"].strip()
        assert len(task["points"]) == len(task["keywords"]) == 3
        assert all(isinstance(point, str) and point.strip() for point in task["points"])
        assert all(clues and all(isinstance(clue, str) and clue.strip() for clue in clues) for clues in task["keywords"])
        if task["kind"] == "Story":
            assert task["starter"] in task["prompt"]
            assert task["starter"].strip()
        else:
            assert task["starter"] == ""


def test_loaded_content_cannot_be_mutated_by_a_page():
    reading = load_reading()
    first_id = reading[0]["questions"][0]["id"]
    reading[0]["questions"][0]["options"].clear()
    assert len(get_question(first_id)["options"]) == 3
    question = get_question(first_id)
    question["answer"] = "changed"
    assert get_question(first_id)["answer"] != "changed"
    for loader in (load_grammar, load_vocabulary, load_writing):
        records = loader()
        original_id = records[0]["id"]
        records[0]["id"] = "changed"
        assert loader()[0]["id"] == original_id


def test_unknown_question_is_safe_to_look_up():
    assert get_question("does-not-exist") is None
    assert get_question("vocabulary_001") is None
