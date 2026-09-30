"""Public content API for original Cambridge B1 Preliminary practice.

Copies are returned so page code cannot accidentally change the shared bank.
This is independent training material, not an official Cambridge exam paper.
"""

from copy import deepcopy

from data.practice import GRAMMAR, VOCABULARY, WRITING
from data.reading import READING


def load_reading():
    """Return twelve sets, two for each of the six Reading parts."""
    return deepcopy(READING)


def load_grammar():
    """Return grammar questions with answers and teaching explanations."""
    return deepcopy(GRAMMAR)


def load_vocabulary():
    """Return English vocabulary cards with German meanings and examples."""
    return deepcopy(VOCABULARY)


def load_writing():
    """Return original Email, Article and Story tasks."""
    return deepcopy(WRITING)


_QUESTIONS = {
    question["id"]: question
    for question in [*GRAMMAR, *(q for reading_set in READING for q in reading_set["questions"])]
}


def get_question(question_id):
    """Find a Reading/Grammar question, or return None for an unknown ID."""
    question = _QUESTIONS.get(question_id)
    return deepcopy(question) if question is not None else None
